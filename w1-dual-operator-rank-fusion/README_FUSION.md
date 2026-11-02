# Regime-adaptive W1/MP2 fusion

This additive experiment evaluates rank fusion of the frozen W1 member and
two-iteration Karrer–Newman–Zdeborová message passing. The declared evidence
mode and split are generated before any held-out evaluation.

From the package directory, using Python 3.11+ and the pinned requirements:

```bash
python scripts/fusion_search_real.py
python scripts/fusion_run.py dev
python scripts/fusion_select.py
python scripts/fusion_confirm.py dev
python tests/test_fusion.py
```

All numerical commands must use `OMP_NUM_THREADS=MKL_NUM_THREADS=OPENBLAS_NUM_THREADS=1`.
The current baseline evidence mode is synthetic because four NetworkX-bundled
real networks were obtained; the search and split are recorded under
`results/fusion/`.
