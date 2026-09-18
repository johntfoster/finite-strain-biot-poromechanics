#!/usr/bin/env python3
"""Verify coupled poroplastic storage and curate compression/drainage evidence.

Run inside the repository MOOSE environment. Raw output stays in .agent-runtime;
--curate publishes data only after every acceptance check succeeds.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import os
import sys
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
from scipy.optimize import brentq

ROOT = Path(__file__).resolve().parents[2]
DECK = ROOT / 'moose_app/test/tests/poroplastic_mandel/compression.i'
SAMPLES = DECK.with_name('storage_samples.i')
EXE = ROOT / 'moose_app/nonlinear_biot_ad-opt'
RUNTIME = ROOT / '.agent-runtime/poroplastic-mandel'
K, KS, PHI0, KF, RHOF, BETA = 1e9, 2.5e9, .9, 8e9, 1000., .4
TIMES = (.04, .1, .2, .3, .5, .7)


def read(path):
    with path.open() as f:
        return [{k: float(v) for k, v in r.items()} for r in csv.DictReader(f)]


def write(path, rows):
    with path.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def mineral(Je, p):
    alpha = 1 - K / (PHI0 * KS)
    def residual(x):
        return x + alpha * p / KS * np.exp(x) - K / (PHI0 * KS) * np.log(Je)
    return np.exp(brentq(residual, -20, .9, xtol=5e-15))


def run(name, nx=10, ny=1, dt=.01, end=.7, samples=False, extra=(), reuse=False):
    RUNTIME.mkdir(parents=True, exist_ok=True)
    base = RUNTIME / name
    cmd = [str(EXE), '-i', str(DECK)]
    ranks = int(os.environ.get('POROPLASTIC_MPI_RANKS', '1')) if nx > 4 else 1
    if ranks > 1:
        cmd = ['mpiexec', '-n', str(ranks), *cmd]
    if samples:
        cmd += [str(SAMPLES)]
    cmd += [f'mesh_nx={nx}', f'mesh_ny={ny}', f'step={dt}',
            f'Executioner/end_time={end}', f'Outputs/file_base={base}',
            '--disable-perf-graph-live', '--color', 'off', *extra]
    signature_files = [DECK, SAMPLES, EXE]
    signature_files += sorted((ROOT/'moose_app/src').rglob('*.C'))
    signature_files += sorted((ROOT/'moose_app/include').rglob('*.h'))
    signature = hashlib.sha256(json.dumps(cmd).encode())
    for path in signature_files:
        signature.update(path.read_bytes())
    manifest = base.with_suffix('.run.json')
    signature = signature.hexdigest()
    cached = (reuse and manifest.exists() and base.with_suffix('.csv').exists()
              and json.loads(manifest.read_text()).get('signature') == signature)
    if not cached:
        manifest.unlink(missing_ok=True)
        if samples:
            for path in RUNTIME.glob(name + '_storage_samples_*.csv'):
                path.unlink()
        print('RUN', name, flush=True)
        with base.with_suffix('.log').open('w') as log:
            subprocess.run(cmd, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, check=True)
    rows = read(base.with_suffix('.csv'))
    if not rows or abs(rows[-1]['time'] - end) > 1e-10:
        raise AssertionError(f'{name} failed to reach {end}')
    steps = np.diff([0.] + [r['time'] for r in rows])
    if max(abs(steps - dt)) > 1e-9:
        raise AssertionError(f'{name} changed the prescribed refinement step')
    if not all(np.isfinite(v) for r in rows for v in r.values()):
        raise AssertionError(f'{name} has nonfinite output')
    manifest.write_text(json.dumps(dict(signature=signature,completed=True))+'\n')
    return rows, [arg.replace(str(ROOT) + '/', '') for arg in cmd]


def storage_check(name, dt):
    files = sorted(RUNTIME.glob(name + '_storage_samples_*.csv'))
    if len(files) < 3:
        raise AssertionError('Missing quadrature-point storage samples')
    old = None
    worst = dict(storage_rate=0., biot=0., elastic_biot=0., mineral=0., plastic_determinant=0.)
    active = 0
    omitted_effect = 0.
    for file in files:
        rows = read(file)
        rows.sort(key=lambda r: (r['elem_id'], r['qp_id']))
        if old is None:
            old = rows
            continue
        for r, prev in zip(rows, old, strict=True):
            J,p,rho,ap = (r['check_'+v] for v in ('J','p','rho','ap'))
            jd = r['check_Jdot']
            pd = (p-prev['check_p'])/dt
            rd = (rho-prev['check_rho'])/dt
            lp = BETA*r['check_gamma']/dt
            def accumulation(tau, plastic=True):
                j = J+tau*jd
                z = mineral(j/(ap*np.exp(tau*lp if plastic else 0)), p+tau*pd)
                return j*(1-PHI0*(rho+tau*rd)*z)*RHOF*np.exp((p+tau*pd)/KF)
            h = 1e-5
            fd = (accumulation(h)-accumulation(-h))/(2*h)
            fd_without = (accumulation(h, False)-accumulation(-h, False))/(2*h)
            worst['storage_rate'] = max(worst['storage_rate'], abs(fd-r['check_storage'])/RHOF)
            omitted_effect = max(omitted_effect, abs(fd-fd_without)/RHOF)
            active += r['check_gamma'] > 1e-10
            worst['plastic_determinant'] = max(worst['plastic_determinant'],
                abs(np.log(ap/prev['check_ap'])-BETA*r['check_gamma']))
            z = mineral(J/ap,p)
            worst['mineral'] = max(worst['mineral'],abs(z*r['check_ratio']-1))
            for a,key in [(ap,'biot'),(1.,'elastic_biot')]:
                b = 1-PHI0*(mineral((J+h)/a,p)-mineral((J-h)/a,p))/(2*h)
                reported = r['check_B'] if key=='biot' else r['check_Bel']
                worst[key] = max(worst[key],abs(b-reported))
        old = rows
    limits = dict(storage_rate=2e-7, biot=5e-8, elastic_biot=5e-8, mineral=1e-10, plastic_determinant=1e-9)
    for k,v in worst.items():
        if v > limits[k]:
            raise AssertionError(f'{k}: {v} > {limits[k]}')
    if active == 0 or omitted_effect < 1e-4:
        raise AssertionError('Storage verification did not exercise a significant plastic contribution')
    return dict(errors=worst, tolerances=limits, active_samples=active,
                omitted_plastic_rate_error_per_water_density=omitted_effect)


def mass_metrics(rows):
    # 0.1 m^2 quarter-domain, per unit out-of-plane reference thickness.
    initial = .1*(1-PHI0)*RHOF
    out = rate = reaction = 0.
    last = 0.
    worst = chain = reaction_worst = 0.
    for r in rows:
        dt = r['time']-last
        out += dt*r['outflow']
        reaction += dt*r['outflow_reaction']
        reaction_worst = max(reaction_worst,abs(r['water_mass']-initial+reaction)/initial)
        rate += dt*r['water_rate']
        worst = max(worst,abs(r['water_mass']-initial+out)/initial)
        chain = max(chain,abs(r['water_mass']-initial-rate)/initial)
        last = r['time']
    return dict(max_relative_mass_defect=worst, max_relative_reaction_mass_defect=reaction_worst, final_relative_mass_defect=(rows[-1]['water_mass']-initial+out)/initial,
                max_relative_chain_rule_defect=chain,
                solid_mass_l2=max(r['solid_material_mass_constraint_l2'] for r in rows),
                mineral_eos_l2=max(r['solid_mineral_eos_constraint_l2'] for r in rows))


def elastic_reference(reuse=False):
    sys.path.insert(0, str(ROOT/'scripts'))
    import reproduce_mandel_publication as publication
    publication.prepare_decks(RUNTIME)
    base=RUNTIME/'elastic_reference'
    cmd=[str(EXE), '-i', str(RUNTIME/'large.i'), 'mesh_nx=4', 'mesh_ny=1',
         'time_sequence='+publication.mandel.time_sequence(.01,.24),
         'Executioner/end_time=.24', f'Outputs/file_base={base}',
         '--disable-perf-graph-live','--color','off']
    signature = hashlib.sha256(json.dumps(cmd).encode())
    for path in [RUNTIME/'large.i', EXE, *sorted((ROOT/'moose_app/src').rglob('*.C')),
                 *sorted((ROOT/'moose_app/include').rglob('*.h'))]:
        signature.update(path.read_bytes())
    manifest = base.with_suffix('.run.json')
    signature = signature.hexdigest()
    cached = (reuse and manifest.exists() and base.with_suffix('.csv').exists()
              and json.loads(manifest.read_text()).get('signature') == signature)
    if not cached:
        manifest.unlink(missing_ok=True)
        with base.with_suffix('.log').open('w') as log:
            subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
    rows=read(base.with_suffix('.csv'))
    if abs(rows[-1]['time']-.24)>1e-10: raise AssertionError('Elastic reference incomplete')
    manifest.write_text(json.dumps(dict(signature=signature,completed=True))+'\n')
    return rows,[arg.replace(str(ROOT)+'/', '') for arg in cmd]


def sensitivity(a,b):
    result={}
    for key,scale in [('pressure_x0',K),('side_displacement',1.),('biot_average',1.),('delta_b_average',1.),('ap_average',1.)]:
        error=max(abs(r[key]-np.interp(r['time'],[s['time'] for s in b],[s[key] for s in b])) for r in a)
        result[key]=error/scale
    return result


def jacobian_check(log):
    text = log.read_text()
    matches = re.findall(r'\|\|J - Jfd\|\|_F/\|\|J\|\|_F\s*=\s*([\deE.+-]+),\s*\|\|J - Jfd\|\|_F\s*=\s*([\deE.+-]+)',text)
    if not matches:
        raise AssertionError('No PETSc Jacobian comparisons found')
    rel = max(float(a) for a,b in matches)
    absolute = max(float(b) for a,b in matches)
    if rel > 1e-7 or absolute > 1e-5:
        raise AssertionError(f'Jacobian differences: {rel}, {absolute}')
    return dict(comparisons=len(matches), relative=rel, absolute=absolute,
                relative_tolerance=1e-7, absolute_tolerance=1e-5)


def extract(name):
    from scipy.io import netcdf_file
    result=[]
    with netcdf_file(RUNTIME/(name+'.e'),mmap=False) as f:
        names=[r.tobytes().decode().strip('\0 ') for r in f.variables['name_elem_var'][:]]
        times=f.variables['time_whole'][:].copy()
        centers=f.variables['connect1'][:,-1].copy()-1
        xs=f.variables['coordx'][:].copy()[centers]
        ys=f.variables['coordy'][:].copy()[centers]
        props={key:f.variables[f'vals_elem_var{names.index(v)+1}eb1'][:].copy() for key,v in
               [('B','biot_coefficient_state'),('B_el','elastic_b'),('delta_B','delta_b'),('a_p','ap'),('plastic_increment','gamma')]}
        for t in TIMES:
            k=int(np.argmin(abs(times-t)))
            if abs(times[k]-t)>1e-9: raise AssertionError(f'Missing snapshot {t}')
            for i,(x,y) in enumerate(zip(xs,ys)):
                result.append(dict(time=t,X=float(x),Y=float(y),**{key:float(v[k,i]) for key,v in props.items()}))
    return result


def field_sensitivity(coarse_name, fine_name):
    coarse = extract(coarse_name)
    fine = extract(fine_name)
    nx = len({r['X'] for r in coarse})
    ny = len({r['Y'] for r in coarse})
    lookup = {(r['time'], int(r['X']*nx), int(r['Y']*ny/.1)):r['delta_B'] for r in coarse}
    result = {}
    for t in TIMES:
        differences = [r['delta_B']-lookup[(t,int(r['X']*nx),int(r['Y']*ny/.1))]
                       for r in fine if r['time']==t]
        result[str(t)] = {'rms':float(np.sqrt(np.mean(np.square(differences)))),
                          'maximum':float(max(abs(v) for v in differences))}
    return result


def spatial_structure(name):
    """Measure departure from the Y-independent solution on reference rectangles."""
    from scipy.io import netcdf_file
    with netcdf_file(RUNTIME/(name+'.e'), mmap=False) as data:
        names = [r.tobytes().decode().strip('\0 ') for r in data.variables['name_elem_var'][:]]
        centers = data.variables['connect1'][:, -1]-1
        x, y = (data.variables['coord'+c][:][centers] for c in ('x', 'y'))
        order = np.lexsort((x, y))
        nx, ny = len(set(x)), len(set(y))
        result = {}
        for key in ('delta_b', 'ap', 'gamma'):
            field = data.variables[f'vals_elem_var{names.index(key)+1}eb1'][:].copy()
            field = field[:, order].reshape(-1, ny, nx)
            departure = field-field.mean(axis=1, keepdims=True)
            result[key] = dict(
                maximum_transverse_rms=float(np.sqrt(np.mean(departure**2, axis=(1, 2))).max()),
                final_x_second_difference_rms=float(np.sqrt(np.mean(np.diff(field[-1], n=2, axis=1)**2))))
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--quick',action='store_true')
    parser.add_argument('--curate',action='store_true')
    parser.add_argument('--reuse',action='store_true',help='Reuse local run CSVs while developing the verification script')
    args=parser.parse_args()
    commands=[]
    rows,cmd=run('storage',nx=4,ny=1,dt=.01,end=.24,samples=True,reuse=args.reuse)
    commands.append(cmd)
    storage=storage_check('storage',.01)
    print('PASS storage',storage,flush=True)
    # Unit-scaled moduli preserve dimensionless response and the absolute PETSc criterion.
    # Extrapolate the Newton initial guess away from the yield switching surface;
    # test every assembled Jacobian through the ramp and hold at unchanged tolerances.
    jrows,cmd=run('jacobian',nx=2,ny=2,dt=.02,end=.7,
        extra=('stiffness_scale_pa=1','cohesion_pa=.02','Outputs/exodus=false','-snes_test_err','1e-9','-snes_test_jacobian'),reuse=args.reuse)
    commands.append(cmd)
    jac=jacobian_check(RUNTIME/'jacobian.log')
    if max(r['gamma_max'] for r in jrows)<1e-8: raise AssertionError('Jacobian run remained elastic')
    print('PASS jacobian',jac,flush=True)
    record=dict(accepted=False,storage=storage,jacobian=jac,commands=commands)
    if args.quick:
        print('PASS poroplastic Mandel storage and coupled Jacobian')
        return
    cases={}
    for name,nx,ny,dt in [('temporal_coarse',20,2,.01),('spatial_coarse',10,1,.005),('fine',20,2,.005),('temporal_fine',20,2,.0025),('spatial_fine',40,4,.0025)]:
        cases[name],cmd=run(name,nx=nx,ny=ny,dt=dt,reuse=args.reuse)
        commands.append(cmd)
        print(name,mass_metrics(cases[name]),flush=True)
    metrics={n:mass_metrics(r) for n,r in cases.items()}
    structure = {name: spatial_structure(name) for name in ('temporal_fine', 'spatial_fine')}
    for name, fields in structure.items():
        for field, limit in [('delta_b', 1.e-8), ('ap', 1.e-7), ('gamma', 1.e-8)]:
            if fields[field]['maximum_transverse_rms'] > limit:
                raise AssertionError(f'{name}: unresolved transverse variation in {field}')
    if (structure['spatial_fine']['delta_b']['final_x_second_difference_rms'] >
            .6*structure['temporal_fine']['delta_b']['final_x_second_difference_rms']):
        raise AssertionError('Coefficient second differences failed spatial refinement')
    if not (metrics['temporal_fine']['max_relative_chain_rule_defect'] < metrics['fine']['max_relative_chain_rule_defect'] < metrics['temporal_coarse']['max_relative_chain_rule_defect']):
        raise AssertionError('Water chain-rule drift failed temporal refinement')
    if not (metrics['temporal_fine']['max_relative_reaction_mass_defect'] < metrics['fine']['max_relative_reaction_mass_defect'] < metrics['temporal_coarse']['max_relative_reaction_mass_defect']):
        raise AssertionError('Integrated boundary reaction and water mass failed temporal refinement')
    if not (metrics['temporal_fine']['solid_mass_l2'] < metrics['fine']['solid_mass_l2'] < metrics['temporal_coarse']['solid_mass_l2']):
        raise AssertionError('Solid mass drift failed temporal refinement')
    if max(m['mineral_eos_l2'] for m in metrics.values())>1e-10:
        raise AssertionError('Mineral EOS residual exceeded tolerance')
    # High cohesion suppresses yielding while retaining the coupled plastic code path.
    elastic,cmd=run('elastic_limit',nx=4,ny=1,dt=.01,end=.24,extra=('cohesion_pa=1e12',),reuse=args.reuse)
    commands.append(cmd)
    if max(abs(r['delta_b_max']) for r in elastic)>1e-10 or max(abs(r['ap_max']-1) for r in elastic)>1e-10:
        raise AssertionError('Elastic limit failed')
    reference,cmd=elastic_reference(args.reuse)
    commands.append(cmd)
    elastic_errors={}
    for key,scale in [('pressure_x0',K),('side_displacement',1.),('biot_average',1.)]:
        elastic_errors[key]=max(abs(a[key]-b[key])/scale for a,b in zip(elastic,reference,strict=True))
        if elastic_errors[key]>1e-7: raise AssertionError(f'Elastic recovery {key}: {elastic_errors[key]}')
    if metrics['spatial_fine']['max_relative_mass_defect'] > .01:
        raise AssertionError('Water mass versus integrated Darcy outflow exceeds 1% of initial water mass')
    toolchain = {'environment':Path(os.environ.get('CONDA_DEFAULT_ENV', 'not-recorded')).name,
        'framework_commit':subprocess.check_output(['git','-C',str(ROOT/'.agent-runtime/moose'),'rev-parse','HEAD'],text=True).strip()}
    try:
        packages = json.loads(subprocess.check_output(['conda','list','--json'],text=True))
        toolchain['packages'] = {p['name']:p['version'] for p in packages
                                 if p['name'] in ('moose-dev','moose-libmesh','moose-tools')}
    except (FileNotFoundError, subprocess.CalledProcessError):
        toolchain['packages'] = 'not recorded; run inside the documented Conda environment'
    record.update(accepted=True,created_utc=datetime.now(timezone.utc).isoformat(),
        mass=metrics,elastic_limit=dict(max_delta_B=max(abs(r['delta_b_max']) for r in elastic), field_errors=elastic_errors),
        sensitivity={
            'time_001_to_0005':sensitivity(cases['temporal_coarse'],cases['fine']),
            'time_0005_to_00025':sensitivity(cases['fine'],cases['temporal_fine']),
            'mesh_10x1_to_20x2':sensitivity(cases['spatial_coarse'],cases['fine']),
            'mesh_20x2_to_40x4':sensitivity(cases['temporal_fine'],cases['spatial_fine'])},
        parameters=dict(K=K,Ks=KS,G=.75e9,Kf=KF,phi_s0=PHI0,M=.6,beta=BETA,cohesion=2e7,hardening_modulus=1e8),
        spatial_structure=structure,
        case_discretization={'temporal_coarse':[20,2,.01], 'spatial_coarse':[10,1,.005],
            'fine':[20,2,.005], 'temporal_fine':[20,2,.0025], 'spatial_fine':[40,4,.0025]},
        field_sensitivity={
            'definition':'difference between piecewise-constant element averages on the common reference domain',
            'mesh_20x2_to_40x4':field_sensitivity('temporal_fine','spatial_fine'),
            'time_001_to_0005':field_sensitivity('temporal_coarse','fine'),
            'time_0005_to_00025':field_sensitivity('fine','temporal_fine')},
        toolchain=toolchain,
        limitations=['No experimental validation or calibration',
            'Single-phase water EOS continued into tension; no cavitation or desaturation',
            'Positive sampled acoustic tensors and resolved profiles apply to the tested synthetic hardening law, not all constitutive states'],
        snapshots=list(TIMES),evidence_class='implementation verification and synthetic discrimination')
    sources=[DECK,SAMPLES,Path(__file__),ROOT/'moose_app/src/materials/ADPoroplasticPoreVolumeMaterial.C',ROOT/'moose_app/src/materials/ADImplicitPoroplasticBiotMaterial.C']
    sources += [ROOT/name for name in [
        'moose_app/include/materials/ADPoroplasticPoreVolumeMaterial.h',
        'moose_app/include/materials/ADImplicitPoroplasticBiotMaterial.h',
        'moose_app/include/postprocessors/NodalDofSum.h',
        'moose_app/src/postprocessors/NodalDofSum.C',
        'moose_app/src/materials/ADBiotPressureStorageMaterial.C',
        'moose_app/src/materials/ADBiotDarcyReferenceFluxMaterial.C',
        'moose_app/src/materials/ADBinarySolidSpatialMassMaterial.C',
        'moose_app/src/materials/ADSolidReferenceKinematics.C',
        'moose_app/src/kernels/ADReferenceMaterialStorageRateTerm.C',
        'moose_app/src/kernels/ADReferenceSolidMomentum.C',
        'moose_app/include/utils/MatchedLogMineralState.h']]
    record['source_sha256']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    (RUNTIME/'verification.json').write_text(json.dumps(record,indent=2)+'\n')
    if args.curate:
        write(ROOT/'validation/poroplastic_mandel_history.csv',cases['spatial_fine'])
        write(ROOT/'validation/poroplastic_mandel_contours.csv',extract('spatial_fine'))
        (ROOT/'validation/poroplastic_mandel_verification.json').write_text(json.dumps(record,indent=2)+'\n')
    print('PASS poroplastic Mandel verification',flush=True)

if __name__=='__main__': main()
