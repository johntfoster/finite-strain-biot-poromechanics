#!/usr/bin/env python3
"""Plot verified coupled poroplastic fields for the paper and website."""
import csv
import json
from pathlib import Path
import shutil
import numpy as np
import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams.update({'pgf.texsystem':'lualatex','pgf.rcfonts':False,
    'font.family':'serif','font.size':9,'legend.fontsize':8})
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pgf import FigureCanvasPgf
from plot_mandel_extended_results import B0, BIOT_RATIO_LIMITS, plot_spatial_contours
ROOT=Path(__file__).resolve().parents[1]

def read(name):
    with (ROOT/'validation'/name).open() as f:
        return [{k:float(v) for k,v in r.items()} for r in csv.DictReader(f)]

def save(fig,name):
    path=ROOT/'figures'/name
    fig.savefig(path.with_suffix('.png'),dpi=220)
    FigureCanvasPgf(fig).print_pgf(path.with_suffix('.pgf'))
    shutil.copyfile(path.with_suffix('.png'),ROOT/'docs/assets/img'/f'{name}.png')
    plt.close(fig)

def main():
    record=json.loads((ROOT/'validation/poroplastic_mandel_verification.json').read_text())
    if record.get('accepted') is not True: raise ValueError('Verification has not passed')
    rows=read('poroplastic_mandel_contours.csv')
    parameters = record['parameters']
    if not np.isclose(1. - parameters['K']/parameters['Ks'], B0):
        raise ValueError('The plastic and elastic figures must share the reference coefficient')
    for row in rows:
        row['B_ratio'] = row['B']/B0
    if not all(BIOT_RATIO_LIMITS[0] <= row['B_ratio'] <= BIOT_RATIO_LIMITS[1] for row in rows):
        raise ValueError('The shared Biot-ratio color scale would clip the computed field')
    plot_spatial_contours(
        rows, 'B_ratio', r'normalized Biot coefficient, $B/B_0$',
        ROOT/'figures/poroplastic_mandel_biot_ratio.pgf',
        limits=BIOT_RATIO_LIMITS,
        active_key='plastic_increment',
    )
    history=read('poroplastic_mandel_history.csv')
    t=np.array([r['time'] for r in history])
    fig,axes=plt.subplots(1,2,figsize=(6.4,2.7))
    axes[0].plot(t,[r['pressure_x0']/1e6 for r in history],label='$X=0$')
    axes[0].plot(t,[r['pressure_x08']/1e6 for r in history],label='$X=0.8$ m')
    axes[0].axhline(0,color='.5',lw=.7)
    axes[0].set_ylabel('Water pressure (MPa)'); axes[0].legend(frameon=False)
    axes[1].plot(t,[r['biot_average'] for r in history],label='$B$')
    axes[1].plot(t,[r['elastic_b_average'] for r in history],'--',label=r'$B_{\mathrm{el}}(p,J)$')
    axes[1].set_ylabel('Reference-volume average'); axes[1].legend(frameon=False)
    for ax in axes:
        ax.axvline(.2,color='.4',ls=':',lw=.8); ax.set_xlabel('Time (s)'); ax.grid(alpha=.2)
    fig.tight_layout()
    save(fig,'poroplastic_mandel_history')

if __name__=='__main__': main()
