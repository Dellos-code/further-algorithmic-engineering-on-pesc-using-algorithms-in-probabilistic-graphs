"""Compute FIT-only member curves and covariates."""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fusion.covariates import covariates
from fusion.members import member_scores
from w1.instances import load_instance, panel_paths
from w1.metrics import ranks_of, spearman


GRID = np.linspace(0.0, 1.0, 41)


def run(panel: str, out: Path):
    rows = []
    for path in panel_paths(Path("data"), panel):
        t0 = time.perf_counter()
        inst, yA, yB, _ = load_instance(path)
        members = member_scores(inst)
        rw, rm = ranks_of(members["W1"]), ranks_of(members["MP2"])
        curve_a = [spearman((1 - c) * rw + c * rm, ranks_of(yA)) for c in GRID]
        curve_b = [spearman((1 - c) * rw + c * rm, ranks_of(yB)) for c in GRID]
        j = int(np.argmax(curve_b))
        rows.append({
            "id": int(path.stem), "name": inst.name, "family": inst.meta.get("family"),
            "n": inst.n, "m": inst.m, "panel": panel,
            "rho_W1": float(curve_a[0]), "rho_MP2": float(curve_a[-1]),
            "curve_yA": curve_a, "curve_yB": curve_b, "c_star_B": float(GRID[j]),
            "flat_B": [float(c) for c, v in zip(GRID, curve_b) if v >= curve_b[j] - 0.002],
            "covariates": covariates(inst),
            "seconds_members_covariates": time.perf_counter() - t0,
        })
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{panel}.json").write_text(json.dumps(rows, indent=2) + "\n")
    print(f"{panel}: {len(rows)} instances -> {out / (panel + '.json')}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("panel")
    ap.add_argument("--out", type=Path, default=Path("results/fusion/fit"))
    args = ap.parse_args()
    run(args.panel, args.out)
