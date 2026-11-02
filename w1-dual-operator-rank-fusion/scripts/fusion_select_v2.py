"""Fresh grouped-CV selection and v2 freeze for the fusion study."""
from __future__ import annotations

import hashlib
import itertools
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from scipy.optimize import differential_evolution, minimize

GRID = np.linspace(0.0, 1.0, 41)
COVARIATES = ("pbar_E", "dbar", "Pesc_bar", "rho_P", "rho_NB", "S_MP", "kappa_E")


def score(curves, c):
    return float(np.mean([np.interp(v, GRID, row) for row, v in zip(curves, c)]))


def fit_family(name, x, curves):
    x = np.asarray(x, float)
    scale = max(float(np.ptp(x)), 1e-12)
    z = (x - x.min()) / scale

    def objective(c):
        return -score(curves, np.clip(c, 0, 1))

    if name == "constant":
        j = int(np.argmax(np.mean(curves, axis=0)))
        return {"c": float(GRID[j])}
    if name == "hard_gate":
        best = max(((objective((x > t).astype(float)), {"tau": float(t)})
                    for t in np.unique(x)), key=lambda v: -v[0])
        return best[1]
    if name == "clipped_linear":
        r = differential_evolution(lambda q: objective(q[0] * z + q[1]),
                                    [(-8, 8), (-2, 2)], seed=20261102, polish=True)
        return {"a": float(r.x[0]), "b": float(r.x[1]),
                "scale_min": float(x.min()), "scale": scale}
    if name == "logistic":
        r = differential_evolution(
            lambda q: objective(1 / (1 + np.exp(-np.clip(q[0] * (z - q[1]), -60, 60)))),
            [(-12, 12), (0, 1)], seed=20261103, polish=True)
        return {"a": float(r.x[0]), "tau": float(x.min() + r.x[1] * scale),
                "scale_min": float(x.min()), "scale": scale}
    if name == "isotonic":
        order = np.argsort(x)
        vals = np.maximum.accumulate(np.array([
            np.mean(curves[order[i:j]], axis=0).argmax() / 40
            for i, j in zip(np.linspace(0, len(x) - 1, 5, dtype=int),
                             np.r_[np.linspace(0, len(x) - 1, 5, dtype=int)[1:], len(x)])
        ]))
        return {"breaks": [float(v) for v in np.quantile(x, [0.2, 0.4, 0.6, 0.8])],
                "values": [float(v) for v in vals]}
    if name == "spline":
        r = minimize(lambda q: objective(np.polyval(q, z)), [0.0, 0.0, 0.0, 0.5],
                     method="Nelder-Mead", options={"maxiter": 5000})
        return {"coefficients": [float(v) for v in r.x],
                "scale_min": float(x.min()), "scale": scale}
    raise ValueError(name)


def predict(name, x, params):
    x = np.asarray(x, float)
    if name == "constant":
        return np.full(len(x), params["c"])
    if name == "hard_gate":
        return (x > params["tau"]).astype(float)
    if name == "isotonic":
        return np.asarray(params["values"])[np.searchsorted(params["breaks"], x, side="right")]
    z = (x - params["scale_min"]) / params["scale"]
    if name == "clipped_linear":
        return np.clip(params["a"] * z + params["b"], 0, 1)
    if name == "logistic":
        return 1 / (1 + np.exp(-np.clip(params["a"] * (z - (params["tau"] - params["scale_min"]) / params["scale"]), -60, 60)))
    if name == "spline":
        return np.clip(np.polyval(params["coefficients"], z), 0, 1)
    raise ValueError(name)


def load_rows(root):
    rows = []
    for panel in ("dev", "test3", "fit500"):
        path = root / "results" / "fusion" / "fit" / f"{panel}.json"
        if panel == "test3":
            path = root / "results" / "fusion" / "fit" / f"{panel}.json"
        rows.extend(json.loads(path.read_text()))
    return rows


def main():
    root = Path(__file__).resolve().parents[1]
    rows = load_rows(root)
    curves_a = np.array([r["curve_yA"] for r in rows])
    curves_b = np.array([r["curve_yB"] for r in rows])
    groups = np.array([r.get("family", "unknown") for r in rows])
    candidates = []
    for cov in COVARIATES:
        x = np.array([r["covariates"][cov] for r in rows])
        for family in ("constant", "hard_gate", "clipped_linear", "logistic", "isotonic", "spline"):
            fold_scores = []
            for group in np.unique(groups):
                train = groups != group
                params = fit_family(family, x[train], curves_b[train])
                fold_scores.append(score(curves_a[~train], predict(family, x[~train], params)))
            params = fit_family(family, x, curves_b)
            candidates.append({
                "covariate": cov, "family": family, "parameters": params,
                "cv_mean": float(np.mean(fold_scores)),
                "cv_se": float(np.std(fold_scores, ddof=1) / np.sqrt(len(fold_scores))),
                "fit_score": score(curves_b, predict(family, x, params)),
                "parameters_count": len(params),
            })
    best = max(candidates, key=lambda r: r["cv_mean"])
    eligible = [r for r in candidates if r["cv_mean"] >= best["cv_mean"] - best["cv_se"]]
    eligible.sort(key=lambda r: (r["parameters_count"], r["covariate"] != "pbar_E", r["fit_score"] * -1))
    chosen = eligible[0]
    x = np.array([r["covariates"][chosen["covariate"]] for r in rows])
    c0_params = fit_family("constant", x, curves_b)
    gate_params = fit_family("hard_gate", x, curves_b)
    frozen = {
        "member_W": "w1.algorithm.w1_scores(inst, w1.algorithm.W1)",
        "member_M": "w1.diffusion.knz_mp(inst, iters=2)[0]",
        "covariate": chosen["covariate"], "family": chosen["family"],
        "parameters": chosen["parameters"], "c0": c0_params["c"],
        "hard_gate_tau": gate_params["tau"],
        "fit_panels": ["dev", "test3", "fit500"],
        "hold_panels": ["scale3", "big2", "oof", "real_hold"],
        "hypotheses": ["H1: F_v2 > W1", "H2: F_v2 > F_c0_v2", "H3: F_v2 > MP2"],
        "statistical_plan": "two-sided Wilcoxon with Holm; instance and generator/network clustered bootstrap, 20,000 resamples",
        "selection": {"cv_candidates": candidates, "best": best, "one_se_eligible": eligible},
        "utc": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
    }
    out = root / "results" / "fusion"
    raw = json.dumps(frozen, indent=2, sort_keys=True) + "\n"
    (out / "frozen_fusion_v2.json").write_text(raw)
    (out / "frozen_fusion_v2.sha256").write_text(hashlib.sha256(raw.encode()).hexdigest() + "\n")
    print(json.dumps({"covariate": chosen["covariate"], "family": chosen["family"],
                      "parameters": chosen["parameters"], "cv_mean": chosen["cv_mean"]}, indent=2))


if __name__ == "__main__":
    main()
