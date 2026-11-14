# HitMind 0.1.0：六人物成绩（作者自测）

> **投稿类型**：作者自测（author-reported），非本仓库维护者独立复现或审核。
> **数据集**：Chat-Memory-Benchmark 1.0 六人物正式测试集 `datasets/natural-timegrid-20261101-v2`（714 题 / 6 人物）。
> **判分**：`grading/judge-prompt.md` + DeepSeek（`deepseek-chat`, temperature=0）自动语义判分，`grade.py` 汇总；未做人工抽查。

## 总成绩

| 档位 | 通过 / 已判题数 | 通过率 | 未答 |
| --- | ---: | ---: | ---: |
| **有 rerank（主）** | **660 / 714** | **92.44%** | 0 |
| 无 rerank（对照） | 631 / 714 | 88.38% | 0 |

714 题全部作答并判分，无未答、无判分失败。两档使用同一套入库历史与作答提示词，仅 rerank 开关不同。

## 所用模型

| 角色 | 模型 | 说明 |
| --- | --- | --- |
| 作答（QA） | `deepseek-chat` | temperature=0；只喂召回记忆 + 问题 |
| 判分 | `deepseek-chat` | temperature=0；按 `grading/judge-prompt.md` 语义判分 |
| 嵌入（dense） | `embeddinggemma-2` | 本地 OpenAI 兼容 `/v1/embeddings`，int4量化，512 维 |
| 重排（rerank） | `temsa/mmarco-mMiniLMv2-L12-H384-v1-onnx-cpu-qint8` | 本地 cross-encoder `/rerank`（`rerank_pool=30`，fail-open）；无 rerank 档关闭 |

## 按人物（有 rerank）

| 人物 | 通过 / 题数 | 通过率 |
| --- | ---: | ---: |
| P01 | 85 / 88 | 96.59% |
| P12 | 74 / 79 | 93.67% |
| P14 | 74 / 82 | 90.24% |
| P16 | 116 / 123 | 94.31% |
| P17 | 154 / 172 | 89.53% |
| P20 | 157 / 170 | 92.35% |

## 按时间间隔（有 rerank）

| 时距 | 通过 / 题数 | 通过率 |
| --- | ---: | ---: |
| 0 天 | 177 / 189 | 93.65% |
| 3 天 | 173 / 184 | 94.02% |
| 15 天 | 159 / 174 | 91.38% |
| 45 天 | 151 / 167 | 90.42% |

## 各考点

一题可属于多个考点，不能相加当总题数；完整 27 项见 `summary.json` 的 `groups.content_tags`，无 rerank 档见 `summary-off.json`。按通过率升序（有 rerank）：

| 考点 | 通过 / 题数 | 通过率 |
| --- | ---: | ---: |
| 真实变化 | 47 / 58 | 81.03% |
| 时间题 | 40 / 48 | 83.33% |
| 用户的基本信息 | 47 / 56 | 83.93% |
| 职业 | 43 / 51 | 84.31% |
| 约定和欠账 | 47 / 55 | 85.45% |
| 共同编的故事 | 37 / 43 | 86.05% |
| 计划 | 56 / 65 | 86.15% |
| 没解释的矛盾 | 41 / 47 | 87.23% |
| 改口 | 35 / 40 | 87.50% |
| 没说完要跟进的事 | 38 / 42 | 90.48% |
| 相对日期 | 40 / 44 | 90.91% |
| 分散的线索 | 51 / 56 | 91.07% |
| 边界 | 62 / 68 | 91.18% |
| 助手自己说过的话 | 53 / 58 | 91.38% |
| 敏感的事 | 37 / 40 | 92.50% |
| 第三方事实 | 107 / 114 | 93.86% |
| 带条件或期限的偏好和边界 | 56 / 59 | 94.92% |
| 相似事件 | 38 / 40 | 95.00% |
| 时间约定 | 41 / 43 | 95.35% |
| 偏好 | 63 / 66 | 95.45% |
| 纠错 | 46 / 48 | 95.83% |
| 转述 | 43 / 44 | 97.73% |
| 假设 | 48 / 49 | 97.96% |
| 资料不足 | 55 / 56 | 98.21% |
| 计划假设梦转述猜测 | 64 / 65 | 98.46% |
| 生日 | 40 / 40 | 100.00% |
| 称呼条件 | 48 / 48 | 100.00% |

## 消耗与耗时

DeepSeek 平台账单（作答 + 判分）：**两次测评合计 3.57 元，平均每次 1.79 元**（按 token 计费口径，人民币；本地嵌入/重排不计费）。

| 档位 | 作答 QA tokens | topic 定稿 tokens | 判分 tokens |
| --- | ---: | ---: | ---: |
| 有 rerank（主） | 1,231,204 | 204,027 | 863,291 |
| 无 rerank（对照） | 1,182,554 | 206,027 | 861,712 |

- 一次测评 = 一个档位（整套 714 题：逐轮入库 + 作答 + 判分）。
- 墙钟耗时（同机顺序跑两档）：**全程约 1 小时 42 分**；其中无 rerank 作答约 31 分钟、有 rerank 作答约 44 分钟，两档判分各约 13 分钟；另含本地嵌入式建库与检索。

## 文件

| 文件 | 内容 |
| --- | --- |
| `answers.jsonl` | 714 题 `{id, answer}` 真实回答（有 rerank，主） |
| `reviews.jsonl` | 714 题判分记录（rubric 必答项、错误标记、理由、答案/标准哈希） |
| `judgments.jsonl` | `grade.py` 校验并汇总的逐题判定（有 rerank） |
| `summary.json` | `grade.py score` 机器可读汇总（分人物/考点/时距，有 rerank） |
| `runmeta.json` / `trace.jsonl` | 运行元数据与逐题召回 trace（有 rerank） |
| `answers-off.jsonl` / `reviews-off.jsonl` / `judgments-off.jsonl` / `summary-off.json` / `runmeta-off.json` / `trace-off.jsonl` | 无 rerank 对照档同构文件 |
| `unanswered.jsonl` | 未答题列表（空，全部已答） |
| `report.md` | 中文完整报告：配置、分项、失败模式、用量耗时 |
| `reproduce.md` | 复现配置/命令与哈希校验方法 |
| `scripts/` | 测评脚本子文件夹（`run.py` 接入适配器、`judge.py` 判分封装、`grade.py` 官方判分脚本），见其 `README.md` |
| `SHA256SUMS` | 全部文件 sha256 |

## 项目与版本

- 项目：**HitMind** —— 本地优先、轻量、多 Agent 共享的长期记忆服务（宿主无关 Core + SQLite）。
- 仓库：https://github.com/Fishskys/hitmind
- 版本：v0.1.0（`plugin.yaml` `version: 0.1.0`），commit **`8fc7a51`**。
- 接入方式：Hermes 记忆 Provider 插件（`hitmind/adapters/hermes`），基准适配器为仓库内 `adapters/hitmind/run.py`（外部 benchmark 侧，未随包发布）。

## 说明与限制

- 这是 1.0 六人物正式集（714 题），非 2.1 的 212 题开发集，两者成绩不可直接比较。
- 判分为 DeepSeek 自动语义判分，未人工抽查；不同判分模型/规则会有波动。
- 作答模型为 `deepseek-chat`（temperature=0），嵌入 `embeddinggemma-2`（本地 512 维），rerank 为本地 cross-encoder（见 `report.md`）。
- 未包含 API key、私聊原文、本地绝对路径或数据库文件。
