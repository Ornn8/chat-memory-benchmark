# 复现说明 — HitMind 0.1.0（commit `8fc7a51`）

## 环境与版本
- HitMind v0.1.0，commit `8fc7a51`，仓库 https://github.com/Fishskys/hitmind。
- 基准适配器：`adapters/hitmind/run.py`（本 benchmark 仓库内，外部 benchmark 侧）。
- 依赖：本地 OpenAI 兼容嵌入服务（`embeddinggemma-2`, 512 维）与本地 cross-encoder `/rerank` 端点；作答/判分走 DeepSeek `deepseek-chat`。

## 题库与哈希
- `datasets/natural-timegrid-20261101-v2`（714 题 / 6 人物）
- exam-inputs.jsonl sha256 = `584e1acd8f2dc334be5859e31e689f9e684f24be88e6d9c808318698c4ea6c63`
- review-only/answer-key.jsonl sha256 = `07f390bbead123ed0f723a38d7642a0ca3367926e84d1af484b255284b2de392`
- manifest.json sha256 = `19b7edf73bde64067a59132f6a58b1756863a880026c1487ee8a4766a377938f`

校验：
```sh
sha256sum datasets/natural-timegrid-20261101-v2/exam-inputs.jsonl
sha256sum datasets/natural-timegrid-20261101-v2/review-only/answer-key.jsonl
sha256sum datasets/natural-timegrid-20261101-v2/manifest.json
```

## 运行（两档）
```sh
# 无 rerank（对照）
python adapters/hitmind/run.py --no-rerank \
  --out outputs/answers-714-aligned-off.jsonl --trace-out outputs/trace-714-aligned-off.jsonl
# 有 rerank（主）
python adapters/hitmind/run.py \
  --out outputs/answers-714-aligned-on.jsonl --trace-out outputs/trace-714-aligned-on.jsonl
```
run.py 内部：每人隔离 DB；按 `cutoff_turn` 逐轮 `Engine.capture(raw)` 入库（`memory_max_chars=0`）；到截止点 `recall(top_k=10)` → 拼 `[id] (kind)[@date]：原文` → 交 `deepseek-chat` 作答。

## 判分与汇总
```sh
python grading/grade.py prepare --answers outputs/answers-714-aligned-on.jsonl --out outputs/packets-714-aligned-on.jsonl
python adapters/hitmind/judge.py --packets outputs/packets-714-aligned-on.jsonl --out outputs/reviews-714-aligned-on.jsonl
python grading/grade.py score --packets outputs/packets-714-aligned-on.jsonl \
  --reviews outputs/reviews-714-aligned-on.jsonl \
  --out outputs/scores-714-aligned-on.jsonl --summary outputs/summary-714-aligned-on.json
# 无 rerank 档同理，把 on 换成 off
```

## 提交文件校验
```sh
sha256sum -c SHA256SUMS
```

## 配置记录
逐档运行配置见 `runmeta.json`（有 rerank）与 `runmeta-off.json`（无 rerank）。
