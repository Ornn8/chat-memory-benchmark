"""HitMind adapter/runner for chat-memory-benchmark (natural-timegrid-20261101-v2).

Honest pipeline (HitMind v1 has no extraction / background consolidation):
  1. per-persona isolated DB (no cross-persona leakage)
  2. feed each historical turn as ONE raw memory via Engine.capture() (skips the
     write gate so similar turns are not deduped/versioned), stamped with the
     turn's logical time
  3. a question is answered once all turns up to its cutoff_turn are in memory
     (questions processed in ascending cutoff order, incremental reuse)
  4. answer = unified QA model given ONLY the recalled memories (+ the question)
  5. write answers.jsonl  -> grading via grading/grade.py

Usage:
  uv run python adapters/hitmind/run.py --dry-run --limit 3      # no LLM; verify pipeline
  uv run python adapters/hitmind/run.py --limit 5 --out outputs/answers.jsonl
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
BENCH = HERE.parents[1]                     # references/chat-memory-benchmark
REPO = HERE.parents[3]                       # hitmind repo root
sys.path.insert(0, str(REPO))

from hitmind.core.engine import Engine, make_embedder_from_env  # noqa: E402

_RERANK_MODEL_DEFAULT = "temsa/mmarco-mMiniLMv2-L12-H384-v1-onnx-cpu-qint8"


def _make_reranker():
    """Reranker from env (set by main): a real HttpReranker when HITMIND_RERANK_MODEL is
    present, else NullReranker. Rerank shares the embedding base_url (server root /rerank)."""
    from hitmind.core.engine import make_reranker_from_env
    return make_reranker_from_env()

DATASET = BENCH / "datasets" / "natural-timegrid-20261101-v2"
PERSONAS = ["P01", "P12", "P14", "P16", "P17", "P20"]


def _rows(path: Path) -> list[dict]:
    return [json.loads(s) for s in path.read_text(encoding="utf-8-sig").splitlines() if s.strip()]


# ---- token usage accounting (QA + topic finalize; judge is tallied separately) ----
USAGE = {"qa": {"calls": 0, "prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
         "finalize": {"calls": 0, "prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}}
USAGE_LOCK = __import__("threading").Lock()


def _tally_usage(kind: str, data: dict) -> None:
    u = (data or {}).get("usage") or {}
    with USAGE_LOCK:
        b = USAGE[kind]
        b["calls"] += 1
        b["prompt_tokens"] += int(u.get("prompt_tokens") or 0)
        b["completion_tokens"] += int(u.get("completion_tokens") or 0)
        b["total_tokens"] += int(u.get("total_tokens") or 0)


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


def _qa(question: str, memories: list[dict], model: str, api_key: str,
        base_url: str = "https://api.deepseek.com", timeout: float = 60.0,
        recent_turns: list[dict] | None = None) -> str:
    if not api_key:
        return "[NO_QA_MODEL] " + question
    mem_block = "\n".join(
        f"[{m.get('id') or ''}] ({m.get('kind') or ''})[@{(m.get('created_at') or '')[:10]}]："
        f"{(m.get('content') or '').replace(chr(10), ' ').strip()}"
        for m in memories) or "（无可用记忆）"
    recent_block = ""
    if recent_turns:
        recent_block = "\n\n最近对话（短期窗口）：\n" + "\n".join(
            f"用户：{t['用户消息']}\n助手：{t['助手回复']}" for t in recent_turns)
    sys_prompt = (
        "You are answering as the assistant in a long-term chat, using ONLY the provided "
        "memory excerpts (each tagged with the date it was said, like [@2026-06-10]) and the "
        "recent conversation.\n"
        "Rules:\n"
        "1. Scan ALL excerpts first; if any states the asked fact, use it — never reply "
        "'not mentioned / I don't know' when the excerpts actually contain it.\n"
        "2. Only give a specific date/number/name that is supported by the excerpts. If the "
        "question is about a TIME/DATE and an excerpt gives it only as a relative expression "
        "('上周五'/'前天'/'昨天'/'下周二'), you MAY compute the absolute date using THAT "
        "excerpt's [@date] (the day it was said) and state it. Do not fabricate dates that "
        "cannot be derived.\n"
        "3. Do NOT volunteer specific dates when the question is not about time.\n"
        "4. If a detail is genuinely absent from the excerpts, say you don't know; don't guess.\n"
        "5. If the excerpts give conflicting accounts of the same thing, point out the "
        "inconsistency and suggest confirming; do NOT assert which version is correct.\n"
        "6. Do not proactively mention sensitive personal details or unrelated old events; "
        "answer only what is asked.\n"
        "Answer concisely, in the user's language."
    )
    user_prompt = f"记忆片段：\n{mem_block}{recent_block}\n\n问题：{question}"
    body = json.dumps({
        "model": model,
        "messages": [{"role": "system", "content": sys_prompt},
                     {"role": "user", "content": user_prompt}],
        "temperature": 0.0,
    }).encode("utf-8")
    req = urllib.request.Request(
        base_url.rstrip("/") + "/chat/completions", data=body,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
        method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    _tally_usage("qa", data)
    return data["choices"][0]["message"]["content"].strip()


_FINALIZE_SYS = (
    "你是长期记忆的离线聚合助手。下面给出同一个候选簇里的若干条记忆（按时间先后编号 [0]、[1]…）。"
    "请判断它们是否在讲**同一件事**，并**仔细检查彼此是否矛盾或前后更新**（同一事实/参数/偏好被后来的记忆推翻或修改）。"
    "只输出一个 JSON 对象，不要任何多余文字：\n"
    '{"same_matter": true/false, '
    '"topic": "若同一件事，给一句简短中文主题（含主体+对象，<=30字），否则空串", '
    '"corrections": [{"index": 更正（较新）那条的序号, "corrects": 被它更正的旧条序号, "note": "更正内容简述"}]}'
)


class DeepSeekFinalizeLLM:
    """Minimal LLM for Engine.run_topic_task() in the benchmark (finalize only).

    Mirrors adapters.hermes.llm.HostClusterLLM.finalize: given cluster member texts,
    return {same_matter, topic, corrections}. Uses the same DeepSeek endpoint as QA.
    """

    def __init__(self, model: str, api_key: str, base_url: str = "https://api.deepseek.com"):
        self.ok = bool(api_key)
        self.model, self.api_key, self.base_url = model, api_key, base_url

    def _parse(self, text: str) -> dict | None:
        t = (text or "").strip()
        if t.startswith("```"):
            t = t.split("```", 2)[1]
            t = t[4:] if t.lower().startswith("json") else t
        lo, hi = t.find("{"), t.rfind("}")
        if lo < 0 or hi <= lo:
            return None
        try:
            obj = json.loads(t[lo:hi + 1])
        except ValueError:
            return None
        topic = str(obj.get("topic") or "").strip()[:40]
        same = bool(obj.get("same_matter")) and bool(topic)
        corr = obj.get("corrections")
        return {"same_matter": same, "topic": topic,
                "corrections": corr if isinstance(corr, list) else []}

    def finalize(self, members: list[str]) -> dict | None:
        if not members or not self.ok:
            return None
        block = "\n".join(f"[{i}] {t}" for i, t in enumerate(members))
        body = json.dumps({
            "model": self.model, "temperature": 0.0,
            "messages": [{"role": "system", "content": _FINALIZE_SYS},
                         {"role": "user", "content": block}],
        }).encode("utf-8")
        req = urllib.request.Request(
            self.base_url.rstrip("/") + "/chat/completions", data=body,
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.api_key}"},
            method="POST")
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            _tally_usage("finalize", data)
            return self._parse(data["choices"][0]["message"]["content"])
        except Exception:
            return None


def run_persona(persona: str, questions: list[dict], *, top_k: int, dry_run: bool,
                model: str, api_key: str, base_url: str, db_dir: Path,
                finalize: bool = True, short_window: int = 0,
                trace: list | None = None) -> list[dict]:
    history = _rows(DATASET / "histories" / f"{persona}.jsonl")
    # sort questions by cutoff so we advance history monotonically
    questions = sorted(questions, key=lambda q: q["cutoff_turn"])
    eng = Engine(str(db_dir / f"{persona}.db"), agent_id=f"bench-{persona}",
                 embedder=make_embedder_from_env(),
                 reranker=_make_reranker(),
                 memory_max_chars=0)  # raw per-turn capture must NOT be capped (no extraction here)
    if finalize:
        # enable the engine's pull-based topic finalizer with a DeepSeek-backed LLM
        eng._llm = DeepSeekFinalizeLLM(model, api_key, base_url)
    answers = []
    fed = 0
    finalized_clusters = 0
    for q in questions:
        cutoff = q["cutoff_turn"]
        while fed < cutoff and fed < len(history):
            turn = history[fed]
            text = f"用户：{turn['用户消息']}\n助手：{turn['助手回复']}"
            eng.capture(text, "fact", title=f"第{turn['轮次']}轮",
                        tags=[persona], created_at=turn["逻辑时间"])
            fed += 1
        maint_calls = 0
        if finalize:
            # drain the topic backlog so recall can use finalized clusters (topic expansion)
            while True:
                r = eng.run_topic_task().get("data", {})
                if r.get("skipped") or not (r.get("finalized") or r.get("rejected") or r.get("failed")):
                    break
                finalized_clusters += int(r.get("finalized") or 0)
                maint_calls += 1
        res = eng.recall(q["question"], top_k=top_k)["data"]["results"]
        if trace is not None:
            trace.append({"id": q["id"], "persona": persona, "cutoff_turn": cutoff,
                          "now": q.get("now"), "ingested_turns": fed,
                          "short_window": short_window,
                          "recalled_ids": [m.get("id") for m in res],
                          "recalled_titles": [m.get("title") for m in res],
                          "memory_maintenance_calls": maint_calls})
        if dry_run:
            answers.append({"id": q["id"], "answer": f"[DRY] recalled={len(res)} "
                            f"top={[m.get('title') for m in res]}"})
        else:
            recent = history[max(0, fed - short_window):fed] if short_window > 0 else None
            ans = _qa(q["question"], res, model, api_key, base_url, recent_turns=recent)
            answers.append({"id": q["id"], "answer": ans})
    if finalize:
        print(f"  [{persona}] finalized_clusters_during_run={finalized_clusters}", file=sys.stderr)
    eng.close()
    return answers


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--persona", default=None, help="one persona (default: all)")
    ap.add_argument("--limit", type=int, default=0, help="max questions per persona (0=all)")
    ap.add_argument("--top-k", type=int, default=10)
    ap.add_argument("--ids", default=None, help="comma-separated question ids to run (overrides persona/limit)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--out", default=str(BENCH / "outputs" / "answers.jsonl"))
    ap.add_argument("--model", default=os.environ.get("HITMIND_QA_MODEL", "deepseek-chat"))
    ap.add_argument("--base-url", default=os.environ.get("HITMIND_QA_BASE_URL", "https://api.deepseek.com"))
    ap.add_argument("--embed-base-url",
                    default=os.environ.get("HITMIND_EMBED_BASE_URL", "http://127.0.0.1:8091/v1"),
                    help="OpenAI-compatible /v1/embeddings endpoint (default: local-embed 8091)")
    ap.add_argument("--embed-model", default=os.environ.get("HITMIND_EMBED_MODEL", "embeddinggemma-2"))
    ap.add_argument("--embed-api-key",
                    default=os.environ.get("HITMIND_EMBED_API_KEY") or _read_env_key("HITMIND_EMBED_API_KEY"))
    ap.add_argument("--no-embed", action="store_true", help="force BM25-only (skip dense embeddings)")
    ap.add_argument("--no-finalize", action="store_true",
                    help="skip per-question topic finalization (raw-retrieval baseline; default: finalize on)")
    ap.add_argument("--short-window", type=int, default=0,
                    help="N recent turns also shown to the QA model (declared short-term window; 0=pure memory)")
    ap.add_argument("--trace-out", default=None,
                    help="optional JSONL path to record per-question run trace (recalled ids, maintenance calls, ...)")
    ap.add_argument("--rerank-model", default=os.environ.get("HITMIND_RERANK_MODEL", _RERANK_MODEL_DEFAULT),
                    help="cross-encoder model id for /rerank (shared with embed base_url)")
    ap.add_argument("--no-rerank", action="store_true", help="disable rerank (NullReranker)")
    args = ap.parse_args()

    # ---- configure embeddings so dense retrieval works (default: local-embed 8091) ----
    # make_embedder_from_env() reads HITMIND_EMBED_* from os.environ; setting them here makes
    # the benchmark reproducible without exporting env vars. Use --no-embed for BM25-only.
    if args.no_embed:
        os.environ.pop("HITMIND_EMBED_BASE_URL", None)
        os.environ.pop("HITMIND_EMBED_MODEL", None)
    else:
        os.environ["HITMIND_EMBED_BASE_URL"] = args.embed_base_url
        os.environ["HITMIND_EMBED_MODEL"] = args.embed_model
        if args.embed_api_key:
            os.environ["HITMIND_EMBED_API_KEY"] = args.embed_api_key
    _base = os.environ.get("HITMIND_EMBED_BASE_URL")
    print("[embed] " + ("BM25-only (NullEmbedder)" if not _base
                        else f"dense+BM25 @ {_base} · model={os.environ.get('HITMIND_EMBED_MODEL')}"),
          file=sys.stderr)
    # ---- rerank config (shares the embedding base_url; /rerank lives at server root) ----
    if args.no_rerank or args.no_embed:
        os.environ.pop("HITMIND_RERANK_MODEL", None)
        print("[rerank] disabled (NullReranker)", file=sys.stderr)
    else:
        os.environ["HITMIND_RERANK_MODEL"] = args.rerank_model
        print(f"[rerank] on · model={args.rerank_model}", file=sys.stderr)

    all_q = _rows(DATASET / "exam-inputs.jsonl")
    api_key = _read_env_key("DEEPSEEK_API_KEY")
    db_dir = Path(tempfile.mkdtemp(prefix="hitmind-bench-"))

    out_rows = []
    trace: list = []
    if args.ids:
        ids = [x.strip() for x in args.ids.split(",") if x.strip()]
        by_persona: dict[str, list[dict]] = {}
        qmap = {q["id"]: q for q in all_q}
        for i in ids:
            q = qmap[i]
            by_persona.setdefault(q["persona"], []).append(q)
        for p, qs in by_persona.items():
            ans = run_persona(p, qs, top_k=args.top_k, dry_run=args.dry_run,
                              model=args.model, api_key=api_key, base_url=args.base_url, db_dir=db_dir,
                              finalize=not args.no_finalize, short_window=args.short_window, trace=trace)
            out_rows.extend(ans)
            print(f"[{p}] answered {len(ans)} questions", file=sys.stderr)
    else:
        personas = [args.persona] if args.persona else PERSONAS
        for p in personas:
            qs = [q for q in all_q if q["persona"] == p]
            if args.limit:
                qs = qs[: args.limit]
            ans = run_persona(p, qs, top_k=args.top_k, dry_run=args.dry_run,
                              model=args.model, api_key=api_key, base_url=args.base_url, db_dir=db_dir,
                              finalize=not args.no_finalize, short_window=args.short_window, trace=trace)
            out_rows.extend(ans)
            print(f"[{p}] answered {len(ans)} questions", file=sys.stderr)

    outp = Path(args.out)
    outp.parent.mkdir(parents=True, exist_ok=True)
    with outp.open("w", encoding="utf-8") as f:
        for r in out_rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"wrote {len(out_rows)} answers -> {outp}")

    # ---- run metadata for submission (test conditions + dataset/answer hashes) ----
    import hashlib
    manifest = DATASET / "manifest.json"
    msha = hashlib.sha256(manifest.read_bytes()).hexdigest() if manifest.exists() else None
    ans_sha = hashlib.sha256(outp.read_bytes()).hexdigest() if outp.exists() else None
    meta = {
        "answers_file": str(outp), "answers_sha256": ans_sha,
        "dataset": "natural-timegrid-20261101-v2", "dataset_manifest_sha256": msha,
        "questions": len(out_rows),
        "config": {
            "ingest": "capture(raw, skip write-gate), one memory per history turn, logical-time stamped",
            "memory_max_chars": 0, "top_k": args.top_k,
            "finalize_topic": (not args.no_finalize),
            "embed_model": os.environ.get("HITMIND_EMBED_MODEL") if _base else "NullEmbedder(BM25-only)",
            "embed_endpoint": os.environ.get("HITMIND_EMBED_BASE_URL"),
            "qa_model": args.model, "qa_base_url": args.base_url, "short_window_turns": args.short_window,
            "rerank_model": (os.environ.get("HITMIND_RERANK_MODEL") if not (args.no_rerank or args.no_embed) else "off"),
            "memory_isolation": "per-persona isolated DB", "exam_isolation": "questions/answers not written back",
        },
        "usage": USAGE,
    }
    if args.trace_out and trace:
        tp = Path(args.trace_out)
        tp.parent.mkdir(parents=True, exist_ok=True)
        with tp.open("w", encoding="utf-8") as f:
            for t in trace:
                f.write(json.dumps(t, ensure_ascii=False) + "\n")
        meta["trace_file"] = str(tp)
    mp = outp.with_suffix(".runmeta.json")
    mp.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote run metadata -> {mp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
