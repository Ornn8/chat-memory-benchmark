# memory-system（AstrBot 记忆体系）· 作者自测 · 未复核

作者 wuwugi 通过 [Issue #16](https://github.com/Ornn8/chat-memory-benchmark/issues/16) 投稿；这是**作者自测，维护方没有复测**。

| 项 | 内容 |
| --- | --- |
| 项目 | [wuwugi/memory-system](https://github.com/wuwugi/memory-system)（main 分支，投稿时 HEAD；发布包 18 个文件） |
| 题库 | `natural-timegrid-20261101-v2`，六人物，714 题；六个人物各用独立数据目录 |
| 成绩 | **522 / 714 = 73.1%**，未答 0 |
| 判分 | DeepSeek `deepseek-chat`，temperature 0，按 `grading/judge-prompt.md` 逐题判定，`grade.py score` 汇总 |
| 作答 | DeepSeek `deepseek-chat`，temperature 0，max_tokens 220；没有最近对话窗口，只给检索片段和用户档案 |
| 日期 | 2026-11-10（来自投稿材料文件名） |
| 记忆 | 每条消息按归档格式落盘（用历史逻辑时间）；检索 top_k=20，关键词 + `bge-small-zh-v1.5` 语义，按截止日期过滤；`profile.py` 抽取用户自述事实，注入不超过 400 字；**未启用模糊化压缩（S0→S4）** |
| 作者的说明 | 同一系统的调优配置（档案逐窗口抽取 + 按字段取最新）为 540 / 714 = 75.6%（材料未包含）；判分者是 DeepSeek，不是 Codex |

材料：`answers.jsonl`（714 条回答）、`reviews.jsonl`（逐题判定）、`judgments.jsonl`（`grade.py` 输出）、`summary.json`、`report.md`（作者的报告；已转成 UTF-8）。作者的 `packets.jsonl`（题目与证据包，可由 `grade.py prepare` 重新生成）没有收入。

## 维护方做了什么

用 `grading/grade.py` 对作者的回答和逐题判定重新校验与汇总：题号、答案和标准的哈希全部对得上，重算 **522 / 714**，与作者的 `judgments.jsonl` 和 `summary.json` 逐题一致。没有复判语义，也没有重新运行系统。
