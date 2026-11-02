# Fusion reproduction

The fusion experiment is additive to W1. Run from `w1-dual-operator-rank-fusion/`:

```bash
python scripts/fusion_search_real.py
OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 python scripts/fusion_run.py dev
OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 python scripts/fusion_build_panels.py fit500
OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 python scripts/fusion_run.py fit500
OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 python scripts/fusion_run.py test3
OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 python scripts/fusion_select_v2.py
OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 python scripts/fusion_confirm.py dev
python tests/test_fusion.py
```

The development and fitting runs are CPU-bound and can take hours. The
four-network search records actual source and mirror attempts. The evidence
mode is synthetic because four real networks were obtainable.
