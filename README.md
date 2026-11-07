# 大肥鱼 · 聊天记忆系统评测

各种记忆框架，到底能记住什么，又会忘掉什么？这个项目把长时间聊天中的事实、改口、约定和边界整理成可检查的题目，用同一套规则比较不同系统。

目前关注**每天约两轮、跨度最长半年**的超轻度聊天场景。一轮指一条用户消息和一条助手回复。它不代表高频聊天、多人群聊或真实用户的全部使用情况。

**现已公开正式六人物测试集：完整合成历史、714 道正式题、评分标准与证据，以及离线读题工具。** 此外保留了独立的单人物示例；示例与正式卷不是同一份数据。

## 交给 Codex 测试

把下面这段话发给 Codex，并填上要测试的项目地址或本地路径：

```text
请使用 https://github.com/Ornn8/chat-memory-benchmark 测试这个聊天记忆系统：[项目地址或本地路径]。
请先阅读仓库的测试方法、接入说明和判分说明，再按照六人物正式测试集完成接入、作答和判分，给我总成绩、各考点成绩和测试配置。历史交给被测系统的记忆流程处理，考试时不要把完整历史或标准答案直接交给作答模型。请保留实际回答和判分结果。
```

Codex 会根据项目的接入方式完成测试，并使用本仓库的判分规则整理成绩。

## 用图片看结果

最新制作了 **7 张 1800 × 2200 高清图**：Suzu 强制原生检索与 Qwen 对照的测试消费、总成绩，以及覆盖全部 27 个考点的 5 张分组图，比较同一批 714 题。

[查看 Suzu 和 Qwen 的七张图](charts/2026-11-05-suzu-forced/README.md) · [查看之前七路共同题图集](charts/2026-11-01/README.md)

![Suzu 和 Qwen 测试消费，人民币](charts/2026-11-05-suzu-forced/01-cost.png)

![Suzu 和 Qwen 的 714 题总成绩](charts/2026-11-05-suzu-forced/02-overall.png)

## 已经测过哪些

查看[截至 2026 年 11 月 7 日的成绩盘点](results/2026-11-07-recap.md)。下面保留此前已公开成绩的项目目录：完整卷和共同已答题的范围不同，比较请看各行链接里的同卷成绩。

| 项目／上游 | 作者 | 测试状态与成绩（通过 / 已答） |
| --- | --- | --- |
| [冷热记忆方案（ARCHEON）](https://github.com/ARCHEON999/Companion-AI-Memory-Context-Token-Optimization) | 原无奇变 / ARCHEON999 | 按公开方案复现；完整卷 [356 / 714](results/2026-11-01-first-four.md) |
| [SeekMemory](https://github.com/NeverENG/SeekMemory) | BangBang在coding / NeverENG | 原版插件，开启 Dream；完整卷 [230 / 714](results/2026-11-01-first-four.md) |
| [digital-life-core](https://github.com/mashangshui/digital-life-core) | 温水 / mashangshui | 原生核心与迁移入口；完整卷 [233 / 714](results/2026-11-01-first-four.md) |
| [dsh-soul](https://github.com/icyaaaww/dsh-soul) | 糖霜Official | 完整卷 418 / 714；合辑共同题 [402 / 687](results/2026-11-01.md) |
| [SurfCore](https://github.com/Mieksido/surfcore) | 玛露Marrow | 完整卷 123 / 714；合辑共同题 [122 / 687](results/2026-11-01.md) |
| [dsh-rofm](https://github.com/wall1234567/dsh-rofm) | 鄙人乃路人甲 | 1.4.2 重测初判 [471 / 714](results/2026-11-04.md)；旧版测试中断，保留 [242 / 687](results/2026-11-01.md) |
| [OpenViking](https://github.com/volcengine/OpenViking) | 火山引擎 | 0.5.2.1 初判 [555 / 714](results/2026-11-04.md) |
| [dsh-suzu-memory](https://github.com/eryucheng/dsh-suzu-memory) | eryucheng | 强制原生检索重测初判 [621 / 714](results/2026-11-05-suzu-forced.md)；自主决定是否检索的上一轮 [516 / 714](results/2026-11-04.md) |
| [Hindsight](https://github.com/vectorize-io/hindsight) | Vectorize | 1.2.0 初判 [513 / 714](results/2026-11-04.md) |
| dsh-biocore 0.4.0 | 未标注 | **不可用**：测试历时约 34 小时，仅完成 58 / 714 题后停止；[查看记录](results/2026-11-07-recap.md) |
| [dsh-neo4j-memory](https://github.com/shuunO-O/dsh-neo4j-memory) | shuunO-O | 作者自测；DeepSeek 初判及部分抽查后 [684 / 714](results/2026-11-05-dsh-neo4j.md)，判分者与其他项目不同 |
| [dsh-memu-memory](https://github.com/Tkingxiao/dsh-memu-memory) | Tkingxiao | 作者自测；1.2.7 初判 [653 / 714](results/2026-11-06-dsh-memu-memory.md)，判分者与其他项目不同 |
| [dsh-plugin-memory-graph（大肥鱼好记性）](https://github.com/YeStarOne/dsh-plugin-memory-graph) | YeStarOne | 作者侧自测、glm-5.3-flash 单票自判 [502 / 714](results/2026-11-07-dsh-plugin-memory-graph.md) |
| Qwen RAG（本评测搭建的检索对照） | Qwen 模型团队；检索流程由本评测搭建 | 完整卷 [596 / 714](results/2026-11-01-first-four.md)；合辑共同题 [574 / 687](results/2026-11-01.md) |

各项目的固定版本、实际接入方式、维护开关和局限统一放在[测试配置与局限](docs/tested-configurations.md)。作者署名沿用评测登记信息。

## 作者自测投稿

[dsh-neo4j-memory 六人物测试记录](results/2026-11-05-dsh-neo4j.md)：插件作者侧运行，DeepSeek 初判 682 / 714；作者抽查 26 题、维护者另抽查修正 2 题后为 684 / 714。适配方式和判分者与其他记录不同，人工抽查未覆盖全部题目；该结果不是维护者独立复现的成绩。

[dsh-memu-memory 1.2.7 六人物测试记录](results/2026-11-06-dsh-memu-memory.md)：插件作者侧运行，按考试截止点增量回放并重建记忆，DeepSeek 初判 653 / 714；未做人工抽查，判分方式与其他记录不同；测试工具见 [Tkingxiao/memu-bench-714](https://github.com/Tkingxiao/memu-bench-714)。该结果不是维护者独立复现的成绩。

## 从哪里开始

| 你想做什么 | 看这里 |
| --- | --- |
| 看考什么、怎么判 | [测试方法](docs/methodology.md) |
| 看各项目的逐题回答 | [逐题答卷](results/answers/README.md) |
| 下载完整正式测试集 | [六人物正式测试集](datasets/README.md) |
| 给自己的测试回答判分 | [判分工具、证据和使用方法](grading/README.md) |
| 直接看示例题、答案和证据 | 下载仓库后打开 [示例题.html](demo/示例题.html)，或在线读 [示例题.md](demo/示例题.md) |
| 把示例接到自己的系统 | [接入说明](docs/integration.md)、[读题工具](demo/read_exam.py) |
| 核对所有已测系统版本和配置 | [测试配置与局限](docs/tested-configurations.md) |
| 看之前四期的完整成绩 | [冷热方案、SeekMemory、digital-life-core、Qwen：714 题](results/2026-11-01-first-four.md) |
| 看新增三项目合辑的成绩 | [Soul、SurfCore、ROFM、Qwen：共同 687 题](results/2026-11-01.md) |
| 看最新测试和重测 | [OpenViking、Suzu、Hindsight、ROFM、Qwen：714 题初判](results/2026-11-04.md) |
| 看 Suzu 强制检索重测 | [Suzu 与 Qwen：714 题初判](results/2026-11-05-suzu-forced.md) |
| 了解哪些公开、哪些保留 | [发布范围](docs/publication.md) |

## 五分钟运行公开示例

只需 Python 3.10 或更新版本，无第三方依赖、无 API key，也不会产生模型费用。

```sh
git clone https://github.com/Ornn8/chat-memory-benchmark.git
cd chat-memory-benchmark
python demo/read_exam.py --verify-all
python demo/read_exam.py --id PUB01-C001/d45 --output question.json
python -m unittest discover -s tests -v
```

`question.json` 包含题目、考试时间和该时刻允许读取的历史，没有参考答案。**历史是给记忆系统逐轮处理的，不能把整个 JSON 直接塞进作答模型冒充记忆测试。** 具体做法见接入说明。

示例规模：一个虚构人物、182 天、360 轮对话、27 个独立事实组；每组在当天、3 天、15 天、45 天提问，共 108 个实例。重复问同一事实不算新增独立事实。每个考点和时间档仅有一道示例，供理解和接入，不据此排名。

## 使用完整正式测试集

正式集位于 [`datasets/natural-timegrid-20261101-v2/`](datasets/natural-timegrid-20261101-v2/)，包含六个人物的合成历史、714 道已出成绩的题目、标准答案和证据。离线校验与单题读取：

```sh
python datasets/natural-timegrid-20261101-v2/read_exam.py --verify-all
python datasets/natural-timegrid-20261101-v2/read_exam.py --id P01-CASE-001/d03
```

使用时把历史逐轮交给记忆系统处理，再从独立会话提问；标准答案用于判分。

## 我们怎么理解“记住了”

先把已有的用户消息和助手回复按时间交给系统自己的记忆流程，再从独立会话提问。更早的内容需要由系统的记忆或检索机制提供，不能偷偷附上完整聊天。

成绩写“通过几题 / 实际考几题”。只判事实、主体、时间和边界，不判说话风格。忘了、记错了、没有证据却编了，以及该保密时泄露了，分别记录。跨时间召回穿插在各考点里，不另造一个与内容脱节的总分。

## 数据来源

正式测试集和示例使用合成人物及对话；正式集的考点参考了真实使用场景中的记忆需求。仓库提供题目、历史、标准答案、成绩汇总和系统接入说明。

## 许可与反馈

本仓库自行编写的代码、文档和虚构示例使用 [MIT 许可](LICENSE)。第三方项目使用各自许可；仓库不捆绑其源码。

欢迎通过 Issue 指出题意歧义、错误证据或接入差异，请附公开示例题号、版本和复现步骤。不要提交密钥、私人对话或真实用户身份资料。订正会保留变更记录，不以某个系统得分高低为理由改题。
