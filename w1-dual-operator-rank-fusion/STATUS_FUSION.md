# Fusion study status

## F0 — baseline and member reproduction

- Branch: `exp/w1-mp2-fusion`, based on commit `4e806ed`.
- Baseline tests: `test_algorithm.py` and `test_reproduction.py` pass in the isolated requirements environment.
- W1 and MP2 reproduction: first 20 `test2` instances, maximum absolute difference in stored Spearman rho: `0.0`.
- No held-out member computation was performed before the F1 artifacts.

## F1 — data search, evidence mode and split

The reproducible search is `python scripts/fusion_search_real.py`. Four NetworkX-bundled
networks were obtained; the evidence mode is therefore `synthetic` under the prescribed
thresholds. The search log, evidence mode and pre-registered split are in
`results/fusion/`.
