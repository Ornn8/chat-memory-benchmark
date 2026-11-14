"""Judge driver for chat-memory-benchmark using a chat LLM (DeepSeek).

Reads a packets.jsonl (from `grading/grade.py prepare`) and, per packet, asks the
model to produce the review JSON described in grading/judge-prompt.md, then writes
reviews.jsonl. Afterwards run `grading/grade.py score` to aggregate.

Usage:
  uv run python adapters/hitmind/judge.py --packets outputs/packets-60.jsonl \
      --out outputs/reviews-60.jsonl
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
BENCH = HERE.parents[1]
PROMPT = (BENCH / "grading" / "judge-prompt.md").read_text(encoding="utf-8")

REVIEW_KEYS = ["id", "answer_sha256", "rubric_sha256", "required", "错认", "错否",
               "越界", "编造日期", "不当私事披露", "违反禁止", "未知当事实", "无关旧事", "reason"]

# ---- judge token usage tally (written next to the reviews file) ----
JUDGE_USAGE = {"calls": 0, "prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
import threading as _threading
_JUDGE_LOCK = _threading.Lock()


def _tally_judge_usage(data: dict) -> None:
    u = (data or {}).get("usage") or {}
    with _JUDGE_LOCK:
        JUDGE_USAGE["calls"] += 1
        JUDGE_USAGE["prompt_tokens"] += int(u.get("prompt_tokens") or 0)
        JUDGE_USAGE["completion_tokens"] += int(u.get("completion_tokens") or 0)
        JUDGE_USAGE["total_tokens"] += int(u.get("total_tokens") or 0)


def _read_env_key(name: str) -> str:
    if os.environ.get(name):
        return os.environ[name]
    envf = Path.home() / ".hermes" / ".env"
    if envf.exists():
        for line in envf.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if line.startswith(name + "="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


def _chat(messages, model, api_key, base_url, timeout=90.0) -> str:
    body = json.dumps({"model": model, "messages": messages, "temperature": 0.0}).encode("utf-8")
    req = urllib.request.Request(
        base_url.rstrip("/") + "/chat/completions", data=body,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
        method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    _tally_judge_usage(data)
    return data["choices"][0]["message"]["content"].strip()


def _parse_json(text: str) -> dict:
    t = text.strip()
    if t.startswith("```"):
        t = t.split("```", 2)[1]
        t = t[4:] if t.lower().startswith("json") else t
    t = t.strip().strip("`").strip()
    # grab first {...} block
    lo, hi = t.find("{"), t.rfind("}")
    if lo >= 0 and hi > lo:
        t = t[lo:hi + 1]
    return json.loads(t)


def judge_packet(pkt: dict, model: str, api_key: str, base_url: str) -> dict:
    material = {k: pkt[k] for k in ("id", "question", "now", "rubric", "facts", "sources", "answer")}
    messages = [
        {"role": "system", "content": PROMPT},
        {"role": "user", "content": "判分材料（JSON）：\n" + json.dumps(material, ensure_ascii=False)
         + "\n\n只输出一行 JSON 判断对象，字段见系统说明。"},
    ]
    last = None
    for _ in range(2):
        try:
            raw = _chat(messages, model, api_key, base_url)
            r = _parse_json(raw)
            # enforce id + sha from material
            r["id"] = pkt["id"]
            r["answer_sha256"] = pkt["answer_sha256"]
            r["rubric_sha256"] = pkt["rubric_sha256"]
            # ensure required length matches rubric
            req = r.get("required") or []
            n = len(pkt["rubric"].get("required") or [])
            if len(req) != n:
                req = (req + [False] * n)[:n]
            r["required"] = [bool(x) for x in req]
            for k in ("错认", "错否", "越界", "编造日期", "不当私事披露"):
                r[k] = bool(r.get(k, False))
            for k in ("违反禁止", "未知当事实", "无关旧事"):
                v = r.get(k, [])
                r[k] = v if isinstance(v, list) else [str(v)]
            r["reason"] = str(r.get("reason") or "").strip() or "（judge 未给出理由）"
            return {k: r[k] for k in REVIEW_KEYS}
        except Exception as exc:  # retry once, then fallback
            last = exc
    return {"id": pkt["id"], "answer_sha256": pkt["answer_sha256"], "rubric_sha256": pkt["rubric_sha256"],
            "required": [False] * len(pkt["rubric"].get("required") or []), "错认": False, "错否": False,
            "越界": False, "编造日期": False, "不当私事披露": False, "违反禁止": [], "未知当事实": [],
            "无关旧事": [], "reason": f"JUDGE_ERROR: {last}"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--packets", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--model", default=os.environ.get("HITMIND_QA_MODEL", "deepseek-chat"))
    ap.add_argument("--base-url", default=os.environ.get("HITMIND_QA_BASE_URL", "https://api.deepseek.com"))
    args = ap.parse_args()

    api_key = _read_env_key("DEEPSEEK_API_KEY")
    if not api_key:
        print("No DEEPSEEK_API_KEY found", file=sys.stderr)
        return 2
    pkts = [json.loads(s) for s in Path(args.packets).read_text(encoding="utf-8").splitlines() if s.strip()]
    outp = Path(args.out)
    outp.parent.mkdir(parents=True, exist_ok=True)
    with outp.open("w", encoding="utf-8") as f:
        for i, pkt in enumerate(pkts, 1):
            review = judge_packet(pkt, args.model, api_key, args.base_url)
            f.write(json.dumps(review, ensure_ascii=False) + "\n")
            if i % 10 == 0:
                print(f"judged {i}/{len(pkts)}", file=sys.stderr)
    print(f"wrote {len(pkts)} reviews -> {outp}")
    # persist judge token usage next to the reviews file
    usage_out = outp.with_suffix(".usage.json")
    usage_out.write_text(json.dumps({"judge": JUDGE_USAGE}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"judge usage -> {usage_out}  {JUDGE_USAGE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
