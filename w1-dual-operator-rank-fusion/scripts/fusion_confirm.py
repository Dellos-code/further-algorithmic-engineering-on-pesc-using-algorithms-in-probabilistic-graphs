"""Evaluate a frozen fusion on a panel, without fitting or selecting."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fusion.members import member_scores
from w1.instances import load_instance, panel_paths
from w1.metrics import full_metrics, ranks_of


def c_for(row, frozen):
    phi = row["covariates"][frozen["covariate"]]
    p = frozen["parameters"]
    if frozen["family"] == "constant":
        return p["c"]
    if frozen["family"] == "hard_gate":
        return float(phi > p["tau"])
    z = (phi - p["scale_min"]) / p["scale"]
    return float(np.clip(p["a"] * z + p["b"], 0, 1))


def run(panel, frozen_path, out_path):
    frozen = json.loads(Path(frozen_path).read_text())
    rows = []
    fit_rows = json.loads(Path("results/fusion/fit/dev.json").read_text())
    cov_by_id = {r["id"]: r for r in fit_rows} if panel == "dev" else {}
    for path in panel_paths(Path("data"), panel):
        inst, yA, yB, _ = load_instance(path)
        s = member_scores(inst)
        rw, rm, truth = ranks_of(s["W1"]), ranks_of(s["MP2"]), ranks_of(yA)
        phi = float(np.mean(inst.p))
        c = c_for({"covariates": {frozen["covariate"]: phi}}, frozen)
        methods = {"W1": rw, "MP2": rm, "F_g": (1-c) * rw + c * rm,
                   "F_c0": (1-frozen["c0"]) * rw + frozen["c0"] * rm}
        for name, vec in methods.items():
            rows.append({"id": int(path.stem), "method": name,
                         "rho": full_metrics(vec, yA, truth)["rho"], "c": c})
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(out_path, index=False)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("panel")
    ap.add_argument("--frozen", default="results/fusion/frozen_fusion.json")
    ap.add_argument("--out", default="results/fusion/confirm.csv")
    args = ap.parse_args()
    run(args.panel, args.frozen, args.out)
