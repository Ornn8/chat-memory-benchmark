# 测评脚本（本目录为投稿附带的可复现脚本副本）

本子文件夹收录了复现本次 714 题成绩所用的脚本副本，供投稿审阅与复核。注意：这些脚本属于 **chat-memory-benchmark 基准工程侧**，不是 HitMind 包本体（HitMind 见仓库 https://github.com/Fishskys/hitmind ，commit `8fc7a51`）。

| 脚本 | 来源（本 benchmark 仓库） | 作用 |
| --- | --- | --- |
| `run.py` | `adapters/hitmind/run.py` | HitMind 接入适配器：按人物隔离库、逐轮 `Engine.capture(raw)` 入库、按 `cutoff_turn` 到点 `recall(top_k=10)` → 拼 `[id] (kind)[@date]：原文` → 交作答模型 → 产出 `answers.jsonl` 与 `trace.jsonl`。支持 `--no-rerank` 开关跑对照档。 |
| `judge.py` | `adapters/hitmind/judge.py` | 判分封装：读取 `grading/grade.py prepare` 生成的 packets，按 `grading/judge-prompt.md` 规则调用判分模型逐题产出 `reviews.jsonl`。 |
| `grade.py` | `grading/grade.py`（官方判分脚本，未改动） | `prepare`（生成判分 packets）/ `score`（校验题号与哈希，汇总为 `judgments.jsonl` + `summary.json`）。 |

## 使用前提与路径

- 这两个适配脚本按**相对路径**定位基准仓库与 HitMind 源码根：
  - `run.py`：`BENCH = HERE.parents[1]`（= `references/chat-memory-benchmark`）、`REPO = HERE.parents[3]`（= HitMind 仓库根）；并把 `REPO` 插入 `sys.path` 以 `from hitmind.core.engine import Engine`。
  - `judge.py`：`BENCH = HERE.parents[1]`。
- 因此若要直接运行，请把本 `scripts/` 目录放回基准仓库的 `adapters/hitmind/`（即其 `parents[1]` 指向 `references/chat-memory-benchmark`、`parents[3]` 指向 HitMind 源码根），或等效设置 `sys.path`。此处随投稿附带的副本仅用于**审阅与对照**。
- 依赖：本地 OpenAI 兼容嵌入服务（`embeddinggemma-2`, 512 维）与本地 cross-encoder `/rerank` 端点；作答/判分调用 DeepSeek `deepseek-chat`。API key 通过环境变量读取，脚本本身不含任何密钥。

## 复现命令

见上级目录 `reproduce.md`。概要：
```sh
python adapters/hitmind/run.py --no-rerank --out outputs/answers-714-aligned-off.jsonl --trace-out outputs/trace-714-aligned-off.jsonl
python adapters/hitmind/run.py             --out outputs/answers-714-aligned-on.jsonl  --trace-out outputs/trace-714-aligned-on.jsonl
python grading/grade.py prepare --answers outputs/answers-714-aligned-on.jsonl --out outputs/packets-714-aligned-on.jsonl
python adapters/hitmind/judge.py --packets outputs/packets-714-aligned-on.jsonl --out outputs/reviews-714-aligned-on.jsonl
python grading/grade.py score --packets outputs/packets-714-aligned-on.jsonl --reviews outputs/reviews-714-aligned-on.jsonl --out outputs/scores-714-aligned-on.jsonl --summary outputs/summary-714-aligned-on.json
```
