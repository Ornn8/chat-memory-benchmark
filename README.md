# 中文陪伴记忆 Benchmark

<p align="center"><img src="benchmark-2.2/assets/poster.jpg" alt="聊天记忆挑战赛 2.2 海报" width="420"></p>

## 2.2 聊天记忆挑战赛（2026-11-12 开赛）

两个合成人物、各半年的聊天史（约 7000 轮和 5400 轮），测陪伴类 AI 记不记得、该不该提旧事。**成绩和成本一起排名**。

- **短对话榜**：话痨型，短句多。
- **长对话榜**：长信型，一条消息很长。
- **自然用记忆榜**：该提旧事时自然地提，不该提时不翻旧账。

**赛程（北京时间）**

| 阶段 | 时间 |
| --- | --- |
| 调试期（可申请一次开发集试跑） | 11-12 至 12-02 |
| 冻结（提交 commit / tag 和模型清单） | **12-03 00:00** |
| 封存跑（只跑一次） | 12-03 至 12-09 |
| 复核与公布 | 目标 12-12 |

**规则要点**：开源、固定 commit；所有模型调用走我们的评测网关；每次运行先交 **¥50 押金**，按实际费用结算，**用不完退**；总费用到 ¥50 就停止、成绩作废，不补交。奖品：200 美元 ChatGPT 订阅。

**报名**：[开一个 issue](https://github.com/Ornn8/chat-memory-benchmark/issues/new?template=challenge-entry.yml)（报名、申请试跑、提交冻结版本都用它），再加 **QQ 群 1132194746** 交押金、联系我们。

**参照成绩**（Qwen 基础方案，封存集抽样，括号是 95% 区间）：短对话 42.5（35.1–49.9），长对话 47.4（39.7–55.0），自然用记忆 52.5（42.7–60.8），综合 48.7（42.6–53.0）。**开发集分数不是榜单成绩**；2.1 和 2.2 的分数不能直接比较；只有两个合成人物。

[2.2 说明](benchmark-2.2/README.md) · [规则](benchmark-2.2/RULES.md) · [计分](benchmark-2.2/SCORING.md) · [结果](benchmark-2.2/results/README.md) · [评测程序](benchmark-2.2/harness/README.md)

## 旧版本

- [2.1](benchmark-2.1/README.md)：两个人物的长历史、成绩 + 成本计分；挑战赛已改按 2.2 进行。
- [1.0（六人物 714 题）](benchmark-1.0/README.md)：题库、判分工具、示例和投稿方式，下面是成绩表。

## 1.0 六人物 714 题成绩表

成绩写「通过 / 实际考几题」。**作者自测的成绩我们没有复测**（标了「作者自测 · 未复核」，写明判分模型和日期，判分者不同时不能严格横比）。1.0 不再是主榜，欢迎带着系统来 2.2 挑战赛。各项目的版本和接入方式见[测试配置与局限](docs/tested-configurations.md)。

| 项目／上游 | 作者 | 测试状态与成绩（通过 / 已答） |
| --- | --- | --- |
| [冷热记忆方案（ARCHEON）](https://github.com/ARCHEON999/Companion-AI-Memory-Context-Token-Optimization) | 原无奇变 / ARCHEON999 | 按公开方案复现；完整卷 [356 / 714](results/2026-11-01-first-four.md) |
| [SeekMemory](https://github.com/NeverENG/SeekMemory) | BangBang在coding / NeverENG | 原版插件，开启 Dream；完整卷 [230 / 714](results/2026-11-01-first-four.md) |
| [digital-life-core](https://github.com/mashangshui/digital-life-core) | 温水 / mashangshui | 原生核心与迁移入口；完整卷 [233 / 714](results/2026-11-01-first-four.md) |
| [dsh-soul](https://github.com/icyaaaww/dsh-soul) | 糖霜Official | 2.0 原生 452 / 714；[其他版本和配置](results/2026-11-07-recap.md) |
| [SurfCore](https://github.com/Mieksido/surfcore) | 玛露Marrow | 记忆卡完整卷 123 / 714；合辑共同题 [122 / 687](results/2026-11-01.md) |
| [dsh-rofm](https://github.com/wall1234567/dsh-rofm) | 鄙人乃路人甲 | 1.4.2 重测初判 [471 / 714](results/2026-11-04.md)；旧版测试中断，保留 [242 / 687](results/2026-11-01.md) |
| [OpenViking](https://github.com/volcengine/OpenViking) | 火山引擎 | 0.5.2.1 初判 [555 / 714](results/2026-11-04.md) |
| [dsh-suzu-memory](https://github.com/eryucheng/dsh-suzu-memory) | eryucheng | 强制原生检索重测初判 [621 / 714](results/2026-11-05-suzu-forced.md)；自主决定是否检索的上一轮 [516 / 714](results/2026-11-04.md) |
| [Hindsight](https://github.com/vectorize-io/hindsight) | Vectorize | 1.2.0 初判 [513 / 714](results/2026-11-04.md) |
| [dsh-biocore 0.4.0](https://www.npmjs.com/package/dsh-biocore/v/0.4.0) | 未标注 | **不可用**：测试历时约 34 小时，仅完成 58 / 714 题后停止；[查看记录](results/2026-11-07-recap.md) |
| [dsh-world 0.7.2](https://github.com/chenkezhen480/dsh-world) | chenkezhen480 | 完整卷 557 / 714；[成绩数据](results/2026-11-08-dsh-world-0.7.2-summary.json) |
| [dsh-memory-keeper](https://github.com/flywalker68/dsh-memory-keeper) | flywalker68 | 完整卷 542 / 714；[成绩数据](results/2026-11-08-dsh-memory-keeper-summary.json) |
| [whale-card](https://github.com/wangjumhan131/whale-card) | wangjumhan131 | 完整卷 217 / 714；[成绩数据](results/2026-11-08-whale-card-summary.json) |
| [BaiShou Next](https://github.com/foxletters-hq/BaiShou-Next) | foxletters-hq | 已答 711 题，通过 514 题；[成绩数据](results/2026-11-08-baishou-next-summary.json) |
| [dsh-mnemon](https://github.com/omdsh-dev/dsh-mnemon) | omdsh-dev | 已答部分 341 / 539；[成绩盘点](results/2026-11-08-recap.md) |
| [codex-deepseek-starter](https://github.com/xrh66/codex-deepseek-starter) | xrh66 | 345 / 714；[成绩盘点](results/2026-11-08-recap.md) |
| [dsh-memory（灵枢）](https://github.com/FuRongJun-1999/dsh-memory) | FuRongJun-1999 | DSH 原生 363 / 714；[其他配置](results/2026-11-07-recap.md) |
| [dsh-fish-memory](https://github.com/Yuuyuko-uu/dsh-fish-memory) | Yuuyuko-uu | 383 / 714；[成绩盘点](results/2026-11-08-recap.md) |
| [dsh-mnemosyne](https://github.com/canyueY/dsh-mnemosyne) | 胃疾璇 | 425 / 714；[成绩盘点](results/2026-11-08-recap.md) |
| [memory-brain](https://github.com/peterpoal134/memory-brain) | peterpoal134 | 454 / 714；[成绩盘点](results/2026-11-08-recap.md) |
| [dsh-memory-calendar](https://github.com/IStarFoxI/dsh-memory-calendar) | IStarFoxI | 505 / 714；[成绩盘点](results/2026-11-08-recap.md) |
| [dsh-hippocampus](https://github.com/coner13/dsh-hippocampus) | coner13 | 528 / 714；[成绩盘点](results/2026-11-08-recap.md) |
| [dsh-memory-brain](https://github.com/y083245/dsh-memory-brain) | y083245 | 583 / 714；[成绩盘点](results/2026-11-08-recap.md) |
| Qwen RAG（本评测搭建的检索对照） | Qwen 模型团队；检索流程由本评测搭建 | 完整卷 [596 / 714](results/2026-11-01-first-four.md)；合辑共同题 [574 / 687](results/2026-11-01.md) |
| [dsh-neo4j-memory](https://github.com/shuunO-O/dsh-neo4j-memory) | shuunO-O | **684 / 714** · 作者自测 · **未复核** · 判分：DeepSeek（作者抽查 + 维护者抽查修正） · 2026-11-05 · [材料](results/2026-11-05-dsh-neo4j.md) |
| [dsh-memu-memory 1.2.7](https://github.com/Tkingxiao/dsh-memu-memory) | Tkingxiao | **653 / 714** · 作者自测 · **未复核** · 判分：DeepSeek · 2026-11-06 · [材料](results/2026-11-06-dsh-memu-memory.md) |
| [SurfCore](https://github.com/Mieksido/surfcore) 向量记忆（BGE-M3） | mcliudian | **605 / 714** · 作者自测 · **未复核** · 判分：DeepSeek · 2026-11-07 · [材料](results/2026-11-07-surfcore-bge-m3-vector.md) |
| [dsh-dot 0.20.0](https://github.com/Kevinwu901113/dsh-dot) | Kevinwu901113 | **654 / 709（5 题未答）** · 作者自测 · **未复核** · 判分：Codex（gpt-6.1-sol） · 2026-11-07 · [材料](results/submissions/dsh-dot-0.20.0/README.md) |
| [dsh-plugin-memory-graph（大肥鱼好记性）](https://github.com/YeStarOne/dsh-plugin-memory-graph) | YeStarOne | **502 / 714** · 作者自测 · **未复核** · 判分：glm-5.3-flash 单票 · 2026-11-07 · [材料](results/submissions/dsh-plugin-memory-graph-2026-11-07/README.md) |
| [whale-card V5.9.1](https://github.com/wangjumhan131/whale-card) | wangjunhan131 | **585 / 714** · 作者自测 · **未复核** · 判分：DeepSeek · 2026-11-08 · [材料](results/submissions/whale-card-v5.9.1-20261108/README.md) |
| [PMem 0.41.0](https://github.com/dnciyun/dsh-PMem) | dnciyun | **618 / 714；关闭增强模块 583 / 713** · 作者自测 · **未复核** · 判分：deepseek-v4.1-flash · 2026-11-09 · [材料](results/submissions/pmem-0.41.0-2026-11-09/README.md) |
| [灵枢 md_cg 0.10.0 + 补丁包](https://github.com/FuRongJun-1999/dsh-memory) | FuRongJun-1999 | **642 / 714** · 作者自测 · **未复核** · 判分：deepseek-chat · 2026-11-10 · [材料](results/submissions/lingshu-0.10.0-2026-11-10/README.md) |
| [DSH-DREAM v0.3.6](https://github.com/baiqieji-LuLu/DSH-DREAM) | baiqieji-LuLu | **624 / 714** · 作者自测 · **未复核** · 判分：deepseek-flash · 2026-11-10 · [材料](results/submissions/dsh-dream-v0.3.6/README.md) |
| [dsh-rofm 1.5.5](https://github.com/wall1234567/dsh-rofm) | wall1234567 | **681 / 714** · 作者自测 · **未复核** · 判分：deepseek-flash A/B + 人工仲裁 · 2026-11-10 · [材料](results/submissions/dsh-rofm-1.5.5/README.md) |
| [memory-system（AstrBot）](https://github.com/wuwugi/memory-system) | wuwugi | **522 / 714** · 作者自测 · **未复核** · 判分：deepseek-chat · 2026-11-10 · [材料](results/submissions/memory-system-astrbot-2026-11-10/README.md) |

## 许可与反馈

本仓库自行编写的代码、文档和虚构示例使用 [MIT 许可](LICENSE)；第三方项目使用各自许可。欢迎通过 Issue 指出题意歧义、错误证据或接入差异，不要提交密钥、私人对话或真实用户身份资料。
