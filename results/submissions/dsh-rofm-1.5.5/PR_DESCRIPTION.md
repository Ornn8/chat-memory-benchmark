# results: add dsh-rofm 1.5.5（六人物 714 题 681/714 = 95.38%）

## Summary

This PR adds a complete 714-question result for **dsh-rofm 1.5.5** on the Chat-Memory-Benchmark 1.0 six-persona set.

- **System:** dsh-rofm 1.5.5 — DSH long-term memory plugin (archive/recall; 8,000-token non-native window, recent 6-turn window, logical clock).
- **Score:** **681 / 714 (95.38%)**. All 714 questions answered and judged; 0 empty answers, 0 judge errors.
- **Judging:** deepseek-flash A/B (temperature 0) + manual arbitration review; all 714 per-question reasons included.
- **Files:** answers.jsonl, reviews.jsonl, judgments.jsonl, summary.json, results.jsonl, report.md, reproduce.md, SHA256SUMS.

## Score

| Metric | Value |
| --- | ---: |
| Passed / scored | **681 / 714** |
| Pass rate | **95.38%** |
| Answered / total | 714 / 714 |
| Raw A/B first-pass (before review) | 648 / 714 (90.76%) |
| Wrong | 33（8 neutral-style + 1 wording/errata + 24 genuine） |

| Persona | Questions | Passed | Rate |
| --- | ---: | ---: | ---: |
| P17 | 172 | 167 | 97.09% |
| P20 | 170 | 162 | 95.29% |
| P16 | 123 | 115 | 93.50% |
| P01 | 88 | 80 | 90.91% |
| P14 | 82 | 79 | 96.34% |
| P12 | 79 | 78 | 98.73% |

## Test configuration

| Parameter | Value |
| --- | --- |
| Benchmark | 1.0 six-persona, 714 questions |
| Dataset | datasets/natural-timegrid-20261101-v2 |
| Exam SHA-256 | 584e1acd8f2dc334be5859e31e689f9e684f24be88e6d9c808318698c4ea6c63 |
| System version | dsh-rofm 1.5.5 (git HEAD 13f5f353 + 1.5.5 working tree, frozen tree sha256 e5fa6cf2…) |
| Memory window | 8,000-token non-native window; recent 6 turns; logical clock |
| Memory isolation | one independent memory dir per persona; question/answer never written back |
| Answer model | deepseek-flash, temperature 0, max_tokens 2500, max 6 tool rounds |
| Judge | deepseek-flash A/B + manual arbitration review |

## Dataset / judging notes

- **Neutral counted as wrong:** 8 questions had all required facts answered but an extra detail wrong (e.g., a date label). Per the submission request they are counted as **wrong**; they are listed in report.md. The pass count above therefore does not use a lenient “extra content” allowance.
- **P17-CASE-012/d45:** the official answer key requires the 2026-04-10 rename (谈女士→书宁); the 1.5.5 answer recalls the 2026-08-10 rename (便笺→誊写员). The private review revision of this benchmark already treats the 8/10 answer as correct (errata); this submission follows the **official rubric** and counts it as wrong. If maintainers accept the errata, the score becomes 682 / 714.
- **P01-NEW-001 x4:** these four questions were removed in the private dataset revision that the author uses for routine runs; for this submission they were re-answered with 1.5.5 (P01 replay) against the official 714-question set, so the score is complete over 714 questions.
- **Native flow:** the answer model used only dsh-rofm’s native memory tools; no full history, question bank, answer key, or judging hints were given to the answer model, and no question/answer was written back.

## Materials

All files are under results/submissions/dsh-rofm-1.5.5/.

## Caveats

- Author-reported result; judged by deepseek-flash A/B + manual arbitration, not the repository’s official Codex review flow. All 714 reasons are provided for spot-checking.
- This is the 1.0 714-question set, not the 2.1 212-question development set; not comparable across sets.
- No API key, private chat, local path, or database file is included.

## Checklist

- [x] Used the 714-question 1.0 six-persona set and recorded the exam SHA-256.
- [x] All 714 questions answered; real answers, no placeholders.
- [x] Per-question answers, judgments, flags, and reasons included.
- [x] Per-persona memory isolation; only pre-cutoff history processed.
- [x] No question/answer written back into memory.
- [x] Judge method, cost, and timing disclosed.
- [x] No API key, private chat, or local absolute path committed.
