"""Compute generator-family clustered bootstrap intervals from held-out output."""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def main(panel: str) -> None:
    root = Path(__file__).resolve().parents[1]
    df = pd.read_csv(root / "results" / "fusion" / f"confirm_{panel}_v2.csv")
    wide = df.pivot(index=["id", "family"], columns="method", values="rho").reset_index()
    rows = []
    rng = np.random.default_rng(20261102)
    for version, fusion in (("v1", "F_v1"), ("v2", "F_v2")):
        for label, base in (("H1", "W1"), ("H2", "F_c0_v2"), ("H3", "MP2")):
            grouped = wide.groupby("family", sort=True)[[fusion, base]].mean()
            diff = (grouped[fusion] - grouped[base]).to_numpy()
            boot = diff[rng.integers(0, len(diff), size=(20_000, len(diff)))].mean(axis=1)
            rows.append({"version": version, "contrast": label,
                         "clusters": len(diff), "mean_difference": float(diff.mean()),
                         "bootstrap_lo": float(np.quantile(boot, .025)),
                         "bootstrap_hi": float(np.quantile(boot, .975))})
    pd.DataFrame(rows).to_csv(root / "results" / "fusion" / f"confirm_{panel}_v2.cluster_bootstrap.csv", index=False)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("panels", nargs="+")
    for panel in ap.parse_args().panels:
        main(panel)
