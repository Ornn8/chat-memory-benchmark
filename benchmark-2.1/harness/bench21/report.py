# -*- coding: utf-8 -*-
"""Leaderboard from run directories: A (weighted + unweighted), C (CNY), S per board, paired score, leak flags.

    python -m bench21.report --release DIR --run R21c --out OUTDIR
"""
import argparse, collections, json, math, os
from . import scoring
from .release import jl, load_items, board_name
from .gateway import PRICES, price_cny, _priced

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIN = PRICES["models"]["deepseek-v4.1-flash"]["in_per_mtok"]


def reprice(r):
    """Cost of a ledger row under the CURRENT price table, from the recorded token counts."""
    return price_cny(_priced(r["model"]), r.get("in_tokens", 0), r.get("out_tokens", 0))


def load_run(run, system, split):
    d = os.path.join(ROOT, "runs", "bench21", run, system, split)
    if not os.path.exists(os.path.join(d, "summary.json")):
        return None
    g = lambda n: jl(os.path.join(d, n)) if os.path.exists(os.path.join(d, n)) else []
    return {"dir": d, "ctx": {r["id"]: r for r in g("contexts.jsonl")}, "ans": {r["id"]: r for r in g("answers.jsonl")},
            "jud": {r["id"]: r for r in g("judgments.jsonl")}, "summary": json.load(open(os.path.join(d, "summary.json"), encoding="utf-8")),
            "unav": {r["id"] for r in g("unavailable.jsonl")}}


def ledger_costs(run, system, persona, split):
    key = f"{system}:{persona}:{split}"
    ing = ret = 0.0
    for r in jl(os.path.join(ROOT, "runs", "bench21", "spend-ledger.jsonl")):
        if r.get("run") == run and r.get("system") == key:
            c = reprice(r)
            if r["phase"] == "ingest":
                ing += c
            elif r["phase"] == "retrieve":
                ret += c
    return ing, ret


def metrics(items, run, rd, system, persona, split, common, n_run):
    """A and C on the common item set of one board."""
    passed = {i: v["pass"] for i, v in rd["jud"].items()}
    its = [it for it in items if it["id"] in common and it.get("kind") == "main" and it["id"] in rd["jud"]]
    ing, ret = ledger_costs(run, system, persona, split)
    nq = max(1, n_run)
    ratio = (sum(a["mem_tokens"] for a in rd["ans"].values()) / max(1, sum(len(rd["ctx"][i]["prompt"]) for i in rd["ans"]))) if rd["ans"] else 0.7
    mem = sum(rd["ans"][i]["mem_tokens"] if i in rd["ans"] else ratio * len(rd["ctx"][i]["prompt"]) for i in common if i in rd["ctx"])
    c = ing + ret * (len(common) / nq) + mem * FIN / 1e6
    pr, npairs = scoring.paired_rate([it for it in items if it["id"] in common and it["id"] in rd["jud"]], passed)
    return {"n": len(its), "A": scoring.rate(its, passed), "A_w": scoring.weighted_rate(its, passed), "C": c,
            "C_parts": {"ingest": ing, "retrieve": ret * (len(common) / nq), "memory_in_prompt": mem * FIN / 1e6},
            "paired": pr, "n_pairs": npairs, "mean_points": (sum(rd["jud"][it["id"]]["points"] for it in its) / len(its)) if its else None}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--release", required=True)
    ap.add_argument("--run", required=True)
    ap.add_argument("--split", default="sealed")
    ap.add_argument("--systems", default="qwen-base,full-context,bm25-recent6,recent6,none")
    ap.add_argument("--ref", default="qwen-base")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    want = "test" if a.split == "sealed" else "dev"
    items = [i for i in load_items(a.release) if i.get("split") == want]
    runof = {}
    for tok in a.systems.split(","):               # "system" or "system@run" (a leaderboard may mix runs)
        n, _, rn = tok.partition("@")
        runof[n] = rn or a.run
    systems = {s: load_run(runof[s], s, a.split) for s in runof}
    systems = {s: r for s, r in systems.items() if r}
    out = {"run": a.run, "split": a.split, "score_config": scoring.CONFIG, "prices_version": PRICES["version"], "boards": {}}
    for persona in ("M01", "M02"):
        pit = [i for i in items if i["persona"] == persona]
        legacy = {i["id"] for i in pit if i.get("probe_type") in (None, "legacy")}
        new = {i["id"] for i in pit if i.get("probe_type") not in (None, "legacy")}
        blocks = {}
        for bname, ids in (("封存集合计(旧+新)", legacy | new), ("2.0题(含改写)", legacy), ("2.1新题", new)):
            sysm = {s: r for s, r in systems.items() if any(i in r["jud"] for i in ids)}
            # common set: items every participating system actually scored (retrieval available)
            common = set(ids)
            for s, r in sysm.items():
                common &= set(r["jud"]) | ({i for i in ids if i in r["ctx"] and r is systems.get("full-context")})
            for s in list(sysm):
                if not (set(sysm[s]["jud"]) & common):
                    sysm.pop(s)
            if not sysm or not common:
                continue
            rows = {}
            for s, r in sysm.items():
                n_run = len([i for i in r["ctx"] if i in ids])
                rows[s] = metrics(pit, runof[s], r, s, persona, a.split, common if s != "full-context" else common & set(r["jud"]), n_run)
                if s == "full-context":                      # answered on a sample only: C over the whole common set
                    full = metrics(pit, runof[s], r, s, persona, a.split, common, n_run)
                    rows[s]["C"], rows[s]["C_parts"] = full["C"], full["C_parts"]
                    rows[s]["sampled"] = True
            ref = rows.get(a.ref)
            for s, m in rows.items():
                if ref:
                    m["S_w"] = scoring.composite(m["A_w"], m["C"], ref["C"])
                    m["S"] = scoring.composite(m["A"], m["C"], ref["C"])
            blocks[bname] = {"n_common_items": len(common), "systems": rows, "C_ref": ref["C"] if ref else None}
        out["boards"][persona] = {"board": board_name(persona), "blocks": blocks}
    json.dump(out, open(os.path.join(a.out, f"leaderboard-{a.split}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    # markdown
    L = [f"# 榜单（{a.split}，run {a.run}，价目表 {PRICES['version']}）", ""]
    for persona, b in out["boards"].items():
        for bname, blk in b["blocks"].items():
            L += [f"## {b['board']} · {bname}（共同题数 {blk['n_common_items']}，C_ref = {a.ref} 的 C = ¥{blk['C_ref']:.3f}）" if blk["C_ref"] else f"## {b['board']} · {bname}", "",
                  "| 系统 | 题数 | A 加权(%) | A 不加权(%) | C(¥) | S | 成对通过(%) |", "|---|---:|---:|---:|---:|---:|---:|"]
            for s, m in sorted(blk["systems"].items(), key=lambda kv: -kv[1].get("S_w", kv[1]["A_w"])):
                L.append(f"| {s}{' (抽样答题)' if m.get('sampled') else ''} | {m['n']} | {m['A_w']:.1f} | {m['A']:.1f} | {m['C']:.3f} | {m.get('S_w', float('nan')):.1f} | {'-' if m['paired'] is None else format(m['paired'], '.0f')} |")
            L.append("")
    open(os.path.join(a.out, f"leaderboard-{a.split}.md"), "w", encoding="utf-8").write("\n".join(L))
    print("\n".join(L))


if __name__ == "__main__":
    main()
