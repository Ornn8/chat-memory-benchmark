> **投稿类型**：作者自测（author-reported）。判分为 deepseek-flash A/B + 人工仲裁复核；包含全部 714 题回答、逐题判分与理由。
> **数据集**：Chat-Memory-Benchmark 1.0 六人物正式测试集 datasets/natural-timegrid-20261101-v2（714 题）。
> **口径说明**：本成绩按“多余内容无错算过”复核；8 道“required 已答对、仅多余细节有误”的中性题按要求计入错题；1 道题面/答案口径题（P17-CASE-012/d45）按官方 rubric 判错。

# dsh-rofm 1.5.5 — Chat-Memory-Benchmark 1.0 六人物成绩

## 投稿信息

| 项 | 值 |
| --- | --- |
| 项目 | dsh-rofm |
| 作者 | 鄙人乃路人甲 |
| 上游 | https://github.com/wall1234567/dsh-rofm |
| 版本 | 1.5.5（package.json / engine/package.json） |
| 源码状态 | git HEAD 13f5f353；1.5.5 工作树（冻结树 54 文件、sha256 e5fa6cf2…，见 reproduce.md） |
| 测试日期 | 2026-11-10（Asia/Shanghai） |
| 题库 | natural-timegrid-20261101-v2，714 题 / 6 人物 |
| exam-inputs sha256 | 584e1acd8f2dc334be5859e31e689f9e684f24be88e6d9c808318698c4ea6c63 |
| answer-key sha256 | 07f390bbead123ed0f723a38d7642a0ca3367926e84d1af484b255284b2de392 |
| 判分 | deepseek-flash A/B（temperature 0）+ 人工仲裁复核（逐题理由见 judgments.jsonl） |

## 成绩

**681 / 714（95.38%）**。714 / 714 题全部作答；判分 714 / 714；无空答、无判分失败。

| 指标 | 值 |
| --- | ---: |
| 通过 / 已判分 | 681 / 714 |
| 通过率 | 95.38% |
| 原始 A/B 初裁（人工复核前） | 648 / 714（90.76%） |
| 错题 | 33（其中 8 道中性口径、1 道题面口径，其余 24 道为真实答错/漏答） |

## 分人物

| 人物 | 题数 | 通过 | 准确率 |
| --- | ---: | ---: | ---: |
| P17 | 172 | 167 | 97.09% |
| P20 | 170 | 162 | 95.29% |
| P16 | 123 | 115 | 93.50% |
| P01 | 88 | 80 | 90.91% |
| P14 | 82 | 79 | 96.34% |
| P12 | 79 | 78 | 98.73% |

## 文件

| 文件 | 内容 |
| --- | --- |
| answers.jsonl | 714 题 {id, answer} 真实回答 |
| reviews.jsonl | 714 题判分记录（rubric 必答项判定、错误标记、理由、答案/标准哈希） |
| judgments.jsonl | 由仓库 grading/grade.py 校验并汇总的逐题判定 |
| summary.json | grade.py score 生成的机器可读汇总（分人物/考点/间隔） |
| results.jsonl | 逐题富记录：回答、判定、类别、A/B 判词证据 |
| report.md | 中文完整报告：分项成绩、失败模式、成本耗时、口径说明 |
| reproduce.md | 复现配置与流程、哈希校验方法 |
| SHA256SUMS | 全部文件的 sha256 |

## 说明与限制

- 这是 1.0 六人物正式集（714 题），不是 2.1 的 212 题开发集；两套题成绩不可直接比较。
- 判分方式为 deepseek-flash A/B + 人工仲裁复核，不是仓库维护者的独立复现；全部逐题理由已公开供抽查。
- 8 道中性题（required 已答对、仅多余细节有误）按投稿要求计入错题；若按“多余内容不算错”口径，通过率会更高，详见 report.md。
- 未包含 API key、私聊原文、本地绝对路径或数据库文件。
