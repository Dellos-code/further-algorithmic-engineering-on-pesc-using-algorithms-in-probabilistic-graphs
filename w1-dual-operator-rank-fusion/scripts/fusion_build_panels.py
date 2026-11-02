"""Build fresh synthetic panels after the freeze."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from w1.instances import FAMILIES, ground_truth, make_synthetic


def specs(panel):
    fams = FAMILIES if panel == "test3" else ["er", "ba", "grid", "ws", "sbm"]
    sizes = [100] if panel == "test3" else ([900] if panel == "scale3" else [2000, 5000])
    reps = [6, 7] if panel == "test3" else [2]
    return [(fam, n, pr, prior, rep) for fam in fams for n in sizes
            for pr in ("R1", "R2", "R3", "R4", "R5")
            for prior in (("uniform", "dir1") if panel == "test3" else ("uniform",))
            for rep in reps]


def main(panel):
    root = Path(__file__).resolve().parents[1]
    out = root / "data" / panel
    out.mkdir(parents=True, exist_ok=True)
    entries = []
    for i, (fam, n, pr, prior, rep) in enumerate(specs(panel)):
        inst = make_synthetic(fam, n, pr, prior, rep, panel=panel)
        gt = ground_truth(inst)
        meta = dict(inst.meta, name=inst.name)
        np.savez_compressed(out / f"{i:04d}.npz", edges=inst.edges, p=inst.p, x=inst.x,
                            yA=gt["yA"], yB=gt["yB"], yA2=gt["yA2"],
                            meta=json.dumps(meta, sort_keys=True))
        entries.append(dict(kind="syn", fam=fam, n=n, pr=pr, prior=prior, rep=rep, panel=panel))
    (out / "specs.json").write_text(json.dumps(entries, indent=2) + "\n")
    print(f"{panel}: {len(entries)} instances")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("panel", choices=("test3", "scale3", "big2"))
    main(ap.parse_args().panel)
