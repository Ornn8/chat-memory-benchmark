# DSH-DREAM v0.3.6 — Chat-Memory-Benchmark 1.0

## Submission

| Item | Value |
| --- | --- |
| Project | DSH-DREAM |
| Version | v0.3.6 |
| Upstream | https://github.com/baiqieji-LuLu/DSH-DREAM |
| Tested package commit | `61812169fff9cd8e7eac8b216fb269ae6f72b72a` |
| Benchmark | 1.0, six personas, 714 questions |
| Dataset | `datasets/natural-timegrid-20261101-v2/` |
| Exam SHA-256 | `584e1acd8f2dc334be5859e31e689f9e684f24be88e6d9c808318698c4ea6c63` |
| Test date | 2026-11-10 (Asia/Shanghai) |

## Score

**624 / 714 (87.4%)**. All 714 questions answered, no answer errors, no
retrieval errors, and no judge errors.

| Dimension | Passed / questions | Score |
| --- | ---: | ---: |
| Facts | 339 / 393 | 86.3% |
| Corrections / changes | 138 / 161 | 85.7% |
| Commitments / plans | 184 / 219 | 84.0% |
| Boundaries / privacy | 105 / 108 | 97.2% |
| Time | 41 / 52 | 78.8% |
| Hypotheses / insufficient data | 116 / 126 | 92.1% |

A question may carry several tags, so dimension counts do not add up to 714.

## Test configuration

- Storage: sqlite-vec, one isolated database per persona, rebuilt before replay.
- Embedding: local ONNX `bge-small-zh-v1.5`.
- Retrieval: exact Flat vector scan + full-corpus BM25, fused with RRF,
  `top_k=8`, `timeline_mode=True` (chronological event stream, no latest-wins
  conflict collapse).
- Replay: only turns with `turn <= cutoff_turn` are ingested; the question and
  answer are never written back.
- Answer model: `deepseek-flash`, temperature 0, thinking disabled, 6 workers.
- Judge: LLM rubric judge (`deepseek-flash`) using the repository's
  `required` / `forbidden` / `unknown` fields plus the evidence packet.
- No short-term conversation window was appended; answers use retrieved memory
  only.

## Materials

| File | Content |
| --- | --- |
| `report.md` | Full Chinese report: score, dimensions, timing, cost, three typical failures |
| `results.jsonl` | 714 rich per-question records (answer, retrieved memories, usage) |
| `answers.jsonl` | Minimal `{id, answer}` file required by `docs/submit-results.md` |
| `judgments.jsonl` | 714 per-question judgments and reasons |
| `summary.json` | Machine-readable aggregate |
| `reproduce.md` | Reproduction configuration and the 10-question A/B |
| `PR_DESCRIPTION.md` | Ready-to-paste Pull Request body |

## Caveats

- This is the **1.0 six-persona 714-question** set, not the 2.1 212-question
  development set. Scores are not directly comparable across the two.
- The judge is an LLM rubric judge, not the repository's official Codex review
  flow. Per-question reasons are included so maintainers can spot-check.
- The replay stores raw user/assistant turns; it does not run DSH-DREAM's
  MemoryAgent fact extraction or consolidation. The result therefore measures
  the store + hybrid retrieval path.
- No live DSH database, API key, or private chat data is included in this
  directory.
