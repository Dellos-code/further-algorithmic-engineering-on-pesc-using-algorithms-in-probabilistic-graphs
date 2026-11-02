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

## F2–F5 — FIT, freeze and fresh confirmation

- FIT: 180 `dev` instances, 41-point rank-fusion curves on both `yA` and `yB`,
  all seven graph-only covariates, and deterministic member/covariate timing.
- Freeze commit: `d4fded8`; SHA-256 is recorded in `results/fusion/frozen_fusion.sha256`.
- Frozen rule: clipped-linear `pbar_E` function; the FIT objective selected it
  over the constant and hard-gate candidates implemented in this increment.
- Fresh `test3`: 180 instances with new repetitions 6 and 7. The fresh-panel
  paired results are in `results/fusion/confirm_test3.stats.csv`; family-level
  means and a 20,000-resample family bootstrap are also stored.

## Deviations and limitations

The current increment is synthetic evidence, not a 24-network real-network
study. External source acquisition beyond the four bundled NetworkX graphs is
recorded but not completed. The candidate-family implementation currently
contains constant, hard-gate and clipped-linear families; logistic, isotonic,
spline and two-covariate candidates, grouped nested cross-validation, the
large `scale3`/`big2` panels, Monte Carlo cost curves, exploratory
per-vertex fusion, and XeLaTeX zero-box validation remain explicit follow-up
work. The stored fresh results therefore support a reproducible pilot, not
the full confirmatory claim in the master protocol.

## Part 1 — stage B checkpoint

- 2026-11-02T17:43:11Z — stage B complete: recorded `ERRATA_FUSION.md`,
  recomputed `confirm_test2.stats_v2.csv` and `confirm_test3.stats_v2.csv`
  with all-instance means, two-sided Wilcoxon tests, Holm adjustment, and
  20,000-resample instance/family bootstrap intervals; recorded the pinned
  environment. Previous checkpoint: `a497ade`.
- Baseline reproduction gate: `test_algorithm.py` and `test_reproduction.py`,
  15 tests, passed in the pinned environment.

- 2026-11-02T17:49:00Z — stage R complete: attempted the listed real-network
  sources and mirrors with recorded commands, timestamps, HTTP status/error
  text, and retained the four bundled NetworkX networks. Wrote
  `data_search_v2.json`, `data_search_log_v2.md`, `evidence_mode_v2.json`,
  and `split_v2.json`; evidence mode is synthetic with R=4. Previous
  checkpoint: `4b2d034`.

- 2026-11-02T19:46:56Z — stage S computation note: the full `fit500`
  covariate run was stopped after approximately two hours without a final
  aggregate file because the exact Python non-backtracking iteration was the
  bottleneck. To complete the pipeline, the committed `rho_nb` iteration cap
  is reduced from 500 to 100 for the new fitting and held-out panels. This is
  an explicit computational reduction and is reported as a deviation.

- 2026-11-02T20:26:03Z — stage S complete: built the new `fit500` panel
  (180 instances) and computed FIT curves/covariates for `fit500` and the
  no-longer-blind `test3`. Stage V2 selection completed over the recorded
  candidate families and covariates with grouped family CV and one-standard-
  error tie breaking. Previous checkpoint: `b1d289b`.
- 2026-11-02T20:26:03Z — stage V2 freeze prepared: selected `hard_gate` on
  `pbar_E`, wrote `frozen_fusion_v2.json` and
  `frozen_fusion_v2.sha256` (`2c3f5e7a8146590da5c20395ef11eb65f18f5f388c5db47d8b21f30420c49a2a`).
  No `scale3`, `big2`, `oof`, or real-HOLD member/ground-truth computation
  occurred before this checkpoint.

- 2026-11-02T21:15:19Z — stage H computation note: the post-freeze `oof`
  build was reduced to five generator families at `n=500`, one `R3`
  probability range, and uniform prior after the full requested panel failed
  to finish within the session budget. This explicit reduction is a deviation.

- 2026-11-02T21:22:46Z — stage H/D complete: evaluated v1 and v2 on
  `scale3`, `big2`, and the reduced `oof` panel; wrote instance, family, and
  20,000-resample family-clustered bootstrap outputs. Final tests pass
  (`18 passed`), and both English and Greek chapters compile in three XeLaTeX
  passes with no reported errors, overfull boxes, or underfull boxes.
  Previous checkpoint: `99e3824`.

### Post-freeze v2 instance-level results

The v2 paired results are in `results/fusion/confirm_*_v2.stats.csv`.
For `scale3`, H1/H2/H3 mean differences are `0.034675`, `0.019129`, and
`0.030008`, with Holm-adjusted two-sided p-values `0.064453`, `0.078677`,
and `0.016113`. For `big2`, the corresponding values are `0.044718`,
`0.025819`, and `0.029370`, with adjusted p-values `0.002419`, `0.001432`,
and `0.000168`. The reduced `oof` panel gives `0`, `-0.011367`, and
`-0.022183`, with adjusted p-values `1`, `0.5625`, and `1`; these are
descriptive because the panel was reduced.
