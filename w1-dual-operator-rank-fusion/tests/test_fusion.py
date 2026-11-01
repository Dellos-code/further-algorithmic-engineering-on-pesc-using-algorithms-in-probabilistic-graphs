import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from fusion.covariates import covariates, rho_nb
from fusion.members import fusion_scores
from w1.instances import Instance
from w1.metrics import ranks_of


def inst(edges, p, n, x=None):
    return Instance("toy", n, np.asarray(edges, dtype=np.int64), np.asarray(p, float),
                    np.ones(n) / n if x is None else np.asarray(x, float))


def test_fusion_endpoints():
    a = inst([(0, 1), (1, 2)], [0.4, 0.6], 3)
    assert np.array_equal(ranks_of(fusion_scores(a, 0)), ranks_of(fusion_scores(a, 0)))
    assert np.array_equal(fusion_scores(a, 0), ranks_of(fusion_scores(a, 0)))
    assert np.array_equal(fusion_scores(a, 1), ranks_of(fusion_scores(a, 1)))


def test_covariates_toy_values():
    a = inst([(0, 1), (1, 2)], [0.4, 0.6], 3)
    c = covariates(a)
    assert c["pbar_E"] == 0.5
    assert np.isclose(c["dbar"], 2 * 1.0 / 3)
    assert np.isclose(c["rho_NB"], 0.0, atol=1e-10)


def test_regular_graph_nonbacktracking():
    edges = [(0, 1), (1, 2), (2, 3), (3, 0)]
    assert np.isclose(rho_nb(inst(edges, [0.2] * 4, 4)), 0.4, atol=1e-8)
