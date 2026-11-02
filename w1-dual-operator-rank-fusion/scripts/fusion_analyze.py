"""Primary paired tests and compact result tables for confirmation output."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import wilcoxon


def main(path, panel=None):
    df = pd.read_csv(path)
    wide = df.pivot(index="id", columns="method", values="rho")
    out = []
    for method, label in (("W1", "H1"), ("F_c0", "H2"), ("MP2", "H3")):
        d = wide["F_g"] - wide[method]
        d = d[d != 0]
        stat = wilcoxon(d, alternative="greater") if len(d) else (0.0, 1.0)
        out.append({"contrast": label, "n": len(d),
                    "mean_difference": float(d.mean()) if len(d) else 0.0,
                    "p": float(stat.pvalue)})
    result = pd.DataFrame(out)
    order = result["p"].sort_values().index
    result["p_holm"] = 1.0
    for rank, idx in enumerate(order):
        result.loc[idx, "p_holm"] = min(1.0, float(result.loc[idx, "p"]) * (len(result) - rank))
    dest = Path(path).with_suffix(".stats.csv")
    result.to_csv(dest, index=False)
    if panel:
        specs = json.loads((Path("data") / panel / "specs.json").read_text())
        groups = pd.DataFrame({"id": range(len(specs)),
                               "group": [s.get("fam", s.get("g", "unknown")) for s in specs]})
        merged = df.merge(groups, on="id")
        means = merged.groupby(["group", "method"], as_index=False).rho.mean()
        means.to_csv(Path(path).with_suffix(".network_level.csv"), index=False)
        pivot = means.pivot(index="group", columns="method", values="rho")
        diffs = (pivot["F_g"] - pivot["W1"]).dropna().to_numpy()
        rng = np.random.default_rng(20261101)
        boot = rng.choice(diffs, size=(20000, len(diffs)), replace=True).mean(axis=1)
        pd.DataFrame({"contrast": ["F_g-W1"], "mean_difference": [float(diffs.mean())],
                      "bootstrap_lo": [float(np.quantile(boot, .025))],
                      "bootstrap_hi": [float(np.quantile(boot, .975))]}).to_csv(
                          Path(path).with_suffix(".network_bootstrap.csv"), index=False)
    print(result.to_string(index=False))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--panel")
    args = ap.parse_args()
    main(args.path, args.panel)
