# dsh-rofm 1.5.5 — 复现说明

## 环境

- Windows 11（MSYS2 bash）；Node v24.21.0；Python 3.14（仅用于仓库 grading/grade.py 的离线校验；考试与判分本身由 Node 工具完成）。
- 被测系统冻结树：dsh-rofm 1.5.5，runtime 54 文件 / 2,182,335 bytes，sha256 e5fa6cf23c4561e12e8401ba39d2791e320c79145a1ed295568acbf00472ffd1；node --test 1,330 tests / 1,328 pass / 0 fail（2 skipped）。

## 数据集

- 题库：仓库 datasets/natural-timegrid-20261101-v2（714 题，6 人物）。
- exam-inputs.jsonl sha256：584e1acd8f2dc334be5859e31e689f9e684f24be88e6d9c808318698c4ea6c63
- review-only/answer-key.jsonl sha256：07f390bbead123ed0f723a38d7642a0ca3367926e84d1af484b255284b2de392
- histories 与仓库 manifest 的 sha256 一致（P01 5073b1f9… / P12 9d762423… / P14 030dcaf5… / P16 3b51c824… / P17 a8b5b1f7… / P20 847ac8c7…）。

## 测试流程

1. 每个 persona 单独一份记忆（独立 memory 目录；6 个人物互不共享）。
2. 按时间把该人物全部历史轮次交给 DSH 宿主 + dsh-rofm 1.5.5 处理（回放）：上下文 8000 token 非原生窗口；超出阈值自动归档最早的一段到记忆文件夹；每轮 memory_judge 维护；逻辑时钟按题目时间推进。
3. 回放完成后，在题目 cutoff_turn 对应的快照上考试：题目以用户消息形式进入原生对话；模型可使用 memory_recall / memory_judge / memory_image 等记忆工具；最近 6 轮对话窗口；temperature 0；max_tokens 2500；最多 6 轮工具调用。
4. 题目与答案不写回记忆；不同题目的考试状态相互隔离。
5. 714 题分批完成：六人物全量回放 + 首批 41 题；随后复用同一批回放快照补考 669 题；P01-NEW-001 四题（私有题库复核版曾移除，官方题库仍保留）用 P01 重放补测 4 题。三批均为 1.5.5、同一配置、同一作答模型；最终合并为完整 714 题。

## 判分

- 每题 deepseek-flash A/B 双判（temperature 0，独立判词，按 rubric required/forbidden/unknown + 证据节选）。
- A/B 分歧、低置信与边界题由人工仲裁复核（依据全量历史与 exam now/cutoff）：多余内容无错算过；required 缺失/否认/确实说错算错；required 已答对但多余细节有误归中性（本投稿按要求计入错题）。
- reviews.jsonl 即最终判分记录；judgments.jsonl 与 summary.json 由仓库 grading/grade.py 校验生成：

    cd repo  # 含 datasets/natural-timegrid-20261101-v2 与 grading/grade.py 的仓库根
    python grading/grade.py prepare --answers answers.jsonl --out packets.jsonl
    python grading/grade.py score --packets packets.jsonl --reviews reviews.jsonl --out judgments.jsonl --summary summary.json
    # 期望输出：Passed 681 / 714

## 文件校验

    sha256sum -c SHA256SUMS

## 限制

- 测试使用作者本地的 rbench 调度工具（同一宿主与模型网关），它不是仓库 benchmark-2.1 的官方 harness；本目录公开全部回答、判分与理由，便于维护者抽查。
- 判分为 deepseek-flash A/B + 人工仲裁，不是维护者独立复现；模型判分存在波动。
- 不包含 API key、私聊原文、真实用户资料、本地数据库或绝对路径。
