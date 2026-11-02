"""Recompute pilot confirmation statistics under the prescribed protocol."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import wilcoxon


RESAMPLES = 20_000


def holm(pvalues: dict[str, float]) -> dict[str, float]:
    ordered = sorted(pvalues, key=pvalues.get)
    out = {}
    running = 0.0
    for i, name in enumerate(ordered):
        running = max(running, min(1.0, (len(ordered) - i) * pvalues[name]))
        out[name] = running
    return out


def instance_interval(diff: np.ndarray, seed: int) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    draws = rng.integers(0, len(diff), size=(RESAMPLES, len(diff)))
    means = diff[draws].mean(axis=1)
    return tuple(np.quantile(means, [0.025, 0.975]))


def cluster_interval(diff: np.ndarray, groups: np.ndarray, seed: int) -> tuple[float, float]:
    frame = pd.DataFrame({"group": groups, "diff": diff})
    means = frame.groupby("group", sort=True)["diff"].mean().to_numpy()
    rng = np.random.default_rng(seed)
    draws = rng.integers(0, len(means), size=(RESAMPLES, len(means)))
    boot = means[draws].mean(axis=1)
    return tuple(np.quantile(boot, [0.025, 0.975]))


def recompute(panel: str, root: Path) -> None:
    source = root / "results" / "fusion" / f"confirm_{panel}.csv"
    df = pd.read_csv(source)
    specs = json.loads((root / "data" / panel / "specs.json").read_text())
    groups = np.array([s.get("fam", s.get("g", "unknown")) for s in specs])
    wide = df.pivot(index="id", columns="method", values="rho").sort_index()
    contrasts = {"H1": "W1", "H2": "F_c0", "H3": "MP2"}
    rows = []
    pvalues = {}
    for name, baseline in contrasts.items():
        diff = (wide["F_g"] - wide[baseline]).to_numpy(float)
        nonzero = diff[diff != 0]
        p = float(wilcoxon(nonzero, alternative="two-sided").pvalue) if len(nonzero) else 1.0
        lo, hi = instance_interval(diff, 20261102 + len(rows))
        clo, chi = cluster_interval(diff, groups, 20361102 + len(rows))
        rows.append({
            "contrast": name,
            "n": int(len(diff)),
            "mean_difference": float(diff.mean()),
            "wins": int((diff > 0).sum()),
            "losses": int((diff < 0).sum()),
            "ties": int((diff == 0).sum()),
            "p_two_sided": p,
            "instance_bootstrap_lo": float(lo),
            "instance_bootstrap_hi": float(hi),
            "cluster_bootstrap_lo": float(clo),
            "cluster_bootstrap_hi": float(chi),
        })
        pvalues[name] = p
    adjusted = holm(pvalues)
    for row in rows:
        row["p_holm"] = adjusted[row["contrast"]]
    out = root / "results" / "fusion" / f"confirm_{panel}.stats_v2.csv"
    pd.DataFrame(rows).to_csv(out, index=False)
    print(out)
    print(pd.DataFrame(rows).to_string(index=False))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("panels", nargs="+", choices=("test2", "test3"))
    args = ap.parse_args()
    root = Path(__file__).resolve().parents[1]
    for panel in args.panels:
        recompute(panel, root)


if __name__ == "__main__":
    main()
