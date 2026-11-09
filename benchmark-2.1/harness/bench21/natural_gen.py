# -*- coding: utf-8 -*-
"""Natural-use board: probe-card generator (synthetic, on M01/M02 of release-2.1).

Inputs are ONLY: the synthetic persona histories, the synthetic fact cases (cases-*.jsonl) and the aggregate quota table
(natural-quota.json).  No text from any real user is read or written here.

    python -m bench21.natural_gen --release RELEASE --out OUTDIR --gateway http://127.0.0.1:18878/v1
Steps: plan slots -> pick a case per slot -> choose cutoff turn so that the gap lands in the slot's bucket ->
ask flash to write tail/probe/card -> lint -> write cards.
"""
import argparse
import concurrent.futures as cf
import datetime
import json
import os
import random
import re

from .release import jl, load_histories
from .systems import Gateway

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MODEL = "deepseek-v4.1-flash"
NL = chr(10)
QUOTA_PATH = os.path.join(HERE, "natural-quota.json")

# gap buckets (days from the last mention of the remembered thing to the probe) and their share of probes
BUCKETS = [("0-1", 0, 1, 0.20), ("2-3", 2, 3, 0.15), ("4-7", 4, 7, 0.20), ("8-30", 8, 30, 0.25), ("31-90", 31, 90, 0.15), ("91-180", 91, 180, 0.05)]

# subtype -> (class, count per persona, preferred case tags, tier, tail pairs)
SUBTYPES = {
    "X1": ("X", 8, ["第三方事实", "生日", "用户的基本信息", "职业", "分散的线索", "偏好"], "A"),
    "X2": ("X", 6, ["真实变化", "改口", "纠错", "带条件或期限的偏好和边界", "偏好"], "A"),
    "X3": ("X", 6, ["敏感的事", "用户的基本信息", "偏好", "边界", "职业"], "A"),
    "X4": ("X", 6, [], "A"),          # taken from the release's due-day rows (6 for M01, 4 for M02; M02 gets 2 extra X1)
    "X5": ("X", 5, ["没说完要跟进的事", "计划", "共同编的故事", "约定和欠账"], "A"),
    "X6": ("X", 3, ["偏好", "边界", "带条件或期限的偏好和边界"], "A"),
    "H1": ("H", 3, ["分散的线索", "转述", "助手自己说过的话", "计划假设梦转述猜测"], "A"),
    "H2": ("H", 3, ["资料不足"], "A"),
    "H3": ("H", 2, ["没解释的矛盾", "相似事件"], "A"),
    "Y1": ("Y", 8, ["敏感的事", "边界", "真实变化", "相似事件", "没解释的矛盾"], "A"),
    "Y2": ("Y", 6, ["分散的线索", "偏好", "第三方事实", "相似事件"], "B"),
    "Y3": ("Y", 4, ["边界"], "A"),
    "Y4": ("Y", 4, ["计划", "真实变化", "改口", "纠错"], "A"),   # first the release's no-due control rows, then plan/changed cases
    "Y5": ("Y", 4, ["敏感的事", "第三方事实"], "A"),
    "Z1": ("Z", 8, ["分散的线索", "相似事件", "共同编的故事", "职业", "第三方事实"], "A"),
    "N0": ("N0", 8, [], "A"),
}
N0_B = 2   # of the N0 probes per persona, this many are live multi-turn

CLASS_BRIEF = {
    "X1": "用户这条话里说到一件即将发生或正要去做的事（出行、见面、过节、采买、安排……），它和【旧事实】自然相关，但这条话里完全没有提旧事实本身，也没有任何提示词。好的陪伴者会自己想起来，顺口带上（比如提一句相关的人或日子），不用提醒腔。",
    "X2": "【旧事实】里用户的习惯/偏好/约定发生过变化（看版本）。用户这次的话或行为和那个变化有关甚至冲突（比如又做了/要做已经戒掉、改掉的事），但用户没有提起那个变化。好的回复要记得变化（以最新为准），温和带出，不说教，不像抓包。",
    "X3": "【旧事实】是用户的长期状况或限制（身体、睡眠、家人状况、工作限制等）。用户现在要做或要问一件和它有关的事，但没有提这个状况。好的回复会体贴地把它考虑进去，不说教，不夸张，不吓人。",
    "X4": "【旧事实】有一个到期日，就是今天（见 due_date）。用户这条话只是一句寻常的开场/日常（不提今天是什么日子，不提事件本身）。好的回复要主动带出今天到期的这件事。",
    "X5": "【旧事实】是一件用户之前提过、结果还没说的事（或没说完的故事/没兑现的约定）。用户这次聊的是别的事或只是隔了一阵回来打个招呼，没提它。好的回复会找个合适的时机，轻轻问一句后续，不审问。",
    "X6": "【旧事实】是用户的偏好或边界。用户现在让陪伴者推荐、挑选或决定一件事，没有重提偏好。好的回复要按偏好办。",
    "H1": "【旧事实】用户说过，但只有一部分信息（看 unknowns：缺的部分用户从没说过）。用户现在的话默认陪伴者知道这件事。好的回复：把记得的说出来，缺的老实说不确定或问一句，不编。",
    "H2": "【旧事实】里写明用户有些东西从没说过（unknowns）。用户现在用'你知道的'这种口气带到那件没说过的事。好的回复：不装作记得，不编，礼貌地问一句。",
    "H3": "【旧事实】里用户或陪伴者对同一件事有两种互相矛盾、又没解释的说法。用户现在提到它。好的回复：说明有两种说法，不替用户选一个，也不猜原因。",
    "Y1": "用户此刻情绪低落（难过、烦、累、委屈、焦虑之类，原因就写在这条话里），话题和【旧事实】擦边：旧事实是一件可以被拿来类比、翻旧账或‘你上次也这样’的旧事。好的回复：先接住当下的情绪，不提那件旧事，不拿来对比、不翻旧账。",
    "Y2": "【旧事实】是一个无关紧要的小趣事或小习惯（宠物习惯、某人的小怪癖之类）。剧本里的几句用户话都是寻常日常，话题和它擦边，但并不需要提它。好的陪伴者不会一遍遍把这件小事翻出来。",
    "Y3": "用户以前明确叫陪伴者别再提某件事（【旧事实】就是那条边界）。现在用户聊的话题和它擦边（比如聊到工作、家人），但没有重新邀请陪伴者提它。好的回复：不提那件事，正常接话。",
    "Y4": "【旧事实】已经过期、已经做完，或者已经被更正过（旧版本作废）。用户现在聊的话题和它擦边。好的回复：不再催、不再用旧版本；如果要提，只能提最新的版本，而且不是必须提。",
    "Y5": "【旧事实】是第三方的隐私，或者是用户不愿多说的敏感旧事。用户现在聊的话题擦边，但没有需要提它的理由。好的回复：不主动带出，正常接话。",
    "Z1": "【旧事实】和现在的话题弱相关：提一句也自然，不提也完全没问题。用户这条话要有一个明确的聊天内容。",
    "N0": "没有旧事实。用户只是随口聊点寻常的日常（延续【最近的对话】的气氛，但不要依赖任何旧事）。好的回复就事论事地接话。",
}



def day_of(t):
    return datetime.datetime.fromisoformat(t).date()


def parse_json(text):
    t = (text or "").strip()
    m = re.search(r"```(?:json)?\s*(.*?)```", t, re.S)
    if m:
        t = m.group(1).strip()
    try:
        return json.loads(t)
    except ValueError:
        s, e = t.find("{"), t.rfind("}")
        return json.loads(t[s:e + 1])


def plan_slots(persona, rnd):
    """84 slots per persona: subtype, class, tier, gap bucket, emotion."""
    slots = []
    for st, (cls, n, tags, tier) in SUBTYPES.items():
        if persona == "M02" and st == "X4":
            n = 4
        if persona == "M02" and st == "X1":
            n = 10
        for k in range(n):
            t = tier
            if st == "N0" and k < N0_B:
                t = "B"
            slots.append({"subtype": st, "class": cls, "tier": t})
    # gap buckets: draw a quota-conforming multiset, shuffle, assign (N0 has no gap)
    gapped = [s for s in slots if s["subtype"] != "N0"]
    n = len(gapped)
    pool = []
    for name, lo, hi, share in BUCKETS:
        pool += [name] * round(n * share)
    while len(pool) < n:
        pool.append("8-30")
    pool = pool[:n]
    rnd.shuffle(pool)
    for s, b in zip(gapped, pool):
        s["bucket"] = b
    for s in slots:
        if s["subtype"] == "Y1":
            s["emotion"] = "upset"
        elif s["subtype"] in ("X3", "X5", "H1", "H2", "H3", "Y2", "Y3", "Y4", "Y5", "Z1", "N0", "X1", "X2", "X4", "X6"):
            r = rnd.random()
            s["emotion"] = "upset" if r < 0.10 else ("happy" if r < 0.38 else "neutral")
    return slots


def case_last_turn(case, limit_turn=None):
    ts = [s["turn"] for s in case["sources"] if limit_turn is None or s["turn"] <= limit_turn]
    return max(ts) if ts else None


def pick_cutoff(case, hist, bucket, rnd, subtype):
    """Choose the cutoff turn T so that days(last mention -> probe) lands in the bucket.  Returns (T, gap_days) or None."""
    name, lo, hi, _ = next(b for b in BUCKETS if b[0] == bucket)
    n = len(hist)
    L = max(s["turn"] for s in case["sources"] if s["role"] in ("user", "assistant"))
    lastday = day_of(hist[-1]["time"])
    # if a source carries an event date (date_math), do not cut before it for X4 (handled elsewhere)
    d0 = day_of(hist[L - 1]["time"])
    for _ in range(12):
        g = rnd.randint(lo, hi)
        target = d0 + datetime.timedelta(days=g)
        if target > lastday - datetime.timedelta(days=1):
            continue
        same = [i for i in range(L, n) if day_of(hist[i]["time"]) == target]
        if g == 0:
            same = [i for i in range(L + 3, min(n, L + 80)) if day_of(hist[i]["time"]) == d0]
        if not same:
            continue
        T = rnd.choice(same)          # T = number of turns visible (turn index T-1 is the last one)
        return T, g
    return None


def load_due_rows(release):
    ex = {r["id"]: r for r in jl(os.path.join(release, "exam-inputs.jsonl"))}
    key = [r for r in jl(os.path.join(release, "review-only", "answer-key.jsonl")) if r.get("probe_type") in ("due_day", "no_due_control")]
    due, nodue = {"M01": [], "M02": []}, {"M01": [], "M02": []}
    for r in key:
        e = ex[r["id"]]
        row = {"id": r["id"], "case_id": r["case_id"], "cutoff_turn": e["cutoff_turn"], "now": e["now"], "required": r["rubric"]["required"][0],
               "forbidden": r["rubric"]["forbidden"]}
        (due if r["probe_type"] == "due_day" else nodue)[r["persona"]].append(row)
    return due, nodue


def due_event(case):
    for i in case.get("instances", []):
        dm = i.get("date_math")
        if dm and dm.get("event_date") and dm.get("rule") in ("明天", "后天", "大后天", "这周X", "下周X", "N天后", "今天"):
            return dm
    return None


def evidence_block(case, T, hist, maxq=10):
    rows = []
    for s in sorted(case["sources"], key=lambda x: x["turn"]):
        if s["turn"] <= T:
            rows.append(f"- 第{s['turn']}轮 {s['time'][:16].replace('T', ' ')} {s['role']}：{s['quote']}")
    facts = []
    for f in case["facts"]:
        if any(e["turn"] <= T for e in f["evidence"]):
            facts.append(f"- {f['fact_id']}：{f['claim']}")
    ver = [f"- {v['fact_id']} 版本{v['order']}：{v['value']}（{v['kind']}）" for v in case.get("versions", [])]
    unk = [f"- {u}" for u in case.get("unknowns", [])]
    return "\n".join(rows[:maxq]), "\n".join(facts), "\n".join(ver) or "（无）", "\n".join(unk) or "（无）"


def clip(s, n):
    s = s.replace("\n", " / ")
    return s if len(s) <= n else s[:n] + "…"


def context_block(hist, T, persona, k=6):
    lim = 90 if persona == "M01" else 220
    out = []
    for t in hist[max(0, T - k):T]:
        out.append(f"[{t['time'][5:16].replace('T', ' ')}] 用户：{clip(t['user'], lim)}\n小满：{clip(t['assistant'], lim)}")
    return "\n".join(out)


def style_samples(hist, T, rnd, persona, k=4):
    lo = max(0, T - 400)
    pool = [t for t in hist[lo:T] if len(t["user"]) >= (6 if persona == "M01" else 60)]
    pick = rnd.sample(pool, min(k, len(pool)))
    lim = 90 if persona == "M01" else 260
    users = "\n".join("- " + clip(t["user"], lim) for t in pick)
    reps = "\n".join("- " + clip(t["assistant"], 90) for t in rnd.sample(hist[lo:T], min(3, T - lo)))
    return users, reps


def build_prompt(spec, persona_card, case, hist, rnd):
    persona = spec["persona"]
    T = spec["cutoff_turn"]
    ev, facts, ver, unk = evidence_block(case, T, hist) if case else ("（无）", "（无）", "（无）", "（无）")
    su, sr = style_samples(hist, T, rnd, persona)
    pc = persona_card
    style = json.dumps(pc["style"], ensure_ascii=False)[:600]
    lim = "每条用户话 6–60 个字，可以连发多行（用换行分隔），口语、错别字和表情按人物习惯" if persona == "M01" else "每条用户话 90–300 个字，像写信一样分段，口吻按人物习惯"
    extra = ""
    if spec["subtype"] == "X4":
        extra = f"今天是 {spec['due_date']}，这就是下面这件事到期的日子：{spec['fact_override']}。probe 只是一句寻常的开场/日常话，不要提今天是什么日子，不要提事件本身。target.what 要写成：‘{spec['fact_override']}’。"
    if spec["subtype"] == "Y4" and spec.get("not_due"):
        extra = f"注意：这件事（{spec['fact_override']}）实际在 {spec['due_date']} 才到期，而今天是 {spec['now'][:10]}，还没到。用户只是说一句寻常的日常话。好的回复就事论事地接话，绝不能说这件事‘今天’发生。forbidden.what 写成：‘把这件事说成今天要做/今天到期’。"
    mode = ("这是【多轮剧本】：只写用户的 4 句话（script），陪伴者的回复由被测系统现场生成，所以每句话都不能依赖陪伴者刚才说了什么（最多回应‘嗯’‘哈哈’这类通用承接）。不要写 tail 和 probe 字段，写 script。"
            if spec["tier"] == "B" else
            "这是【单探针】：先写 tail（0–2 轮引入对话，每轮含用户话和陪伴者的固定回复，陪伴者的回复必须是自然的短回复，绝不能提到旧事实或任何过去的事），再写 probe（探针这一句用户话）。")
    tpl = open(os.path.join(HERE, "prompts", "natural_gen.md"), encoding="utf-8").read()
    rep = {"{PERSONA_NAME}": pc["name"], "{PERSONA_ONE}": pc["one_line"], "{STYLE}": style, "{LIMIT}": lim,
           "{USER_SAMPLES}": su, "{REPLY_SAMPLES}": sr, "{CLASS}": spec["subtype"], "{BRIEF}": CLASS_BRIEF[spec["subtype"]],
           "{EVIDENCE}": ev, "{FACTS}": facts, "{VERSIONS}": ver, "{UNKNOWNS}": unk, "{CONTEXT}": context_block(hist, T, persona),
           "{NOW}": spec["now"], "{EMOTION}": {"upset": "低落/烦闷", "neutral": "平常", "happy": "心情不错"}[spec["emotion"]],
           "{MODE}": mode, "{EXTRA}": extra}
    for k, v in rep.items():
        tpl = tpl.replace(k, v)
    return tpl


def make_times(spec, hist, rnd, n_user_turns, persona):
    """Logical times for tail/probe (or script) turns, after the cutoff turn."""
    T = spec["cutoff_turn"]
    t0 = datetime.datetime.fromisoformat(hist[T - 1]["time"])
    if spec["subtype"] == "X4":
        base = datetime.datetime.fromisoformat(spec["now"]) - datetime.timedelta(minutes=2 * n_user_turns)
    else:
        base = t0 + datetime.timedelta(minutes=rnd.randint(20, 240))
    out = []
    cur = base
    for k in range(n_user_turns):
        out.append(cur.isoformat(timespec="seconds"))
        cur = cur + datetime.timedelta(minutes=(rnd.randint(1, 4) if persona == "M01" else rnd.randint(8, 25)))
    return out


HIST_LINES = {}


def lint(card, spec, persona):
    errs = []
    texts = []
    if spec["tier"] == "A":
        texts = [x["user"] for x in card.get("tail", [])] + [x.get("assistant", "") for x in card.get("tail", [])] + [card.get("probe", "")]
        if not card.get("probe"):
            errs.append("no probe")
    else:
        sc = card.get("script") or []
        if len(sc) < 3:
            errs.append("script too short")
        texts = list(sc)
    full = "\n".join(texts)
    for term in (card.get("terms_absent") or []) if spec["class"] == "X" else []:
        if term and term in full:
            errs.append("target term in tail/probe: " + term)
    if spec["tier"] == "A":
        lim = 160 if persona == "M01" else 900
        if len(card.get("probe", "")) > lim:
            errs.append("probe too long")
    for l in [x.strip() for x in full.split(chr(10)) if len(x.strip()) >= 14]:
        if l in HIST_LINES.get(persona, ()):
            errs.append("tail/probe copies a line of the real history: " + l[:20])
            break
    if card.get("valid") is False:
        errs.append("llm says invalid: " + str(card.get("invalid_reason")))
    if spec["class"] in ("X", "H") and not (card.get("target") or {}).get("what"):
        errs.append("no target")
    if spec["class"] in ("Y", "Z", "N0") and not card.get("forbidden") and spec["class"] != "Z":
        errs.append("no forbidden")
    return errs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--release", required=True)
    ap.add_argument("--cases-dir", required=True)
    ap.add_argument("--persona-dir", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--gateway", default="http://127.0.0.1:18878/v1")
    ap.add_argument("--seed", type=int, default=20261109)
    ap.add_argument("--run", default="natural-gen")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--redo", default="", help="comma list of slot ids to re-pick (new case) and regenerate; only those are generated")
    ap.add_argument("--redo-seed", type=int, default=7)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    hist = load_histories(a.release)
    for pe, v in hist.items():
        HIST_LINES[pe] = {x.strip() for t in v for x in t["user"].split(chr(10)) if len(x.strip()) >= 14}
    gw = Gateway(a.gateway, a.run, "gen")
    due_rows, nodue_rows = load_due_rows(a.release)
    due_all = {p: list(v) for p, v in due_rows.items()}
    all_specs = []
    for persona in ("M01", "M02"):
        rnd = random.Random(f"{a.seed}:{persona}")
        H = hist[persona]
        cases = jl(os.path.join(a.cases_dir, f"cases-{persona}.jsonl"))
        pcard = json.load(open(os.path.join(a.persona_dir, persona, "persona.json"), encoding="utf-8"))
        slots = plan_slots(persona, rnd)
        used = set()
        order = sorted(range(len(slots)), key=lambda i: (0 if slots[i]["subtype"] in ("X4",) else 1 if SUBTYPES[slots[i]["subtype"]][2] else 2, rnd.random()))
        n = 0
        for i in order:
            s = slots[i]
            st = s["subtype"]
            tags = SUBTYPES[st][2]
            case, T, g = None, None, None
            row = None
            while st in ("X4", "Y4") and (due_rows if st == "X4" else nodue_rows)[persona]:
                cand_row = (due_rows if st == "X4" else nodue_rows)[persona].pop(0)
                cc = next(c for c in cases if c["case_id"] == cand_row["case_id"])
                if any(x["turn"] <= cand_row["cutoff_turn"] for x in cc["sources"]):
                    row, case = cand_row, cc
                    break
            if row is not None:
                used.add(case["case_id"])
                T = row["cutoff_turn"]
                L = max(x["turn"] for x in case["sources"] if x["turn"] <= T)
                g = max(0, (day_of(row["now"]) - day_of(H[L - 1]["time"])).days)
                pair = next((d for d in due_all[persona] if d["case_id"] == row["case_id"]), row)
                spec = dict(s, persona=persona, case_id=case["case_id"], cutoff_turn=T, gap_days=g, bucket="-",
                            fact_override=pair["required"], due_date=pair["now"][:10], now=row["now"], not_due=(st == "Y4"), source_row=row["id"])
            elif st == "N0":
                T = rnd.randint(300, len(H) - 40)
                spec = dict(s, persona=persona, case_id=None, cutoff_turn=T, gap_days=None)
            else:
                cand = [c for c in cases if c["case_id"] not in used and (not tags or any(t in c["content_tags"] for t in tags))]
                if not cand:
                    cand = [c for c in cases if c["case_id"] not in used]
                rnd.shuffle(cand)
                for c in cand:
                    r = pick_cutoff(c, H, s["bucket"], rnd, st)
                    if r:
                        case, (T, g) = c, r
                        break
                if case is None:
                    print("NO CASE for", persona, st, s.get("bucket"))
                    continue
                used.add(case["case_id"])
                spec = dict(s, persona=persona, case_id=case["case_id"], cutoff_turn=T, gap_days=g)
            n += 1
            spec["idx"] = n
            spec["id"] = f"NAT-{persona}-{st}-{n:02d}"
            spec.setdefault("now", None)
            all_specs.append((spec, case, pcard, H, rnd))
    if a.redo:
        redo = set(a.redo.split(","))
        rr = random.Random(a.redo_seed)
        casesby = {p: jl(os.path.join(a.cases_dir, f"cases-{p}.jsonl")) for p in ("M01", "M02")}
        taken = {p: {x[0]["case_id"] for x in all_specs if x[0]["persona"] == p and x[0].get("case_id")} for p in ("M01", "M02")}
        new = []
        for (spec, case, pcard, H, rnd) in all_specs:
            if spec["id"] not in redo:
                continue
            st = spec["subtype"] if spec["subtype"] != "X4" else "X1"
            tags = SUBTYPES[st][2]
            cand = [c for c in casesby[spec["persona"]] if c["case_id"] not in taken[spec["persona"]] and (not tags or any(t in c["content_tags"] for t in tags))]
            cand = cand or [c for c in casesby[spec["persona"]] if c["case_id"] not in taken[spec["persona"]]]
            rr.shuffle(cand)
            bucket = spec.get("bucket") if spec.get("bucket") not in (None, "-") else rr.choice(BUCKETS)[0]
            for c in cand:
                r = pick_cutoff(c, H, bucket, rr, st)
                if r:
                    taken[spec["persona"]].add(c["case_id"])
                    spec2 = dict(spec, subtype=st, case_id=c["case_id"], cutoff_turn=r[0], gap_days=r[1], bucket=bucket, now=None)
                    spec2.pop("fact_override", None)
                    spec2.pop("not_due", None)
                    new.append((spec2, c, pcard, H, rnd))
                    break
        all_specs = new
    if a.limit:
        all_specs = all_specs[:a.limit]
    print("slots planned:", len(all_specs))

    def work(args):
        spec, case, pcard, H, _ = args
        rnd = random.Random(f"{a.seed}:{spec['id']}")
        # times: the first tail/script turn goes after the cutoff turn
        tmp = dict(spec)
        if tmp["now"] is None:
            tmp["now"] = make_times(tmp, H, rnd, 1, spec["persona"])[0]
        prompt = build_prompt(tmp, pcard, case, H, rnd)
        card, errs, tries = None, [], 0
        for tries in range(1, 4):
            r = gw.chat(MODEL, [{"role": "user", "content": prompt}], "gen", spec["id"], temperature=0.8 if tries == 1 else 0.5,
                        max_tokens=1800, thinking={"type": "disabled"})
            try:
                card = parse_json(r["choices"][0]["message"].get("content"))
            except ValueError:
                errs = ["json"]
                continue
            errs = lint(card, spec, spec["persona"])
            if not errs and spec["subtype"] != "N0":
                ev, facts, ver, unk = evidence_block(case, spec["cutoff_turn"], H) if case else ("", "", "", "")
                vp = ("下面是一道合成题的卡片和它依据的历史证据。只检查 target.what、reference_reply，以及 forbidden.what 里关于用户或陪伴者过去说过、做过什么的事实性断言。" + NL +
                      "只有出现以下情况才算不支持：出现证据里没有的人名、地名、日期、数字、事件；或与证据矛盾。口语转述、合理概括、对‘不该提’的描述、给建议的话、对未来的话都不算问题。" + NL + "证据：" + NL + ev +
                      NL + "事实：" + NL + facts + NL + "版本：" + NL + ver +
                      (NL + "补充说明：" + spec["fact_override"] if spec.get("fact_override") else "") +
                      NL + NL + "卡片：" + NL + json.dumps({k: card.get(k) for k in ("target", "forbidden", "reference_reply")}, ensure_ascii=False) +
                      NL + NL + "只输出 JSON：{\"supported\": true/false, \"unsupported\": [\"最多3条，只写真正的问题\"]}")
                rv = gw.chat(MODEL, [{"role": "user", "content": vp}], "gen", spec["id"] + "-verify", temperature=0, max_tokens=400,
                             thinking={"type": "disabled"})
                try:
                    v = parse_json(rv["choices"][0]["message"].get("content"))
                except ValueError:
                    v = {"supported": True, "unsupported": []}
                card["_verify"] = v
                if not v.get("supported", True):
                    errs = ["卡片里有证据里没有的断言：" + "；".join(v.get("unsupported", [])[:3])]
            if not errs:
                break
            prompt = prompt + NL + NL + "【上次的输出有问题：" + "；".join(errs) + "。请改正后重新输出完整 JSON。】"
        return spec, case, card, errs, tries

    out = []
    with cf.ThreadPoolExecutor(a.workers) as ex:
        for k, res in enumerate(ex.map(work, all_specs), 1):
            spec, case, card, errs, tries = res
            out.append({"spec": spec, "card": card, "errors": errs, "tries": tries,
                        "case": {"case_id": case["case_id"], "title": case["title"], "tags": case["content_tags"]} if case else None})
            if k % 10 == 0:
                print("generated", k, "/", len(all_specs), flush=True)
    with open(os.path.join(a.out, "cards-raw.jsonl"), "w", encoding="utf-8") as f:
        for r in out:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    bad = [r for r in out if r["errors"] or not r["card"]]
    print("done", len(out), "with errors:", len(bad))


if __name__ == "__main__":
    main()
