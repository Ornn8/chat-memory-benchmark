> **Scope**: This result is an **Author-reported** score for a **Raw-turn Retrieval Configuration** (isolating RAGStore + Flat/BM25/RRF + `timeline_mode`). It does **NOT** include the MemoryAgent fact-extraction pipeline. It is **not** a fully independently reproduced end-to-end score.

# results: add DSH-DREAM v0.3.6 Raw-turn Retrieval Configuration (87.4%, ¥2.05)

## Summary

This PR adds a **Raw-turn Retrieval Configuration** result for **DSH-DREAM
v0.3.6** on the Chat-Memory-Benchmark 1.0 six-persona set. It deliberately
isolates the storage + retrieval path: raw user/assistant turns are replayed
into an isolated sqlite-vec store, and answers are generated from the retrieved
`<memory-hint>` only. The MemoryAgent fact-extraction / rewrite / consolidation
pipeline is **not** part of this measurement.

- **System:** DSH-DREAM v0.3.6 — sqlite-vec + local ONNX BGE embedding,
  vector + BM25 retrieval fused with RRF.
- **Score:** **624 / 714 (87.4%)**. All 714 questions answered; 0 answer
  errors, 0 retrieval errors, 0 judge errors.
- **Cost:** **¥2.059** for the full 714-question run (answer + judge,
  estimated from token counts at the repository's `prices.json` rates).
- **Runtime:** 141.9 s answer stage + 119.0 s judge stage; 260.9 s end to end
  with 6 workers.

## Scope: what this result is and is not

| | |
| --- | --- |
| **Is** | Author-reported score for the DSH-DREAM **Raw-turn Retrieval Configuration**: sqlite-vec storage, ONNX BGE embedding, Flat vector + BM25 → RRF, `timeline_mode=True`. |
| **Is not** | An end-to-end DSH-DREAM chat-host run; it does not invoke MemoryAgent fact extraction, rewrite, or consolidation. |
| **Is not** | An independently reproduced score by the benchmark maintainers. |
| **Is** | A reproducible configuration with all 714 answers, per-question judgments, reasons, and a 10-question spot check. |

## Core finding: keep the event stream

The default `auto` retrieval mode applies latest-wins conflict collapse. In a
controlled 10-question pilot (same questions, same prompt, same model), it
scored **8 / 10** because it collapsed facts from 45 days earlier. Setting
`timeline_mode=True`, which returns candidates in ascending event time and
skips the conflict collapse, scored **10 / 10**.

Both `auto` failures were retrieval misses (the old fact was gone before the
answer model saw it), not generation errors. For long-horizon memory, retaining
the full event stream and letting timestamps disambiguate is more important than
aggressively collapsing to a single "latest" value.

## Configuration

| Parameter | Value |
| --- | --- |
| Storage | sqlite-vec, fresh DB per persona |
| Embedding | ONNX `bge-small-zh-v1.5` |
| Retrieval | Flat vector + full-corpus BM25 → RRF |
| `top_k` | 8 |
| `timeline_mode` | `True` |
| Answer model | `deepseek-flash`, temperature 0, thinking disabled |
| Judge | `deepseek-flash` rubric judge |
| Workers | 6 |
| Short-term window | none |
| Replay boundary | only `turn <= cutoff_turn`; question/answer never written back |

## Dimension results

| Dimension | Passed / questions | Score |
| --- | ---: | ---: |
| Facts | 339 / 393 | 86.3% |
| Corrections / changes | 138 / 161 | 85.7% |
| Commitments / plans | 184 / 219 | 84.0% |
| Boundaries / privacy | 105 / 108 | 97.2% |
| Time | 41 / 52 | 78.8% |
| Hypotheses / insufficient data | 116 / 126 | 92.1% |

A question may carry several tags, so dimensions do not sum to 714.

## Materials

All files are under `results/submissions/dsh-dream-v0.3.6/`:

| File | Content |
| --- | --- |
| `report.md` | Full report: score, dimensions, timing, cost, 3 typical failures |
| `results.jsonl` | 714 rich per-question records (answer, retrieved memories, usage) |
| `answers.jsonl` | Minimal `{id, answer}` file |
| `judgments.jsonl` | 714 per-question judgments, flags, and reasons |
| `summary.json` | Machine-readable aggregate |
| `reproduce.md` | Exact configuration, replay/judge pipeline, 10-question A/B |
| `spot_check.md` | 10-question stratified spot check (question, answer, judge reason, consistency) |
| `spot_check.py` | Deterministic sampler used to generate the spot check |
| `README.md` | Submission overview and caveats |

## Three representative failures

1. **`P12-NEW-005/d03` — commitments/plans, retrieval miss.** The question asks
   for the latest status of a lightbox. Retrieval returned the old "only
   measured, not quoted yet" turn but missed the later "the master sent the
   quote" turn because that turn no longer contains the word "lightbox".
2. **`P17-CASE-008/d00` — change/correction, retrieval miss.** The delivery date
   was recalled, but the later revision of how the button was discovered was
   not, so the answer wrongly denied that a revision happened.
3. **`P14-CASE-added-gift/d03` — boundary, generation error.** The memory that
   the card was in the drawer was retrieved correctly, but the answer mentioned
   the card and the weekend plan in front of the person the user wanted to
   surprise. This is a boundary/privacy failure at generation time, not a
   retrieval miss.

## Caveats

- This is the **1.0 six-persona 714-question** set. It is not the 2.1
  212-question development set, and the scores are not directly comparable.
- Replay stores raw user/assistant turns; it does not run MemoryAgent's fact
  extraction or consolidation. The result measures the store + hybrid retrieval
  path.
- Judging uses an automated LLM rubric judge, not the repository's official
  Codex review flow. All 714 individual judgments and reasons are included so
  maintainers can spot-check; the score should be read as an author-run result.
- No API key, private chat, live database, or SQLite file is included.

## Layout

Files follow the repository's documented submission layout:
`results/submissions/dsh-dream-v0.3.6/`.

## Checklist

- [x] Used the 714-question 1.0 six-persona set and recorded the exam SHA-256.
- [x] All 714 questions answered; no fabricated or placeholder answers.
- [x] Per-question answers, judgments, and reasons included.
- [x] 10-question stratified spot check included (8 pass / 2 fail, 10/10 bookkeeping consistency).
- [x] Per-persona memory isolation; only pre-cutoff history ingested.
- [x] No question/answer written back into later memory.
- [x] No SQLite database, API key, or local absolute path committed.
- [x] Cost and timing reported; judge method disclosed.
