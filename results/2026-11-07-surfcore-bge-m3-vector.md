# 六人物记忆系统评测：11 月 7 日 SurfCore BGE-M3 向量记忆

使用同一六人物、714 题正式卷。

这次测的是 **SurfCore 的原生向量记忆路径**（`memory.mode = vector`），不是仓库 2026-11-01 记录的叙事记忆卡流程。六个人物的历史逐轮写入本地 BGE-M3 向量索引，每个截止点生成当时可见的快照，再用当前问题检索 top 4，连同最近 5 轮和当前时间交给统一作答模型。具体接入与局限见[测试配置](../docs/tested-configurations.md)。

## 总成绩

| 判分口径 | 通过 / 题数 |
| --- | ---: |
| 官方 judge prompt + `grade.py` 校验汇总 | 605 / 714 |

判分没有做人工抽查修正；605 是逐题 `reviews` 经 `grade.py` 校验与汇总的结果。**分数为提交方自检，不是维护方独立判分**，是否入表与正式成绩以维护方复判为准。

## 不同时间间隔

| 间隔 | 判定 |
| --- | ---: |
| 0 天 | 169 / 189 |
| 3 天 | 161 / 184 |
| 15 天 | 144 / 174 |
| 45 天 | 131 / 167 |

## 各考点

一题可属于多个考点；每行按整题是否通过统计，不能相加。

| 考点 | 判定 |
| --- | ---: |
| 第三方事实 | 95 / 114 |
| 边界 | 65 / 68 |
| 偏好 | 53 / 66 |
| 计划 | 52 / 65 |
| 计划假设梦转述猜测 | 61 / 65 |
| 带条件或期限的偏好和边界 | 53 / 59 |
| 真实变化 | 47 / 58 |
| 助手自己说过的话 | 40 / 58 |
| 分散的线索 | 41 / 56 |
| 用户的基本信息 | 49 / 56 |
| 资料不足 | 51 / 56 |
| 约定和欠账 | 35 / 55 |
| 职业 | 44 / 51 |
| 假设 | 45 / 49 |
| 称呼条件 | 45 / 48 |
| 纠错 | 45 / 48 |
| 时间题 | 27 / 48 |
| 没解释的矛盾 | 34 / 47 |
| 相对日期 | 29 / 44 |
| 转述 | 38 / 44 |
| 共同编的故事 | 34 / 43 |
| 时间约定 | 32 / 43 |
| 没说完要跟进的事 | 38 / 42 |
| 改口 | 37 / 40 |
| 敏感的事 | 39 / 40 |
| 生日 | 39 / 40 |
| 相似事件 | 37 / 40 |

[答卷](2026-11-07-surfcore-bge-m3-vector-answers.jsonl) · [逐题判定](2026-11-07-surfcore-bge-m3-vector-reviews.jsonl) · [`grade.py` 直出](2026-11-07-surfcore-bge-m3-vector-grading-summary.json) · [整理版汇总](2026-11-07-surfcore-bge-m3-vector-summary.json)

答卷与逐题判定同源：按 [`grading/README.md`](../grading/README.md) 跑 `prepare` + `score` 可复算 605 / 714。

## 接入与差异

接入流程：

1. 六个人物的历史按轮调用 SurfCore 原生 `recordsFromInboxLines` + `mergeVectorRecords` 写入索引；用户消息 `isOwner=true`，助手消息 `isSelf=true`，同一私聊 `conversationKey`，助手事件时间 +1 秒。
2. 每个 cutoff 生成当时可见的前缀快照，按 `createdAt <= cutoff + 1s` 且 `recordTurn <= cutoff` 过滤；未来记录不参与。
3. 每题用当前问题作为 query，调用原生 `rankVectorMemories`（topK = 4、minScore = 0.4），再用 `renderVectorRecallBlock` 注入最多 600 字符。
4. 作答输入 = 向量召回块 + 最近 5 个完整回合（10 条消息）+ 当前逻辑时间 + 当前问题；不提供完整历史、标准答案、rubric、evidence 或外部检索。
5. 每题独立会话，工具调用 0；考试不写回记忆。

与仓库已有 SurfCore 记录的区别：

- 2026-11-01 的 SurfCore 123 / 714 是原生**记忆卡**流程，经过真实 QQ 文字传输；本次是同一上游 0.8.9 的另一条**向量记忆**路径，用隔离 harness 直接调用 `src/vector-memory.js`。两者不是同一配置的版本前后，分数不能直接当作升级收益。
- 没有真实 QQ 连接、语音、图片、文件、手机端体验；本次题库里的多模态题按“检索不到”处理。
- 嵌入是本地 BGE-M3，不是远程 embedding；作答与判分仍是统一的 DeepSeek。

## 复算

```sh
python grading/grade.py prepare \
  --answers results/2026-11-07-surfcore-bge-m3-vector-answers.jsonl \
  --out packets.jsonl
python grading/grade.py score \
  --packets packets.jsonl \
  --reviews results/2026-11-07-surfcore-bge-m3-vector-reviews.jsonl \
  --out judged.jsonl \
  --summary summary.json
```

第二条应输出 `Passed 605 / 714`。

## 历史 SHA

题库发布包自带，未改动：

| 人物 | 文件 | SHA-256 |
|---|---|---|
| P01 | `histories/P01.jsonl` | `5073b1f9…53f198` |
| P12 | `histories/P12.jsonl` | `9d762423…528223` |
| P14 | `histories/P14.jsonl` | `030dcaf5…3aeced` |
| P16 | `histories/P16.jsonl` | `3b51c824…5632e5` |
| P17 | `histories/P17.jsonl` | `a8b5b1f7…f7851d` |
| P20 | `histories/P20.jsonl` | `847ac8c7…21dc4f` |

## 是否中断

无中断，714 题全部作答（0 缺、0 空、0 重复）。

## 实际读取的记忆状态

每题使用该 cutoff 的向量索引前缀快照；历史逐轮写入，考试阶段不写回。题库历史在回放阶段全部进入索引，可见范围由快照的 `createdAt` 与 `recordTurn` 双重过滤控制。本地嵌入服务与索引均为隔离副本，未改动线上 SurfCore 配置。

## 费用

按 DeepSeek 官方价逐调用估算：作答 714 题约 ¥1.70，判分 91 个会话约 ¥2.60，合计约 **¥4.30**。本地 BGE-M3 嵌入不产生远程 API 费用；30 个失败重试会话为 0 token。不含电费与 Codex 开发会话。
