# 投稿材料 · memory-system（AstrBot 记忆体系）

## 一、项目与版本

```
项目名称   memory-system（大肥鱼记忆体系）
作者       wuwugi
仓库       https://github.com/wuwugi/memory-system
国内镜像   https://gitee.com/aueds/memory-system
被测版本   main 分支（投稿时 HEAD），发布包 18 个文件
宿主       AstrBot 4.x；本测试直接运行插件自带脚本，未经过宿主 UI
说明       本轮为"开箱默认配置"，未启用模糊化压缩
```

## 二、测试配置（开箱默认）

```
题库       datasets/natural-timegrid-20261101-v2（714 题 / 6 人物）
记忆隔离   每人一个独立 data_dir

写入       每条消息按归档格式落盘，时间取历史"逻辑时间"：
             - **MM-DD HH:MM · 私聊·对方(10001)**：用户消息
             - **MM-DD HH:MM · 私聊·我(10002)**：助手回复

索引       python rag_index.py --rebuild
           fastembed BAAI/bge-small-zh-v1.5（512 维，本地 CPU）

检索       search.top_k = 20（默认值），关键词 + 语义双路
           按题目 cutoff 日期过滤，取 ≤20 条

用户档案   python profile.py（插件自带）
           模型抽取"用户自述事实"，按字段归类并带日期，
           写 data_dir/用户档案.md；注入时带 ≤400 字

作答       DeepSeek deepseek-chat，temperature 0.0，max_tokens 220
           注入块 = 用户档案 + 相关旧事 + 回答纪律
           直接对话窗口：无（只给检索片段和档案）
           回答纪律：只写材料里出现过的日期/数字/人名，不补细节；
                     档案与旧事冲突以旧事为准；没有才说不知道

判分       DeepSeek deepseek-chat，temperature 0.0，按 grading/judge-prompt.md
           逐题输出判定，再交 grade.py score 汇总

未启用     模糊化压缩（S0→S4）、缓冲期恢复、热层注入、注入不落库
嵌入/重排  bge-small-zh-v1.5 / 无重排
默认参数   除上述默认值外未改动
```

## 三、成绩（按仓库判分工具）

```
通过      522 / 714 = 73.1%
未答      0
判分题数   714
```

按人物：

| 人物 | 通过 / 题数 |
|---|---:|
| P01 | 68 / 88 |
| P12 | 55 / 79 |
| P14 | 61 / 82 |
| P16 | 89 / 123 |
| P17 | 122 / 172 |
| P20 | 127 / 170 |

按时间间隔：

| 间隔 | 通过 / 题数 |
|---|---:|
| 当天 | 134 / 189 |
| 3 天 | 138 / 184 |
| 15 天 | 130 / 174 |
| 45 天 | 120 / 167 |

最弱考点：相对日期 18/44、时间题 22/48、真实变化 30/58、共同编的故事 23/43、分散的线索 30/56。

## 四、同一系统的调优配置

同一套代码、把用户档案改成"逐窗口抽取 + 按字段取最新"，其余不变：

```
开箱默认   522 / 714 = 73.1%
调优配置   540 / 714 = 75.6%
```

投稿采用开箱默认成绩（73.1%），因为这是别人装完、按文档跑一遍能复现的数字。

## 五、配置差异说明（重要）

```
本轮只启用「写入 + 检索 + 用户档案 + 提示词组装」，
未启用模糊化压缩（S0→S4）。

原因：本轮测"记忆能否记住并被检索回来"，不测"遗忘策略是否正确"。
启用压缩后成绩可能升降，需单独一轮测试。
```

## 六、消耗与耗时

```
索引构建   约 40 秒/人物（本地 CPU，不花钱）
档案抽取   约 20 次模型调用，约 ¥0.3
单轮作答   714 请求，约 ¥1.6
单轮判分   714 请求，约 ¥1.6
耗时       作答约 2 分钟、判分约 3 分钟（并发 6）
来源       DeepSeek 平台用量导出（实际账单）
```

## 七、文件清单

```
answers.jsonl    714 行，{"id","answer"}
packets.jsonl    grade.py prepare 生成（含 rubric/证据/哈希）
reviews.jsonl    714 行，逐题判断
judgments.jsonl  grade.py score 生成，逐题判定与理由
summary.json     总通过数与统计
```

## 八、判分者说明

```
判分模型   DeepSeek deepseek-chat（非作者，非 Codex）
判分方式   按 judge-prompt.md 字段逐题判断，脚本负责哈希校验与汇总
局限       作答与判分同模型，可能有偏好；建议复核时用 Codex 重判
```

## 九、复现

```bash
git clone https://github.com/wuwugi/memory-system
cd memory_system && cp config.example.json config.json   # 填 api_key
# 1 六个人物历史按归档格式写入 data_dir/<persona>/归档.md
# 2 python rag_index.py --rebuild --data 每人物一次（MEM_DIR 或配置 data_dir）
# 3 python profile.py             # 抽用户档案
# 4 按 cutoff 过滤检索 top20，注入档案与回答纪律，DeepSeek 作答
# 5 python grading/grade.py prepare --answers answers.jsonl --out packets.jsonl
# 6 按 judge-prompt 生成 reviews.jsonl
# 7 python grading/grade.py score --packets packets.jsonl --reviews reviews.jsonl \
#        --out judgments.jsonl --summary summary.json
```
