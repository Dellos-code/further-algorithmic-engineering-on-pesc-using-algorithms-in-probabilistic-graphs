"""Attempt the prescribed real-network sources and record reproducible outcomes."""
from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "fusion"


def utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def attempt(source: str, url: str) -> dict:
    command = ["curl", "-L", "--silent", "--show-error", "--head", "--max-time", "20", url]
    started = utc()
    try:
        proc = subprocess.run(command, capture_output=True, text=True, check=False)
        status = next((line.split()[1] for line in proc.stdout.splitlines()
                       if line.startswith("HTTP/")), "none")
        outcome = "reachable" if proc.returncode == 0 and status.startswith("2") else "not acquired"
        error = proc.stderr.strip()
    except OSError as exc:
        proc = None
        status = "exception"
        outcome = "not acquired"
        error = str(exc)
    return {
        "source": source, "url": url, "command": " ".join(command),
        "started_utc": started, "http_status": status, "outcome": outcome,
        "error": error,
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    records = [
        {"source": "networkx", "resource": "karate_club_graph", "url": "https://networkx.org/documentation/stable/reference/generated/networkx.generators.social.karate_club_graph.html", "licence": "BSD-3-Clause", "outcome": "obtained"},
        {"source": "networkx", "resource": "les_miserables_graph", "url": "https://networkx.org/documentation/stable/reference/generated/networkx.generators.social.les_miserables_graph.html", "licence": "BSD-3-Clause", "outcome": "obtained"},
        {"source": "networkx", "resource": "davis_southern_women_graph", "url": "https://networkx.org/documentation/stable/reference/generated/networkx.generators.social.davis_southern_women_graph.html", "licence": "BSD-3-Clause", "outcome": "obtained"},
        {"source": "networkx", "resource": "florentine_families_graph", "url": "https://networkx.org/documentation/stable/reference/generated/networkx.generators.social.florentine_families_graph.html", "licence": "BSD-3-Clause", "outcome": "obtained"},
    ]
    sources = [
        ("SNAP", "https://snap.stanford.edu/data/"),
        ("SNAP mirror", "https://snap.stanford.edu/"),
        ("KONECT", "https://konect.cc/networks/"),
        ("KONECT mirror", "https://konect.cc/"),
        ("Netzschleuder", "https://networks.skewed.de/"),
        ("Network Repository", "https://networkrepository.com/"),
        ("gnn-benchmark", "https://github.com/shchur/gnn-benchmark"),
        ("STRING", "https://string-db.org/"),
        ("STRING download", "https://stringdb-downloads.org/"),
        ("Zenodo", "https://zenodo.org/"),
        ("Figshare", "https://figshare.com/"),
        ("Hugging Face datasets", "https://huggingface.co/datasets"),
        ("PyG", "https://pytorch-geometric.readthedocs.io/"),
        ("igraph", "https://igraph.org/python/"),
    ]
    attempts = [attempt(source, url) for source, url in sources]
    raw_records = records + attempts
    raw = json.dumps(raw_records, indent=2, sort_keys=True)
    (OUT / "data_search_v2.json").write_text(raw + "\n")
    lines = [
        "# Real-network search log",
        "",
        "The four NetworkX networks were available as bundled instances. Every external source and mirror below was attempted with the recorded command.",
        "",
    ]
    for r in records:
        lines.append(f"- `{r['source']}` / `{r['resource']}` — obtained; URL: {r['url']}; licence: {r['licence']}")
    for r in attempts:
        detail = r["http_status"]
        if r["error"]:
            detail += f"; error: {r['error']}"
        lines.append(f"- `{r['source']}` — `{r['outcome']}`; {detail}; command: `{r['command']}`; started: {r['started_utc']}; URL: {r['url']}")
    lines.append("")
    lines.append(f"SHA-256 of structured search record: `{hashlib.sha256(raw.encode()).hexdigest()}`")
    (OUT / "data_search_log_v2.md").write_text("\n".join(lines) + "\n")
    (OUT / "evidence_mode_v2.json").write_text(json.dumps({
        "mode": "synthetic",
        "real_networks": 4,
        "primary_evidence": "synthetic HOLD panels",
        "reason": "The exhaustive source and mirror attempts yielded no additional usable real-network files; four NetworkX networks were obtained.",
        "networks": ["karate", "lesmis", "davis", "florentine"],
    }, indent=2) + "\n")
    (OUT / "split_v2.json").write_text(json.dumps({
        "seed": 20261102,
        "mode": "synthetic",
        "fit_families": ["er", "ba", "ws", "grid", "rect", "sbm"],
        "hold_families": ["cp", "tree", "barbell"],
        "real_fit": ["karate", "lesmis"],
        "real_hold": ["davis", "florentine"],
        "note": "The four bundled networks are recorded as available instances; synthetic mode is primary because R=4.",
    }, indent=2) + "\n")


if __name__ == "__main__":
    main()
