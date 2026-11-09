# -*- coding: utf-8 -*-
"""Assemble the natural-use board files from generated cards:
   natural-probes.jsonl  (exam view: tail + probe/script, no card)      -> given to systems / published for dev
   natural-key.jsonl     (private card: target/forbidden/decoys/...)    -> sealed items published as SHA only
"""
import argparse
import datetime
import hashlib
import json
import os
import random

from .release import jl, load_histories
from .natural_gen import evidence_block, make_times, day_of

DEV_PICK = {"X": [2, 7, 12, 17, 22, 27], "H": [2, 7], "Y": [2, 7, 12, 17, 22], "Z": [2, 7], "N0": [2, 7]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--release", required=True)
    ap.add_argument("--cases-dir", required=True)
    ap.add_argument("--cards", nargs="+", required=True, help="cards-raw.jsonl files, later ones override earlier by slot id; redo files add new slots")
    ap.add_argument("--drop", default="", help="comma list of slot ids to drop (failed ones that were replaced)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=20261109)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    hist = load_histories(a.release)
    cases = {}
    for p in ("M01", "M02"):
        for c in jl(os.path.join(a.cases_dir, f"cases-{p}.jsonl")):
            cases[c["case_id"]] = c
    drop = set(a.drop.split(",")) if a.drop else set()
    rows = {}
    for path in a.cards:
        for r in jl(path):
            if r["errors"] or not r["card"]:
                continue
            rows[r["spec"]["id"] + ("#" + r["spec"]["subtype"] if path != a.cards[0] else "")] = r
    rows = {k: v for k, v in rows.items() if k.split("#")[0] not in drop or "#" in k}
    items = list(rows.values())
    # stable final ids
    per = {}
    probes, keys = [], []
    for r in sorted(items, key=lambda r: (r["spec"]["persona"], r["spec"]["subtype"], r["spec"]["idx"], r["spec"]["id"])):
        spec, card = r["spec"], r["card"]
        persona, sub = spec["persona"], spec["subtype"]
        per[(persona, sub)] = per.get((persona, sub), 0) + 1
        pid = f"NAT-{persona}-{sub}-{per[(persona, sub)]:02d}"
        H = hist[persona]
        T = spec["cutoff_turn"]
        rnd0 = random.Random(f"{a.seed}:{spec['id']}")
        sp0 = dict(spec)
        base_now = spec.get("now") or make_times(sp0, H, rnd0, 1, persona)[0]
        rt = random.Random(f"{a.seed}:{pid}:times")
        tier = spec["tier"]
        n_user = (len(card.get("tail") or []) + 1) if tier == "A" else len(card["script"])
        if spec.get("now") and spec["subtype"] == "X4":
            end = datetime.datetime.fromisoformat(spec["now"])
            gaps = [rt.randint(1, 4) if persona == "M01" else rt.randint(8, 25) for _ in range(n_user - 1)]
            times, cur = [end.isoformat(timespec="seconds")], end
            for g in gaps:
                cur = cur - datetime.timedelta(minutes=g)
                times.insert(0, cur.isoformat(timespec="seconds"))
        else:
            cur = datetime.datetime.fromisoformat(base_now)
            times = []
            for _ in range(n_user):
                times.append(cur.isoformat(timespec="seconds"))
                cur = cur + datetime.timedelta(minutes=rt.randint(1, 4) if persona == "M01" else rt.randint(8, 25))
        p = {"id": pid, "persona": persona, "tier": tier, "cutoff_turn": T, "history_file": f"histories/{persona}.jsonl"}
        if tier == "A":
            p["tail"] = [{"user": t["user"], "assistant": t["assistant"], "time": times[i]} for i, t in enumerate(card.get("tail") or [])]
            p["probe"] = {"user": card["probe"], "time": times[-1]}
        else:
            p["script"] = [{"user": u, "time": times[i]} for i, u in enumerate(card["script"])]
        case = cases.get(spec.get("case_id")) if spec.get("case_id") else None
        ev = facts = ""
        first_gap = None
        if case:
            evb, facts, _ver, _unk = evidence_block(case, T, H)
            ev = evb + "\n" + facts
            tt = [s["turn"] for s in case["sources"] if s["turn"] <= T]
            if tt:
                first_gap = (day_of(times[-1]) - day_of(H[min(tt) - 1]["time"])).days
        if spec.get("fact_override"):
            ev = ev + "\n补充：" + spec["fact_override"]
        k = {"id": pid, "persona": persona, "class": spec["class"], "subtype": sub, "tier": tier, "severity": card.get("severity") or "普通",
             "emotion": spec["emotion"], "gap_days_last": spec.get("gap_days"), "gap_days_first": first_gap, "gap_bucket": spec.get("bucket"),
             "case_id": spec.get("case_id"), "source_slot": spec["id"], "target": card.get("target"), "forbidden": card.get("forbidden"),
             "ok_instead": card.get("ok_instead"), "decoys": card.get("decoys") or [], "terms_absent": card.get("terms_absent") or [],
             "evidence": ev, "reference_reply": card.get("reference_reply"), "not_due": spec.get("not_due", False),
             "source_row": spec.get("source_row")}
        probes.append(p)
        keys.append(k)
    # split
    grp = {}
    for p, k in zip(probes, keys):
        grp.setdefault((k["persona"], k["class"]), []).append(p)
    for (persona, cls), ps in grp.items():
        ps.sort(key=lambda p: p["id"])
        picks = set(DEV_PICK[cls])
        for i, p in enumerate(ps):
            p["split"] = "dev" if i in picks else "sealed"
    with open(os.path.join(a.out, "natural-probes.jsonl"), "w", encoding="utf-8") as f:
        for p in probes:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
    with open(os.path.join(a.out, "natural-key.jsonl"), "w", encoding="utf-8") as f:
        for k in keys:
            f.write(json.dumps(k, ensure_ascii=False) + "\n")
    import collections
    print(len(probes), collections.Counter((p["persona"], p["split"]) for p in probes), collections.Counter(k["class"] for k in keys),
          collections.Counter(p["tier"] for p in probes))


if __name__ == "__main__":
    main()
