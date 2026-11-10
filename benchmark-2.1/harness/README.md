# 评测程序（bench21）

评测程序负责四件事：**记忆隔离**、**成本计量**、**答题与判分**、**泄漏哨兵**。参赛系统只需要实现两个函数。

```text
bench21/
  gateway.py      计量网关：持有供应商密钥，按 prices.json 给每次调用计价，账本写 runs/bench21/spend-ledger.jsonl
  systems.py      适配器接口 + 参考系统（qwen-base、none、recent6、bm25-recent6、full-context）
  runner.py       评测程序：按截止轮喂历史、检索、答题、判分、汇总；--sentinel 跑泄漏哨兵
  natural.py      自然用记忆榜：run / judge / confirm / summarize（尾巴、回退、多轮现场生成、判分、子分）
  natural_report.py  三榜榜单与加权综合分、资格底线
  natural_gen.py / natural_build.py  合成出题与组卷（需要私有的案例文件，供复核方法）
  natural_sentinel.py  自然用记忆榜的泄漏哨兵
  scoring.py      通过规则、流量加权、成本 C、综合分 S（系数在 score_config.json）
  report.py       从运行结果生成榜单（A 加权 / 不加权、C、S、成对通过）
  prompts/judge.md  判分提示词（SHA 写进每条判分记录）
  prices.json     固定价目表（带版本号）
  calibrate_judge.py / leniency.py  判分员校准与宽松度检验
```

## 适配器接口

```python
from bench21.systems import System, Retrieval, Gateway

class MySystem(System):
    name = "my-system"
    def __init__(self, gw: Gateway): ...        # gw 是网关客户端；所有模型调用都走它
    def ingest(self, turn):                     # turn = {"turn":int,"time":iso,"user":str,"assistant":str}，严格按顺序，一轮一轮喂
        ...
    def retrieve(self, question, now, cutoff_turn, item_id=None) -> Retrieval:
        # 只读！返回要塞进答题提示词的记忆文本 prompt（它的 token 会按 flash 输入价计入 C）
        return Retrieval(prompt, used_turns=[...])
```

评测程序保证：

- 访问某个考点时，系统已经 `ingest` 的恰好是截止轮及之前的全部历史，一轮不多。系统拿不到历史文件。
- 考点按截止轮从小到大访问，所以系统的状态就是「截止轮之前看到的一切」。
- 返回的 `used_turns` 里出现截止轮之后的轮次，直接记为泄漏。

## 网关

```bash
export DASHSCOPE_API_KEY=...        # 向量 / 重排（Bailian）；对话模型的密钥见 gateway.py 顶部的环境变量说明
python -m bench21.gateway --port 18877 --cap-usd 9.5
export OPENAI_BASE_URL=http://127.0.0.1:18877/v1
```

网关路径：`/v1/chat/completions`、`/v1/embeddings`、`/v1/rerank`。请求头 `X-Bench-Phase`（ingest / retrieve / answer / judge）、`X-Bench-Tag`、`X-Bench-System` 用于记账。网关带花费硬上限。本地模型见规则文档。

## 跑一遍

```bash
python -m bench21.runner --release ../dataset --system qwen-base --split dev --run mine     # 开发集
python -m bench21.runner --release ../dataset --system qwen-base --split dev --run mine --sentinel   # 泄漏哨兵（只检索）
python -m bench21.report  --release ../dataset --run mine --split dev --out out/
pytest ../tests/test_bench21.py                                                      # 离线单元测试，不需要密钥
```

封存集只在评分时由评测方持有；`--split sealed` 需要封存集目录。


## 自然用记忆榜的接口

在 `ingest` / `retrieve` 之外多两个方法：`mark()` 返回当前记忆状态的标记，`rewind(token)` 把尾巴（以及多轮题里现场接上的回复）丢掉、退回到标记时的状态。`System` 基类给了 `mark()` 的默认实现（已喂入的轮数）；`rewind` 必须自己实现。系统若有 `begin_tail()` 方法，评测程序会在喂尾巴前调用它。更多见 [../natural/README.md](../natural/README.md)。

网关可以把百炼的请求转发给另一个持有百炼密钥的网关：`BENCH21_BAILIAN_UPSTREAM=http://127.0.0.1:18877`；对话模型并发数由 `BENCH21_DEEPSEEK_CONCURRENCY` 调。
