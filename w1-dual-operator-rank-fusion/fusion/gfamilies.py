"""Small deterministic candidate family implementations for g(phi)."""
from __future__ import annotations

import numpy as np
from scipy.optimize import minimize_scalar


GRID = np.linspace(0.0, 1.0, 41)


def constant(phi, params):
    return np.full(len(np.asarray(phi)), float(params["c"]))


def hard_gate(phi, params):
    return (np.asarray(phi) > float(params["tau"])).astype(float)


def clipped_linear(phi, params):
    z = np.asarray(phi, float)
    return np.clip(float(params["a"]) * z + float(params["b"]), 0.0, 1.0)


def logistic(phi, params):
    z = np.asarray(phi, float)
    return 1.0 / (1.0 + np.exp(-np.clip(float(params["a"]) * (z - float(params["tau"])), -60, 60)))


def fit_constant(curves, phi):
    mean_curve = np.mean(curves, axis=0)
    j = int(np.argmax(mean_curve))
    return {"c": float(GRID[j])}


def fit_hard_gate(curves, phi):
    best = (-np.inf, None)
    for tau in np.unique(np.asarray(phi)):
        pred = hard_gate(phi, {"tau": tau})
        score = float(np.mean([np.interp(c, GRID, row) for c, row in zip(pred, curves)]))
        if score > best[0]:
            best = (score, {"tau": float(tau)})
    return best[1]


def fit_clipped_linear(curves, phi):
    phi = np.asarray(phi, float)
    scale = max(float(np.ptp(phi)), 1e-12)
    z = (phi - phi.min()) / scale

    def objective(q):
        pred = np.clip(q[0] * z + q[1], 0.0, 1.0)
        return -float(np.mean([np.interp(c, GRID, row) for c, row in zip(pred, curves)]))

    best = None
    for a0 in (-2.0, 0.0, 2.0):
        r = minimize_scalar(lambda b: objective((a0, b)), bounds=(-1, 2), method="bounded")
        cand = {"a": a0, "b": float(r.x), "scale_min": float(phi.min()), "scale": scale}
        score = -objective((a0, r.x))
        if best is None or score > best[0]:
            best = score, cand
    return best[1]


FAMILIES = {
    "constant": constant,
    "hard_gate": hard_gate,
    "clipped_linear": clipped_linear,
    "logistic": logistic,
}
