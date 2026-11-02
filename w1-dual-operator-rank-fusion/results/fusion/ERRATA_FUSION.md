# Errata for the pilot fusion increment

This file records corrections as new evidence; the pilot freeze
`frozen_fusion.json`, its digest, commit `d4fded8`, and the pilot `test3`
assets remain immutable.

1. The original `confirm_test3.stats.csv` and `confirm_test2.stats.csv`
   report `mean_difference` only over non-zero differences and use one-sided
   Wilcoxon tests. The corrected `*_v2.csv` files use the mean over all
   instances, report wins/losses/ties, use two-sided tests with zero
   differences removed only inside the test, apply Holm adjustment, and add
   95% instance-level and family-clustered bootstrap intervals with 20,000
   resamples. `test2` is not blind and is exploratory.
2. `split.json` labels `cp`, `tree`, and `barbell` as held-out families, but
   the rule was fitted on `dev`, which contains all nine families. There was
   therefore no out-of-family test in the pilot.
3. The `"utc"` field in `frozen_fusion.json` is a placeholder
   (`2026-11-01T00:00:00Z`). The freeze commit was made at
   `2026-11-02 00:00:46 UTC` (`d4fded8`); the valid record is the commit
   order, with freeze before `test3`.
4. The baseline search log records source names as “not acquired” without
   actual download attempts or error text, and the four NetworkX networks
   were not evaluated. The real-network search was not carried out.
5. Only constant, hard-gate, and clipped-linear families were fitted; the
   clipped-linear slope was restricted to `{-2, 0, 2}`. Grouped
   cross-validation and covariate comparison were not performed.
6. The existing thesis chapter sources do not compile and do not satisfy the
   documentation requirements: macro names such as `\MeanF_g` contain
   underscores, and the required complete chapter content is absent.

The second-round work below is exploratory until the new selection and freeze
are committed.
