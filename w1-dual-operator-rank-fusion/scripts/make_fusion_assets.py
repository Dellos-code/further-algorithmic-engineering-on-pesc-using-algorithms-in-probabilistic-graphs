"""Generate thesis macros from fusion result tables."""
from __future__ import annotations

import csv
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[1]
    path = root / "results/fusion/confirm_test3.csv"
    rows = list(csv.DictReader(path.open()))
    means = {}
    for method in ("F_g", "F_c0", "W1", "MP2"):
        vals = [float(r["rho"]) for r in rows if r["method"] == method]
        means[method] = sum(vals) / len(vals)
    out = root / "thesis/fusion"
    out.mkdir(parents=True, exist_ok=True)
    (out / "fusion_numbers.tex").write_text("\n".join(
        rf"\newcommand{{\Mean{m}}}{{{v:.6f}}}" for m, v in means.items()) + "\n")


if __name__ == "__main__":
    main()
