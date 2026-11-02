"""Generate thesis macros from committed fusion evidence."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


def main():
    root = Path(__file__).resolve().parents[1]
    stats = pd.read_csv(root / "results/fusion/confirm_test3.stats_v2.csv")
    freeze_path = root / "results/fusion/frozen_fusion_v2.json"
    freeze = json.loads(freeze_path.read_text()) if freeze_path.exists() else {}
    values = {
        "FusionEvidenceMode": "synthetic",
        "FusionRealNetworkCount": 4,
        "FusionTestThreeInstances": int(stats.loc[0, "n"]),
        "FusionHOneMean": f"{stats.loc[0, 'mean_difference']:.6f}",
        "FusionHTwoMean": f"{stats.loc[1, 'mean_difference']:.6f}",
        "FusionHThreeMean": f"{stats.loc[2, 'mean_difference']:.6f}",
        "FusionHOneP": f"{stats.loc[0, 'p_holm']:.3g}",
        "FusionHTwoP": f"{stats.loc[1, 'p_holm']:.3g}",
        "FusionHThreeP": f"{stats.loc[2, 'p_holm']:.3g}",
        "FusionChosenCovariate": freeze.get("covariate", "pending"),
        "FusionChosenFamily": freeze.get("family", "pending"),
    }
    out = root / "thesis/fusion"
    out.mkdir(parents=True, exist_ok=True)
    (out / "fusion_numbers.tex").write_text(
        "\n".join(rf"\newcommand{{\{k}}}{{{v}}}" for k, v in values.items()) + "\n"
    )


if __name__ == "__main__":
    main()
