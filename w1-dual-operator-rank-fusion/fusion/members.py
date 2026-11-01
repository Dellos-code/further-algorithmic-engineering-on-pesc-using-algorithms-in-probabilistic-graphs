"""Frozen W1/MP members and rank-domain fusion helpers."""
from __future__ import annotations

import numpy as np

from w1.algorithm import W1, w1_scores
from w1.diffusion import knz_mp
from w1.metrics import ranks_of


def member_scores(inst):
    """Return deployable member score vectors without using ground truth."""
    return {"W1": w1_scores(inst, W1), "MP2": knz_mp(inst, iters=2)[0]}


def fusion_scores(inst, c: float) -> np.ndarray:
    """Fuse W1 and MP2 in rank space, with c=0 equal to W1 and c=1 to MP2."""
    if not 0.0 <= c <= 1.0:
        raise ValueError("c must be in [0, 1]")
    scores = member_scores(inst)
    rw = ranks_of(scores["W1"])
    rm = ranks_of(scores["MP2"])
    return (1.0 - c) * rw + c * rm
