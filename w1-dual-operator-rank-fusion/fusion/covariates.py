"""Ground-truth-free graph covariates for regime adaptation."""
from __future__ import annotations

import numpy as np
import scipy.sparse as sp
from scipy.sparse.linalg import eigsh

from w1.diffusion import knz_mp


def rho_nb(inst, tol: float = 1e-12, maxit: int = 500) -> float:
    """Spectral radius of the p-weighted non-backtracking operator.

    The vector is indexed by directed edges u->v and the transition
    (u,v)->(v,w) has weight p(v,w).  The matrix is never materialised.
    """
    m = inst.m
    if m == 0:
        return 0.0
    edges = np.asarray(inst.edges, dtype=np.int64)
    p = np.asarray(inst.p, dtype=float)
    n = inst.n
    src = np.concatenate((edges[:, 0], edges[:, 1]))
    dst = np.concatenate((edges[:, 1], edges[:, 0]))
    prob = np.concatenate((p, p))
    incoming = [[] for _ in range(n)]
    for k, (u, v) in enumerate(zip(src, dst)):
        incoming[v].append(k)
    outgoing = [[] for _ in range(n)]
    for k, (u, v) in enumerate(zip(src, dst)):
        outgoing[u].append(k)
    rev = np.empty(2 * m, dtype=np.int64)
    rev[:m] = np.arange(m, 2 * m)
    rev[m:] = np.arange(m)
    q = np.ones(2 * m, dtype=float)
    q /= np.linalg.norm(q)
    lam = 0.0
    for _ in range(maxit):
        z = np.zeros_like(q)
        for k, (u, v) in enumerate(zip(src, dst)):
            total = 0.0
            for h in outgoing[v]:
                if h != rev[k]:
                    total += prob[h] * q[h]
            z[k] = total
        norm = float(np.linalg.norm(z))
        if norm == 0.0:
            return 0.0
        z /= norm
        new_lam = float(np.dot(z, np.asarray([sum(prob[h] * q[h] for h in outgoing[v] if h != rev[k])
                                               for k, (u, v) in enumerate(zip(src, dst))])))
        if abs(new_lam - lam) <= tol * max(1.0, abs(new_lam)):
            return abs(new_lam)
        q, lam = z, new_lam
    return abs(lam)


def covariates(inst) -> dict[str, float]:
    """Compute all pre-specified covariates from (G, p, x) only."""
    n, m = inst.n, inst.m
    if m:
        pbar = float(np.mean(inst.p))
        expected_degree = np.bincount(inst.edges.ravel(), weights=np.repeat(inst.p, 2), minlength=n)
    else:
        pbar = dbar = kappa = 0.0
        expected_degree = np.zeros(n)
    if m:
        dbar = float(expected_degree.mean())
        mean_k2 = float(np.mean(expected_degree ** 2))
        kappa = float(pbar * (mean_k2 - dbar) / dbar) if dbar else 0.0
    ops = inst.ops()
    pesc_bar = float(np.mean(ops["Pesc"])) if n else 0.0
    if m:
        rows = np.concatenate((inst.edges[:, 0], inst.edges[:, 1]))
        cols = np.concatenate((inst.edges[:, 1], inst.edges[:, 0]))
        vals = np.concatenate((inst.p, inst.p))
        P = sp.csr_matrix((vals, (rows, cols)), shape=(n, n))
        rho_p = float(eigsh((P + P.T) * 0.5, k=1, which="LM", return_eigenvectors=False)[0])
    else:
        rho_p = 0.0
    mu = knz_mp(inst, iters=None)[0]
    return {
        "pbar_E": pbar,
        "dbar": dbar,
        "Pesc_bar": pesc_bar,
        "rho_P": rho_p,
        "rho_NB": rho_nb(inst),
        "S_MP": float(np.dot(inst.x, mu)),
        "kappa_E": kappa,
    }
