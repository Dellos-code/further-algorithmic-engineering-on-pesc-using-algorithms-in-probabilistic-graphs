# Fusion reproduction

The fusion experiment is additive to W1. Run from `w1-dual-operator-rank-fusion/`:

```bash
python scripts/fusion_search_real.py
OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 python scripts/fusion_run.py dev
OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 python scripts/fusion_select.py
OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 python scripts/fusion_confirm.py dev
python tests/test_fusion.py
```

The development run is CPU-bound and depends on the panel size. The four-network
search and the evidence mode are deterministic and require no network access.
