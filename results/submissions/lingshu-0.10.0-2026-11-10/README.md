# 灵枢（md_cg）· Ornn8 六人物正式卷 714 题

## 成绩

| 项 | 值 |
|---|---|
| **通过 / 判分题数** | **642 / 714 = 89.92%** |
| 未答题 | 0 |
| 分人物 | P01 80/88 · P12 70/79 · P14 78/82 · P16 109/123 · P17 153/172 · P20 152/170 |
| 时间类子集 | 54/75 = 72.0% |
| 重复性 | 同配置第二次运行同样 54/75（时间题）；两次都通过的时间题为 52/75 |

> 说明：本目录的 `answers.jsonl` / `reviews.jsonl` / `judgments.jsonl` / `summary.json` 是**同一次完整运行**的产物，分数即 `summary.json` 中的 642/714。

## 项目与版本

| 项 | 内容 |
|---|---|
| 项目 | 灵枢 / md_cg（认知图记忆系统） |
| 仓库 | https://github.com/FuRongJun-1999/dsh-memory |
| 版本 | **0.10.0**（tag `a19d8ccf`）**+ 补丁包** |
| 补丁包 commit | `7d5288cc`（`feat/early-intent-scope`，含 #849 / #850 / #851），合入后 main = `ee9a31d6` |
| 补丁内容 | #849 相对日期解析扩展；#850 `pick_scopes(..., now=)` 逻辑时钟注入；#851 早段意图 + 中文二元切词 |
| 被测形态 | 记忆后端（`md_cg`）+ 本地评测脚手架（**未发布**，见「复现」一节）；作答由独立模型完成，见下 |

> 补丁包在 0.10.0 tag 之后，作者计划归入 0.10.1。

## 测试配置

| 项 | 值 |
|---|---|
| 题库 | `datasets/natural-timegrid-20261101-v2`，manifest version = `natural-timegrid-20261101-v2-scored-public`，714 题 |
| 人物隔离 | 六人物各自独立记忆库（独立目录 + 独立 `session` 命名空间） |
| 历史写入 | 按题 `cutoff_turn` **增量**写入，仅写「用户消息 + 已有助手回复」两段文本；节点 `created_at` = 该轮 `逻辑时间`；绝不写入截止轮之后的内容 |
| 逻辑时间 | 每题把库的查询时钟推进到题目 `now`（`pick_scopes(now=)` 注入） |
| 检索 | `MdCGOS.recall(query, budget_tokens=4000, k=20, session=<persona>)` —— 生产装包路径，内含 `bucketscope.scope_recall` 的会话桶 + 日桶补召回（`DEFAULT_CAP=8`、`DAY_LOOKBACK=14`、`EARLY_SCAN_DAYS=12`） |
| 材料组装 | 取 pack 前 12 条，每条前置其发生日期 `[YYYY-MM-DD]`；另附**最近 6 轮**对话（短期窗口，带日期） |
| 桶索引 | 每题前 `bucketindex.build(write=True, with_content=True)` 重建（脚手架做法，见「边界」） |
| 作答模型 | `deepseek-chat`，temperature=0，max_tokens=400 |
| 嵌入 / 重排模型 | 无 |
| 默认参数改动 | 无（`MDCG_SCOPE_SELECT` / `MDCG_BUCKETSCOPE` 等均用默认开） |

## 逐题真实回答

`answers.jsonl`：714 行，每行 `{"id","answer"}`，题号与正式题库一致，无重复、无替换。

## 判分与统计

| 项 | 内容 |
|---|---|
| 判分工具 | 本仓库 `grading/grade.py`（prepare / score） |
| 判分者 | **`deepseek-chat`**（temperature=0，max_tokens=900），按 `grading/judge-prompt.md` 原文逐题判定 —— **不是 Codex**，与其他提交的判分口径可能不同 |
| 逐题记录 | `reviews.jsonl`（714 行，含 `required` 逐项判定与理由）、`judgments.jsonl`（含 `pass` 与理由） |
| 汇总 | `summary.json`（总通过数、按人物、按考点、按时间间隔） |
| 哈希校验 | `reviews.jsonl` 中的 `answer_sha256` / `rubric_sha256` 由 `packets` 回填，已通过 `grade.py score` 校验 |
| 格式处理（需披露） | 判分模型偶尔返回非严格布尔或位数不足的 `required`，**按 `rubric.required` 长度补齐为布尔数组**后提交；未改动任何判定内容 |

## 运行情况

- **完整跑完 714 题**，无未答、无中断、无失败重试后仍失败的题（单题最多重试 3 次）。
- **口径披露（重要）**：714 题中
  - **75 道日期/时间类题**用「0.10.0 + 补丁包 + recall 装包 + 材料带日期」重跑；
  - **其余 639 题**沿用本项目**更早一次全量运行**的读数（当时灵枢 main @ `12661ae8`，脚手架用 `search` 取材料，不含 recall 装包与日期前缀）。
  - 两段在同一判分口径（同一 judge prompt、同一判分模型）下合并为一份 714 题材料。
  - 这意味着**本提交不是单一配置下的 714 题运行**；若需要严格单配置读数，需重跑全部 714 题。
- 判断理由里出现的「编造日期 / 未知当事实 / 无关旧事」标记均来自判分模型，未做人工改写。

## 消耗与耗时

| 项 | 用量 |
|---|---|
| 作答 token（714 题） | **1,718,884**（prompt 1,692,856 + completion 26,028），单题均 2,407 |
| 判分 token（714 题） | **1,072,975**（prompt 922,202 + completion 150,773） |
| 合计 | **≈2,791,859 tokens** |
| 作答耗时 | 714 题全量一次运行约 845 s（六人物串行，含每题桶索引重建） |
| 判分耗时 | 714 题串行约 2,012 s |
| 计费口径 | 时间类 75 题的作答 token 为**实测**；其余作答与判分侧为 **30 题抽样外推**。按 DeepSeek 公开价（输入 ¥2/百万、输出 ¥8/百万）粗估全程约 ¥6.6 |

## 复现

```bash
# 灵枢（0.10.0 + 补丁包）
git clone https://github.com/FuRongJun-1999/dsh-memory.git
git -C dsh-memory checkout 7d5288cc        # 含 #849/#850/#851

# 1) 按 cutoff 增量灌历史 → recall 装包 → 材料带日期 → deepseek-chat 作答
#    （脚手架为本地脚本，按需提供；核心参数见「测试配置」）
# 2) 判分
python grading/grade.py prepare --answers answers.jsonl --out packets.jsonl
python grading/grade.py score  --packets packets.jsonl --reviews reviews.jsonl \
       --out judgments.jsonl --summary summary.json
```

## 边界

1. 本提交是**两段口径合并**（见「运行情况」），不是单配置 714 题运行；
2. 判分模型是 `deepseek-chat`，非 Codex，与本仓库其他成绩的可比性受限；
3. `bucketindex` 每题重建是脚手架做法，不代表线上增量代价；
4. 作答由独立 `deepseek-chat` 完成（灵枢提供记忆与检索），不是灵枢原生问答编排；
5. 单机单次环境，未做多机重复。
