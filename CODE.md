# Code reference

## Authoritative upstream implementation

- Source repository: `/home/jfoster/projects/research/reactive_transport/multicomponent_reactive_flow`
- Material: `moose_app/src/materials/ADConstrainedSkeletonBiotMaterial.C`
- Header: `moose_app/include/materials/ADConstrainedSkeletonBiotMaterial.h`
- Stress consumer: `moose_app/src/materials/ADReferenceSolidStressMaterial.C`
- Production tests: `moose_app/test/tests/nonlinear_biot_coefficient/`

## Algorithm

At each quadrature point:

1. assemble AD-valued \(\mathbf R_{\mathbf y}\) and \(\mathbf R_{,J}\);
2. solve the small dense tangent system with pivoted Gaussian elimination;
3. form the fixed-\(p_E\) derivative of the numerator and denominator of
   \(\bar v_s\);
4. compute AD-valued \(B\) and intrinsic density \(1/\bar v_s\); and
5. consume \(B\) in
   \(\mathbf P_s=\mathbf P_s''-Bp_EJ_s\mathbf F_s^{-T}\).

`raw_value` is permitted only for pivot selection, singularity checks, and
diagnostic norms. It must not sever the arithmetic path that produces \(B\).

## Build environment

```bash
eval "$(~/miniconda3/bin/conda shell.bash hook)"
conda activate moose
export MOOSE_DIR=~/.local/moose
export LD_LIBRARY_PATH=~/.local/moose/framework:${LD_LIBRARY_PATH:-}
```

The initial experiment decks in this paper repository run with the optimized
application in the upstream repository. `moose/source_manifest.yml` records the
exact upstream files and revision status used for each paper result.

