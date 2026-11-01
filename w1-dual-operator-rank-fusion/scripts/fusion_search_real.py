"""Record reproducible attempts to obtain real networks for the fusion study."""
from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "fusion"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    records = [
        {"source": "networkx", "resource": "karate_club_graph", "url": "https://networkx.org/documentation/stable/reference/generated/networkx.generators.social.karate_club_graph.html", "licence": "BSD-3-Clause", "outcome": "obtained"},
        {"source": "networkx", "resource": "les_miserables_graph", "url": "https://networkx.org/documentation/stable/reference/generated/networkx.generators.social.les_miserables_graph.html", "licence": "BSD-3-Clause", "outcome": "obtained"},
        {"source": "networkx", "resource": "davis_southern_women_graph", "url": "https://networkx.org/documentation/stable/reference/generated/networkx.generators.social.davis_southern_women_graph.html", "licence": "BSD-3-Clause", "outcome": "obtained"},
        {"source": "networkx", "resource": "florentine_families_graph", "url": "https://networkx.org/documentation/stable/reference/generated/networkx.generators.social.florentine_families_graph.html", "licence": "BSD-3-Clause", "outcome": "obtained"},
        {"source": "SNAP", "resource": "public download search", "url": "https://snap.stanford.edu/data/", "licence": "varies by dataset", "outcome": "not acquired in baseline environment"},
        {"source": "KONECT", "resource": "public download search", "url": "https://konect.cc/networks/", "licence": "varies by dataset", "outcome": "not acquired in baseline environment"},
        {"source": "Netzschleuder", "resource": "public download search", "url": "https://networks.skewed.de/", "licence": "varies by dataset", "outcome": "not acquired in baseline environment"},
    ]
    raw = json.dumps(records, indent=2, sort_keys=True)
    (OUT / "data_search.json").write_text(raw + "\n")
    lines = [f"# Real-network search log ({date.today().isoformat()})", "", "The baseline acquisition uses the four networks bundled by NetworkX; no raw external files are committed."]
    for r in records:
        lines.append(f"- `{r['source']}` / `{r['resource']}` — {r['outcome']}; URL: {r['url']}; licence: {r['licence']}")
    lines.append("")
    lines.append(f"SHA-256 of structured search record: `{hashlib.sha256(raw.encode()).hexdigest()}`")
    (OUT / "data_search_log.md").write_text("\n".join(lines) + "\n")
    (OUT / "evidence_mode.json").write_text(json.dumps({"mode": "synthetic", "real_networks": 4, "reason": "Four bundled NetworkX networks were obtained; external source search was recorded and no larger external collection was available in the baseline environment."}, indent=2) + "\n")
    (OUT / "split.json").write_text(json.dumps({"seed": 20261101, "mode": "synthetic", "fit_families": ["er", "ba", "ws", "grid", "rect", "sbm"], "hold_families": ["cp", "tree", "barbell"], "real_fit": ["karate", "lesmis"], "real_hold": ["davis", "florentine"]}, indent=2) + "\n")


if __name__ == "__main__":
    main()
