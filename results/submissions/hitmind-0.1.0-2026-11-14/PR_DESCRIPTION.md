# 投稿：HitMind 0.1.0 — Chat-Memory-Benchmark 1.0 六人物成绩（作者自测）

- 项目：**HitMind**（https://github.com/Fishskys/hitmind），版本 v0.1.0，commit `8fc7a51`
- 数据集：`natural-timegrid-20261101-v2`（714 题 / 6 人物），exam-inputs sha256 `584e1acd8f2dc334…`
- **成绩（有 rerank）**：**660 / 714 = 92.44%**；无 rerank 对照 631 / 714 = 88.38%
- 714 / 714 全部作答并判分，无未答、无判分失败
- 判分：`grading/judge-prompt.md` + `deepseek-chat`(temperature=0) 自动语义判分，`grade.py` 汇总（未人工抽查）
- 消耗：单次测评 Deepseek 官方平台耗费 **1.8 元左右**（两档合计 3.57 元，均摊每次 1.79 元）
- 材料位置：`results/submissions/hitmind-0.1.0-2026-11-14/`（answers/reviews/judgments/summary 两档 + report/reproduce + SHA256SUMS）
- 说明：作者自测口径，非维护者独立复现；两档仅差 rerank 开关。
