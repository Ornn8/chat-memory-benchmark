# 已测项目、配置与局限

这份记录列出已出成绩的项目、上游版本和测试配置。上游项目可能继续变化，复查应使用下面固定的 commit。

| 系统 | 作者署名 | 上游与已测版本 |
| --- | --- | --- |
| 冷热记忆方案（ARCHEON） | 原无奇变 / ARCHEON999 | [ARCHEON999/Companion-AI-Memory-Context-Token-Optimization](https://github.com/ARCHEON999/Companion-AI-Memory-Context-Token-Optimization) · [`dec675c`](https://github.com/ARCHEON999/Companion-AI-Memory-Context-Token-Optimization/tree/dec675cb01a4a0eb41d770972b783900b3387f87) |
| SeekMemory | BangBang在coding / NeverENG | [NeverENG/SeekMemory](https://github.com/NeverENG/SeekMemory) · [`8aaa7ee`](https://github.com/NeverENG/SeekMemory/tree/8aaa7eec7a069ec1da6b414d61adc25257e3cd9a) |
| digital-life-core | 温水 / mashangshui | [mashangshui/digital-life-core](https://github.com/mashangshui/digital-life-core) · [`d984665`](https://github.com/mashangshui/digital-life-core/tree/d984665ff2e452cf9f57d845cfb93bfb9a64b6b1) |
| dsh-soul | 糖霜Official | [icyaaaww/dsh-soul](https://github.com/icyaaaww/dsh-soul) · [`8a95301`](https://github.com/icyaaaww/dsh-soul/tree/8a953010bdc97b54cb6be2e9b3793ec7a81317a6) |
| SurfCore | 玛露Marrow | [Mieksido/surfcore](https://github.com/Mieksido/surfcore) · [`59ec306`](https://github.com/Mieksido/surfcore/tree/59ec3066f7d42a0452fae01f170c9a8484d5dbe5) |
| SurfCore BGE-M3 向量重测 | 玛露Marrow | [Mieksido/surfcore](https://github.com/Mieksido/surfcore) · [`0ce8580`](https://github.com/Mieksido/surfcore/tree/0ce8580048d3dddb21860114edb8b115d5d79d1e)（0.8.9） |
| dsh-rofm | 鄙人乃路人甲 | [wall1234567/dsh-rofm](https://github.com/wall1234567/dsh-rofm) · [`a51ed67`](https://github.com/wall1234567/dsh-rofm/tree/a51ed67607a40ea6d88b38f5ac12b9792eae681a) |
| dsh-rofm 1.4.2（重测） | 鄙人乃路人甲 | [wall1234567/dsh-rofm](https://github.com/wall1234567/dsh-rofm) · [`ef3e20e`](https://github.com/wall1234567/dsh-rofm/tree/ef3e20e30582b59bddb9308c629793b44bfc567f) |
| OpenViking 0.5.2.1 | 火山引擎 | [volcengine/OpenViking](https://github.com/volcengine/OpenViking) · [`f5e6203`](https://github.com/volcengine/OpenViking/tree/f5e6203033a13469c3d9a937f2ca39492ea69c51) |
| Suzu 原生重测 | eryucheng | [eryucheng/dsh-suzu-memory](https://github.com/eryucheng/dsh-suzu-memory)，使用 Suzu core `645c862470b1a207c9904e614083f8b77a8f15bf` |
| Suzu 强制原生检索重测 | eryucheng | [eryucheng/dsh-suzu-memory](https://github.com/eryucheng/dsh-suzu-memory)，同一 Suzu core `645c862470b1a207c9904e614083f8b77a8f15bf` |
| Hindsight 1.2.0 | Vectorize | [vectorize-io/hindsight](https://github.com/vectorize-io/hindsight) · [`34a1386`](https://github.com/vectorize-io/hindsight/tree/34a138684a899b6ec34175f7a2b633860466d289) |
| Qwen RAG | 本评测搭建的对照 | Qwen 嵌入、重排，加统一作答模型；不是另一个社区记忆项目 |

作者署名按提交测试时提供的信息记录。仓库仅链接上游，不包含其代码或表示其背书。

## 共用设置

既有对话逐轮回放，考试使用对应截止点的记忆。作答使用 DeepSeek；不同批次可能使用不同渠道，Suzu 重测中途由 OpenCode Go 切换到 DeepSeek 官方渠道。本记录不能替代完整 provider 版本快照。发布时间不代表模型参数保证永远不变。

直接聊天与持久记忆分开核验。历史输入不含答案、判据和未来对话；题目答案不反哺其他题。考试模型和记忆维护调用分别记录，固定历史回放本身不要求重生成助手回复。

## dsh-neo4j-memory（作者侧自测）

插件作者侧按自然日合并多轮回放，考试截止点拆分，使用隔离数据库、最近六轮和模型自主检索。测试基于插件 `2756ba2` 检索实现，入库使用当时未提交改动，不能视为已发布版本的精确复现。DeepSeek 初判 682 / 714，作者及维护者共抽查 28 题后为 684 / 714；判分者差异见[实验记录](../results/2026-11-05-dsh-neo4j.md)。本仓库维护者尚未独立复现。

## dsh-memu-memory 1.2.7（作者侧自测）

插件作者侧按考试截止点增量回放冻结历史，每个截止点先完成该段记忆整理，再重建记忆库后作答；每个人物使用独立私有库。测试固定插件 `1.2.7`（提交 `6df299c`）、DSH 宿主 `0.2.2-rc.1`、MemU `0.11.0b3`；记忆后端 `api`、向量来源 `local`、嵌入 `multilingual-e5-small`（int8 ONNX，384 维），召回为 `managed-vector-rrf`（向量与词法 RRF 融合）。作答提供最近六轮加插件召回，矛盾条目双方保留、由作答模型自行取舍。作答与判分使用 `dys-router` / `deepseek-v4.1-flash`（作答思考强度 high），按 rubric 信息点填空判分，DeepSeek 初判 653 / 714；未做人工抽查。判分方式与其他记录使用的 Codex 初判不同，不宜严格横比。测试工具见 [`Tkingxiao/memu-bench-714`](https://github.com/Tkingxiao/memu-bench-714)，记录见[实验报告](../results/2026-11-06-dsh-memu-memory.md)。

## 冷热记忆方案（ARCHEON）

按作者公开设计、配置示例和提示词复现，并非直接运行作者交付的完整程序。逐逻辑日整理记忆卡，近期内容常驻，旧内容逐步摘要并放入冷库；提问时判断线索，最多召回三条旧记忆，另加最近六轮。复现使用本地 bge 向量检索，阈值沿用示例配置。

已完成新卷 714 题，整题通过 356 题。成绩同时受我们复现方式影响，不能写成作者原版成品程序的实测。见[之前四路完整成绩](../results/2026-11-01-first-four.md)。

## SeekMemory

运行原版 AstrBot 插件，由模拟事件宿主回放固定聊天；没有连接真实平台账号。原始消息作为证据存储，原插件负责提取、整理和召回，再加最近六轮交给统一作答模型。

**本次开启定时整理和 Dream，关闭空闲抽取，用测试时钟推进原生后台整理。** 开启机制不等于每次整理都成功；提取失败和运行中断保留记录，考试使用当时实际已有的记忆，不由评测器补答案。

已完成新卷 714 题，整题通过 230 题。早期恢复过程中，评测驱动曾把原插件已重试成功的历史提取错误仍视为失败；这是驱动判断问题，修复记录与插件原始提取失败分别保留，不能全部归咎于上游。

## digital-life-core

原版核心与 memory-v2 在 DSH 内运行。按日期分批通过文档提供的迁移入口导入固定聊天，由原程序决定如何保存记忆；考试从原生对话入口进行，使用原生记忆投影和工具，另外带最近六轮。

本次关闭联网、自改源码、后台定时 Dream 和主动唤醒，不代表默认实时聊天模式，也不评自主生活能力。已完成新卷 714 题，整题通过 233 题。

固定版本中自带的 `energy-stipend` 模块缺少宿主调用的 `getPromptContext`，出现接口错误；宿主捕获后继续，相关上下文为空。保留这一观察，没有在测试里静默修改上游；尚未证明该错误导致记忆丢失或某道题失分，不能用它解释全部低分。

## dsh-soul

通过原生 AgentLoop 回放固定对话，保留原生图谱、索引、记忆和工具。考试使用新会话 ID、同一人物范围，直接聊天最多最近六轮。没有额外 RAG。

本轮未运行 `/mem sleep` 手动睡眠整理，因此成绩不代表启用该机制后的效果。714 条答案中，713 条有可逐项核验的原始输入边界，另 1 条只有用量记录；不能宣称完整审计了 714 条输入。

## SurfCore

通过隔离的文字传输进入原生 QQ 会话流程，使用原生记忆卡、维护、衰减、工具和实际发送结果。每轮及考试前按逻辑时间处理维护。没有另外外挂检索或自动补全历史。

只把真正向用户发送的消息记为回答；原生流程没有发出回复时如实记沉默。已核验 714 条考试调用的输入边界。本轮未测试真实 QQ 连接、语音、图片和手机端体验。

## dsh-rofm

默认配置约需 80 万 token 才触发归档，超轻度历史不足以触发。经事先确定，仅在**测试副本的历史回放阶段**把工作窗口设为 8,000 token，保留原生 80% 触发规则和实际 token 度量，不加入无关填充文本。

考试阶段宿主窗口恢复 1,000,000 token，但直接旧聊天仍最多最近六轮；更早内容靠原生归档、评分与召回。维护输出上限 8,000、作答上限 2,500 是测试网关设置，不是上游默认值。未归档且已超出短期窗口的尾段，没有额外补给作答模型。

在该降低阈值的配置中，系统把维护工具记录再次归档，持续产生评分任务，触及 12 轮维护保护上限。最终完成 687/714 题，27 题未答；保留中断，不继续换配置混分。**这个现象不能直接推断为默认阈值下也必然发生。**

另观察到模型提交不存在的文件夹 ID，原生工具进行了拒绝；这不等同于证明纯粹的代码错误。

早期适配器曾把过小窗口带到考试阶段，压缩掉当前考题，且维护输出上限过小造成截断。这些属于评测侧问题，相关旧结果已撤出本轮比较。当前结果只使用修订后的实验，仍保留上述系统在测试配置下的中断限制。

## OpenViking 0.5.2.1

使用独立服务处理各人物的历史和记忆；考试按该题可见历史前缀读取快照，直接对话最多保留最近六轮，未额外接入 RAG。完成 714 题，Codex 初判 555 题通过。

## Suzu 原生重测

按 Suzu core 原生机制增量处理历史，在各考试节点整理待处理的历史，并提供最近六轮及记忆检索工具。每次工具检索默认和最多返回 10 条、最多 10,976 字符，每题最多检索 6 次；不是整题合计只能召回 10 条。使用 `text-embedding-v4`、1,024 维。重测完成 714 题，Codex 初判 516 题通过。

本次由作答模型决定是否调用 Suzu 检索工具，没有在每题开头强制检索；714 题中有 351 题未调用该工具。按题目各项事实标注的证据轮次与最近六轮交集粗算，其中 185 题每项事实至少一处证据在最近六轮，25 题部分命中，141 题没有命中；这 141 题中 108 题未通过。证据轮次命中不保证具体内容足以单独答题，也不能据此断言所有未通过均由未检索导致。

此前测试在清理直接上下文前没有先整理未归档尾段，旧的 329 / 714 不作为公平成绩。本次采用修正后的接入；两个成绩分别保留，不混算。

## Suzu 强制原生检索重测

使用同一份六人物、714 题题库及相同 Suzu core，逐轮处理历史，在考试节点先完成原生记忆整理。每题以问题原文强制调用一次 Suzu 原生检索，最多返回 10 条，再与最近六轮对话一起交给 DeepSeek 官方渠道作答；向量模型为 `text-embedding-v4`，1,024 维。本轮不保存记忆快照。

714 题均执行检索，5 题没有匹配结果；整题初判通过 **621 / 714**。Qwen 对照复用此前的 **596 / 714**，其语义检索最多取 40 条候选、重排至最多 10 条，使用的调用渠道和检索流程与 Suzu 不同。完整成绩及分考点结果见[本轮报告](../results/2026-11-05-suzu-forced.md)。

## Hindsight 1.2.0

按时间戳增量写入既有用户与助手对话，每个考试节点克隆独立记忆库并使用原生召回，另提供最近六轮；考题和答案不写回历史。嵌入与重排使用 Hindsight 本地默认设置。714 题 Codex 初判通过 513 题。

## dsh-rofm 1.4.2 重测

使用 8,000 token 测试窗口，考试时保留原生未归档会话尾段以及原生记忆。714 题 Codex 初判通过 471 题；Qwen 对照沿用原有 596 题通过。这次重测与上面旧版中断的 687 题结果分列，接入与题数不同，不合并成一条成绩。

## Qwen RAG 对照

将每轮用户消息和助手回复作为一块，嵌入检索最多 40 块，再重排取最多 10 块，按时间顺序提供给作答模型，另加最近六轮。检索范围限制在该题可见历史前缀，回答仍由统一 DeepSeek 模型生成。

本地运行记录中的嵌入标识为 `qwen3.7-text-embedding`，重排标识为 `qwen3.7-text-rerank`，维度 2,560。这里只记录本轮使用标识，不宣称它们是任何时间、任何地区均可用的默认型号。

本轮沿用已有答案和判分，未重复跑 Qwen。这个对照衡量的是“找出相关旧话再作答”的整套流程，不是只测试一个嵌入模型的裸能力。

## 早期还跑过的诊断对照

旧卷中还试跑过无记忆、最近 20 轮、全量上下文、朴素向量检索，以及“一律含糊”“全倒出来”两种检验判分是否有效的反例。这些不是新增社区项目；旧卷评分、样本覆盖与当前新卷不同，不并入当前成绩表，也不把全量上下文当作长期记忆机制的成绩。

## SurfCore BGE-M3 向量记忆（同上游重测）

上游：[Mieksido/surfcore](https://github.com/Mieksido/surfcore) · [`0ce8580`](https://github.com/Mieksido/surfcore/tree/0ce8580048d3dddb21860114edb8b115d5d79d1e)（0.8.9）

**接入性质：使用原生向量记忆模块，但不是真实 QQ bridge 会话。** 隔离 harness 直接调用 `src/vector-memory.js`，没有改动线上配置，也没有真实平台连接。

接入流程：

1. 六个人物的历史按轮调用 `recordsFromInboxLines` + `mergeVectorRecords` 写入本地 BGE-M3 索引；用户 `isOwner=true`、助手 `isSelf=true`、同一私聊 `conversationKey`，助手事件 +1 秒。
2. 每个 cutoff 生成当时可见的前缀快照，按 `createdAt <= cutoff + 1s` 且 `recordTurn <= cutoff` 过滤。
3. 每题用当前问题作为 query 调 `rankVectorMemories`（topK = 4、minScore = 0.4），再用 `renderVectorRecallBlock` 注入最多 600 字符。
4. 作答输入 = 向量召回块 + 最近 5 个完整回合 + 当前逻辑时间 + 当前问题；不含完整历史、答案、rubric、evidence。
5. 每题独立会话，考试不写回。

与原生系统的差异（写清楚，便于按同一把尺子解读）：

- **没有真实 QQ 连接、语音、图片、文件、手机端体验**；这些题按“检索不到”处理。
- 使用隔离 harness 直接调用原生向量模块，不是线上 bridge 的一份运行实例。
- 嵌入是本地 BGE-M3（Ollama 0.40.15、RTX 4060 Laptop、1024 维、`bge-m3@1024-f16-v1`），不是远程 embedding。
- 与 2026-11-01 的 SurfCore 记忆卡记录（123 / 714）不是同一配置：那条是记忆卡 + 真实 QQ 文字传输，本条是向量检索路径，分数不能直接当作升级收益。

本次分数说明：

- **605 / 714**。逐题 `reviews` 由提交方按 `judge-prompt.md` 让 DeepSeek 判定，`grade.py` 只负责校验与汇总；**不是维护方独立判分**，是否入表与正式成绩以维护方复判为准。
- 没有人工抽查修正；只提交一个判分口径。
- 自动校验：714 条答案与 714 条判定题号全匹配、无重复、无空答案；未来记录泄漏 0；prompt 中 rubric / answer_sha256 / evidence / fact_id 标记 0；工具调用 0。
- 答卷与判定可直接复算：`prepare` + `score` 应输出 `Passed 605 / 714`。报告同目录的 `-summary.json` 是仿榜单格式整理（含考点 × 时间档 cells、来源哈希、检索与成本），`-grading-summary.json` 是 `grade.py` 直出。

**历史 SHA**（题库发布包自带，未改动）：

| 人物 | 文件 | SHA-256 |
|---|---|---|
| P01 | `histories/P01.jsonl` | `5073b1f9…53f198` |
| P12 | `histories/P12.jsonl` | `9d762423…528223` |
| P14 | `histories/P14.jsonl` | `030dcaf5…3aeced` |
| P16 | `histories/P16.jsonl` | `3b51c824…5632e5` |
| P17 | `histories/P17.jsonl` | `a8b5b1f7…f7851d` |
| P20 | `histories/P20.jsonl` | `847ac8c7…21dc4f` |

**是否中断**：无中断，714 题全部作答（0 缺、0 空、0 重复）。

**实际读取的记忆状态**：每题使用该 cutoff 的向量索引前缀快照；历史逐轮写入，考试阶段不写回。可见范围由快照的 `createdAt` 与 `recordTurn` 双重过滤控制。本地嵌入服务与索引均为隔离副本，未改动线上 SurfCore 配置。

**费用**：按 DeepSeek 官方价逐调用估算，作答约 ¥1.70、判分约 ¥2.60，合计约 ¥4.30；本地 BGE-M3 嵌入无远程 API 费用，失败重试为 0 token。
