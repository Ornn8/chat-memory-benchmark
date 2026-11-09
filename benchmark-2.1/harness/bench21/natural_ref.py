# -*- coding: utf-8 -*-
"""Ceiling check: score the card author's reference reply for every tier-A probe with the same judge (system name 'reference')."""
import json, os, sys
from .natural import load_natural, ROOT
from .release import jl

def main():
    natdir, run, split = sys.argv[1], sys.argv[2], sys.argv[3]
    probes, key = load_natural(natdir, split)
    out = os.path.join(ROOT, "runs", "bench21", run, "reference", "natural-" + split)
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "turns.jsonl"), "w", encoding="utf-8") as f:
        for p in probes:
            if p["tier"] != "A":
                continue
            r = {"id": p["id"], "k": 0, "persona": p["persona"], "cutoff_turn": p["cutoff_turn"], "visible_until": p["cutoff_turn"] + len(p.get("tail") or []),
                 "prompt": "", "used_turns": [], "leak_turns_after_visible": [], "meta": {}, "user": p["probe"]["user"], "time": p["probe"]["time"],
                 "answer": key[p["id"]]["reference_reply"] or "", "prompt_tokens": 0, "completion_tokens": 0, "mem_tokens": 0, "prompt_sha256": ""}
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
main()
