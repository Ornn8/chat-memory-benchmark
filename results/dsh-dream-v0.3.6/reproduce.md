# Reproduction — DSH-DREAM v0.3.6 on Chat-Memory-Benchmark 1.0

This directory is a frozen results submission. It contains the 714 answers,
the per-question judgments, the aggregate, and the full report. The harness is
kept separately in the DSH-DREAM benchmark workspace; the exact pipeline is
described below so the run can be repeated without reversing the outputs.

## 1. Dataset

- Benchmark: 1.0 six-persona set.
- Path: `datasets/natural-timegrid-20261101-v2/`.
- Questions: 714 (`exam-inputs.jsonl`), personas `P01`, `P12`, `P14`, `P16`,
  `P17`, `P20`.
- Exam file SHA-256:
  `584e1acd8f2dc334be5859e31e689f9e684f24be88e6d9c808318698c4ea6c63`.
- Histories and answer key are used unmodified. The answer key is only read by
  the judge, never by the answering model.

## 2. System under test

- DSH-DREAM v0.3.6.
- Storage: sqlite-vec.
- Embedding: local ONNX `bge-small-zh-v1.5` (512-d, unit-normalized).
- Retrieval: exact Flat vector scan + full-corpus BM25, fused with RRF.
- Reranking/conflict handling: `timeline_mode=True` — candidates are returned in
  ascending event time and the latest-wins conflict collapse is skipped.
- Answer model: `deepseek-flash` (DeepSeek API), temperature 0, thinking
  disabled, `max_tokens=450`, 6 concurrent workers.
- Judge model: `deepseek-flash`, temperature 0, thinking disabled.

## 3. Isolation and replay

For each persona, in a fresh temporary database:

1. Delete the previous test database.
2. Sort that persona's questions by `cutoff_turn` ascending.
3. Ingest every history turn with `turn <= cutoff_turn`, never later turns.
   Both the user message and the assistant reply are stored with the same
   millisecond timestamp; no future turn is visible.
4. Retrieve with `search_memory(question, top_k=8, timeline_mode=True)`.
5. Build the answer prompt from the retrieved `<memory-hint>` and the current
   question. No full history and no answer key are passed to the answer model.
6. Store the answer and move to the next question. The question and answer are
   never written back into memory.
7. After the persona is finished, close and delete the temporary database.

Six personas are processed one after another. No live DSH database is opened;
the test database is created only inside the benchmark work directory and is
removed after the run.

## 4. Answer prompt

- System prompt: answer only from retrieved memory; admit unknown facts; do not
  invent dates, names, or details; if memories describe the same thing at
  different times, prefer the newest for current-state questions and the
  relevant past state for historical questions.
- User prompt: current logical time, `<memory-hint>` block with timestamped
  memories, then the question.
- No short-term conversation window is appended.

## 5. Judging

For each question the judge receives:

- the question, `now`, and the model answer;
- the repository's `required`, `forbidden`, `unknown`, and `acceptable` fields;
- the public evidence packet (`facts` + source quotes).

The judge returns one boolean per `required` item, indices for forbidden and
unknown hits, and flags for misidentification, wrong denial, boundary
violation, fabricated date, and improper private disclosure. A question passes
only when all required items are true, no forbidden/unknown item is hit, and no
error flag is raised. This mirrors `grading/README.md`'s pass rule. The judge
transcript is preserved per question in `judgments.jsonl`.

The official repository recommends a Codex-based review with the `grading/`
tool. This submission uses an automated LLM rubric judge instead; the reasons
and all 714 individual decisions are included for independent spot-checking.

## 6. Configuration summary

| Parameter | Value |
| --- | --- |
| `retrieval_mode` | `timeline` (`timeline_mode=True`) |
| `top_k` | 8 |
| Answer temperature | 0 |
| Thinking | disabled |
| Workers | 6 |
| Short-term window | none |
| Storage | sqlite-vec, per-persona rebuild |
| Embedding | ONNX `bge-small-zh-v1.5` |
| Answer / judge model | `deepseek-flash` |

## 7. Ten-question A/B: why `timeline_mode`

A controlled pilot used the same 10 questions, the same prompt, and the same
model; only the retrieval mode changed:

| Mode | Passed | Notes |
| --- | ---: | --- |
| `auto` (default) | 8 / 10 | latest-wins collapse removed 45-day-old facts |
| `timeline_mode=True` | 10 / 10 | old and new events both survive; timestamps disambiguate |

Pilot question ids:

`P01-NEW-009/d03`, `P12-ADD-004/d45`, `P14-CASE-added-rumor/d00`,
`P16-CASE-added-mixup/d00`, `P16-CASE-batch-whisky/d45`,
`P17-CASE-026/d00`, `P17-CASE-032/d03`, `P17-CASE-034/d03`,
`P20-CASE-014/d45`, `P20-CASE-018/d15`.

The two `auto` failures were both retrieval misses caused by conflict collapse,
not answer-generation errors. This pilot preceded a small final prompt-wording
tweak; it isolates the retrieval-mode effect.

## 8. Cost and timing

| Item | Value |
| --- | ---: |
| Ingest (6 personas, ~4,480 memory records) | 26.3 s |
| Retrieval (714 queries) | 10.7 s |
| Answer generation (cumulative request latency) | 599.2 s |
| Judge (cumulative request latency) | 695.2 s |
| Answer-stage wall clock | 141.9 s |
| Judge-stage wall clock | 119.0 s |
| End-to-end wall clock | 260.9 s |
| Answer tokens (input / output) | 552,335 / 24,479 |
| Judge tokens (input / output) | 678,055 / 65,103 |
| Estimated cost | **¥2.059** |

Cost uses the repository's `prices.json` (DeepSeek V4.1 flash: ¥1.296/M input,
¥5.184/M output). Embeddings run locally and are not billed. The number is an
estimate from token counts, not a provider invoice.

## 9. Caveats

- This is the 1.0 714-question set, not the 2.1 212-question development set.
- The replay stores raw turns; it does not reproduce MemoryAgent's extraction,
  rewrite, or consolidation steps.
- The judge is a single LLM rubric judge; borderline semantic cases may differ
  from a human/Codex review. Every decision and reason is included.
- No API key, private chat, live database, or SQLite file is part of this
  submission.
