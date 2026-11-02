"""Select a compact regime function on FIT and write the immutable freeze."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fusion.gfamilies import GRID, fit_clipped_linear, fit_constant, fit_hard_gate


def main():
    root = Path(__file__).resolve().parents[1]
    data = json.loads((root / "results/fusion/fit/dev.json").read_text())
    covariate = "pbar_E"
    phi = np.array([r["covariates"][covariate] for r in data])
    curves = np.array([r["curve_yB"] for r in data])
    candidates = {
        "constant": fit_constant(curves, phi),
        "hard_gate": fit_hard_gate(curves, phi),
        "clipped_linear": fit_clipped_linear(curves, phi),
    }
    scores = {}
    for family, params in candidates.items():
        if family == "constant":
            c = np.full(len(phi), params["c"])
        elif family == "hard_gate":
            c = (phi > params["tau"]).astype(float)
        else:
            z = (phi - params["scale_min"]) / params["scale"]
            c = np.clip(params["a"] * z + params["b"], 0, 1)
        scores[family] = float(np.mean([np.interp(ci, GRID, row) for ci, row in zip(c, curves)]))
    family = max(scores, key=scores.get)
    c0 = fit_constant(curves, phi)["c"]
    frozen = {
        "member_W": "w1.algorithm.w1_scores(inst, w1.algorithm.W1)",
        "member_M": "w1.diffusion.knz_mp(inst, iters=2)[0]",
        "covariate": covariate, "family": family, "parameters": candidates[family],
        "c0": c0, "hard_gate_tau": candidates["hard_gate"].get("tau"),
        "fit_panel": "dev", "hold_panels": ["cp/tree/barbell synthetic family hold"],
        "hypotheses": ["H1: F_g > W1", "H2: F_g > F_c0", "H3: F_g > MP2"],
        "statistical_plan": "paired two-sided Wilcoxon with Holm; network/family clustered bootstrap",
        "scores_yB": scores,
        "utc": "2026-11-01T00:00:00Z",
    }
    out = root / "results/fusion"
    raw = json.dumps(frozen, indent=2, sort_keys=True) + "\n"
    (out / "frozen_fusion.json").write_text(raw)
    (out / "frozen_fusion.sha256").write_text(hashlib.sha256(raw.encode()).hexdigest() + "\n")
    print(json.dumps({"family": family, "parameters": candidates[family], "scores": scores}, indent=2))


if __name__ == "__main__":
    main()
