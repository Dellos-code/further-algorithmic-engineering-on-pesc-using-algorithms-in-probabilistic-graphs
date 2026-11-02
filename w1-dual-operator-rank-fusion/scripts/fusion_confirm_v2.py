"""Post-freeze confirmation for v1 and v2 on held-out panels."""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fusion.members import member_scores
from w1.hybrid import baseline_scores
from w1.instances import load_instance, panel_paths, stable_seed
from w1.metrics import full_metrics, ranks_of


def coefficient(phi, frozen):
    p = frozen["parameters"]
    if frozen["family"] == "constant":
        return float(p["c"])
    if frozen["family"] == "hard_gate":
        return float(phi > p["tau"])
    z = (phi - p["scale_min"]) / p["scale"]
    if frozen["family"] == "logistic":
        return float(1 / (1 + np.exp(-np.clip(p["a"] * (z - p["tau"]), -60, 60))))
    return float(np.clip(p["a"] * z + p["b"], 0, 1))


def run(panel: str, root: Path) -> pd.DataFrame:
    frozen = json.loads((root / "results" / "fusion" / "frozen_fusion_v2.json").read_text())
    frozen_v1 = json.loads((root / "results" / "fusion" / "frozen_fusion.json").read_text())
    rows = []
    for path in panel_paths(root / "data", panel):
        inst, y_a, y_b, _ = load_instance(path)
        t0 = time.perf_counter()
        members = member_scores(inst)
        rw, rm = ranks_of(members["W1"]), ranks_of(members["MP2"])
        phi = float(np.mean(inst.p))
        c = coefficient(phi, frozen)
        c1 = float(np.clip(frozen_v1["parameters"]["a"] *
                           (phi - frozen_v1["parameters"]["scale_min"]) /
                           frozen_v1["parameters"]["scale"] +
                           frozen_v1["parameters"]["b"], 0, 1))
        c0 = float(frozen["c0"])
        gate = float(phi > frozen["hard_gate_tau"])
        curve = np.array([full_metrics((1-v) * rw + v * rm, y_b, ranks_of(y_b))["rho"]
                          for v in np.linspace(0, 1, 41)])
        oracle_c = float(np.argmax(curve) / 40)
        methods = {
            "W1": rw, "MP2": rm, "F_v1": (1-c1) * rw + c1 * rm,
            "F_v2": (1-c) * rw + c * rm,
            "F_c0_v2": (1-c0) * rw + c0 * rm,
            "F_gate_v2": (1-gate) * rw + gate * rm,
            "F_oracle_c": (1-oracle_c) * rw + oracle_c * rm,
            "F_best_two": rw if curve[0] >= curve[-1] else rm,
        }
        methods.update(baseline_scores(inst, y_b, names=("MPinf", "IRIE_exact", "oracle:scalar")))
        for name, vec in methods.items():
            rows.append({"id": int(path.stem), "family": inst.meta.get("family", "unknown"),
                         "n": inst.n, "method": name,
                         "rho": full_metrics(vec, y_a, ranks_of(y_a))["rho"],
                         "c": c, "seconds": time.perf_counter() - t0})
    out = root / "results" / "fusion"
    pd.DataFrame(rows).to_csv(out / f"confirm_{panel}_v2.csv", index=False)
    return pd.DataFrame(rows)


def summarize(panel: str, df: pd.DataFrame, root: Path) -> None:
    wide = df.pivot(index="id", columns="method", values="rho")
    contrasts = {"H1": "W1", "H2": "F_c0_v2", "H3": "MP2"}
    rows = []
    pvals = {}
    from scipy.stats import wilcoxon
    for version, fusion in (("v1", "F_v1"), ("v2", "F_v2")):
        pvals = {}
        subset = []
        for label, base in contrasts.items():
            d = (wide[fusion] - wide[base]).to_numpy()
            nz = d[d != 0]
            p = float(wilcoxon(nz).pvalue) if len(nz) else 1.0
            subset.append({"version": version, "contrast": label, "n": len(d),
                           "mean_difference": float(d.mean()),
                           "wins": int((d > 0).sum()), "losses": int((d < 0).sum()),
                           "ties": int((d == 0).sum()), "p_two_sided": p})
            pvals[label] = p
        ordered = sorted(pvals, key=pvals.get)
        for row in subset:
            row["p_holm"] = min(1.0, pvals[row["contrast"]] * (len(subset) - ordered.index(row["contrast"])))
        rows.extend(subset)
    result = pd.DataFrame(rows)
    result.to_csv(root / "results" / "fusion" / f"confirm_{panel}_v2.stats.csv", index=False)
    cluster = df.groupby(["family", "method"], as_index=False).rho.mean()
    cluster.to_csv(root / "results" / "fusion" / f"confirm_{panel}_v2.cluster.csv", index=False)
    print(panel)
    print(result.to_string(index=False))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("panels", nargs="+")
    args = ap.parse_args()
    root = Path(__file__).resolve().parents[1]
    for panel in args.panels:
        frame = run(panel, root)
        summarize(panel, frame, root)


if __name__ == "__main__":
    main()
