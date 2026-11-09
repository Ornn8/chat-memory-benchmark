# -*- coding: utf-8 -*-
"""Three-board leaderboard: short (M01), long (M02) from the 2.1 leaderboard json + the natural-use board from run summaries.

    python -m bench21.natural_report --lb21 PATH/leaderboard-sealed.json --run NR1 --out OUTDIR
Composite = 0.375*S_short + 0.375*S_long + 0.25*S_natural   (weights in score_config.json: board_weights).
Qualification floors (prize condition, not part of S): restraint >= 70%, fabrication <= 5% on the natural board.
"""
import argparse
import json
import os

from . import scoring
from .release import jl

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG = dict(scoring.CONFIG)
W = CFG.get("board_weights", {"short": 0.375, "long": 0.375, "natural": 0.25})
FLOOR_RESTRAINT, FLOOR_FAB = CFG.get("floor_restraint_pct", 70.0), CFG.get("floor_fabrication_pct", 5.0)
BLOCK = "封存集合计(旧+新)"
NATURAL_ONLY = {"never-recall", "always-recall"}


def load_nat(run, system, split="sealed"):
    p = os.path.join(ROOT, "runs", "bench21", run, system, f"natural-{split}", "summary.json")
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lb21", required=True)
    ap.add_argument("--run", required=True)
    ap.add_argument("--systems", default="r3,qwen-base,full-context,bm25-recent6,recent6,none,never-recall,always-recall")
    ap.add_argument("--ref", default="r3")
    ap.add_argument("--out", required=True)
    ap.add_argument("--runs-for", default="", help="system@run overrides, comma list")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    over = dict(t.split("@") for t in a.runs_for.split(",") if t)
    lb = json.load(open(a.lb21, encoding="utf-8"))
    names = a.systems.split(",")
    nat = {s: load_nat(over.get(s, a.run), s) for s in names}
    ref = nat[a.ref]
    c_ref = ref["cost_cny"]["total_C"]
    rows = {}
    for s in names:
        r = {"system": s}
        for key, persona in (("short", "M01"), ("long", "M02")):
            m = lb["boards"][persona]["blocks"][BLOCK]["systems"].get(s)
            r[key] = {"A": m["A_w"], "A_plain": m["A"], "C": m["C"], "S": m["S_w"], "sampled": bool(m.get("sampled"))} if m else None
        n = nat[s]
        if n:
            met = n["metrics"]
            r["natural"] = {"A": met["A_nat"], "A_plain": met["A_nat_plain"], "A_traffic": met["A_nat_traffic"], "C": n["cost_cny"]["total_C"],
                            "S": scoring.composite(met["A_nat"], n["cost_cny"]["total_C"], c_ref), "by_class": met["by_class"],
                            "recall": met["recall_rate"], "restraint": met["restraint_rate"], "fabrication": met["fabrication_rate"],
                            "hedge": met["hedge_pass_rate"], "naturalness": met["naturalness_mean"], "leaks": len(n["leak_flags"]), "contam": n["n_contaminated"]}
            r["qualifies_floor"] = met["restraint_rate"] >= FLOOR_RESTRAINT and met["fabrication_rate"] <= FLOOR_FAB
        else:
            r["natural"] = None
        if r["short"] and r["long"] and r["natural"]:
            r["composite_S"] = W["short"] * r["short"]["S"] + W["long"] * r["long"]["S"] + W["natural"] * r["natural"]["S"]
            r["composite_A"] = W["short"] * r["short"]["A"] + W["long"] * r["long"]["A"] + W["natural"] * r["natural"]["A"]
            r["two_board_S"] = (r["short"]["S"] + r["long"]["S"]) / 2
        rows[s] = r
    out = {"weights": W, "floors": {"restraint_pct": FLOOR_RESTRAINT, "fabrication_pct": FLOOR_FAB}, "C_ref_natural": c_ref,
           "prices_version": json.load(open(os.path.join(ROOT, "bench21", "prices.json"), encoding="utf-8"))["version"], "rows": rows}
    json.dump(out, open(os.path.join(a.out, "leaderboard-three-boards.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    L = [f"# 三榜榜单（封存集；短对话榜 / 长对话榜来自 2.1 榜单，自然用记忆榜 run {a.run}）", "",
         f"综合分 = {W['short']} × S短 + {W['long']} × S长 + {W['natural']} × S自然；自然用记忆榜 C_ref = r3 的 C = ¥{c_ref:.3f}。", "",
         "## 总排名（三榜都有成绩的系统）", "", "| 系统 | 综合 S | 综合 A | 短 A/C/S | 长 A/C/S | 自然 A/C/S | 达标底线(克制≥70%且编造≤5%) |", "|---|---:|---:|---|---|---|---|"]
    f3 = lambda b: "-" if not b else f"{b['A']:.1f} / {b['C']:.3f} / {b['S']:.1f}"
    for s, r in sorted(rows.items(), key=lambda kv: -kv[1].get("composite_S", -1e9)):
        if "composite_S" not in r:
            continue
        L.append(f"| {s}{' (全塞抽样)' if r['short'] and r['short']['sampled'] else ''} | {r['composite_S']:.1f} | {r['composite_A']:.1f} | {f3(r['short'])} | {f3(r['long'])} | {f3(r['natural'])} | {'是' if r['qualifies_floor'] else '否'} |")
    L += ["", "## 自然用记忆榜明细", "", "| 系统 | A | 想起率 | 克制率 | 编造率 | 拿不准通过率 | 自然度(0-2) | C(¥) | S | 泄漏 | 尾巴污染 |", "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for s, r in sorted(rows.items(), key=lambda kv: -(kv[1]["natural"]["S"] if kv[1]["natural"] else -1e9)):
        n = r["natural"]
        if not n:
            continue
        L.append(f"| {s} | {n['A']:.1f} | {n['recall']:.1f} | {n['restraint']:.1f} | {n['fabrication']:.1f} | {n['hedge']:.1f} | {n['naturalness']:.2f} | {n['C']:.3f} | {n['S']:.1f} | {n['leaks']} | {n['contam']} |")
    L += ["", "各类得分（X 该提 / H 拿不准 / Y 不该提 / Z 都行 / N0 无关对照）：", ""]
    for s, r in rows.items():
        if r["natural"]:
            L.append(f"- {s}: " + "，".join(f"{c} {v}" for c, v in sorted(r["natural"]["by_class"].items())))
    open(os.path.join(a.out, "leaderboard-three-boards.md"), "w", encoding="utf-8").write("\n".join(L))
    print("\n".join(L))


if __name__ == "__main__":
    main()
