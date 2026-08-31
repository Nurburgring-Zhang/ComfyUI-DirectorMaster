# benchmark/ — 固定任务 × 固定模型 × 逐请求记录 (V16.7 批次3 D8, builder-b2)

经济性/质量基准框架：把"同一个提示词工程在不同模型端点上的真实表现"变成可对账的逐请求数据。
仅 stdlib（零第三方依赖），Python ≥3.8。

## 方法论（三条硬规矩）

1. **固定任务 × 固定模型**。任务集固定在 `tasks/*.json`（输入 messages + 期望结构，逐字节固定）；
   每次运行通过 `--model` 钉死单一模型，每任务连续跑 `--repeats` 次。变量只有一个：模型端点。
   任务不改、提示词不改、温度不改——改了就不是同一次基准，必须换 `--tag` 另存一列。
2. **逐请求记录，不估算**。每个请求一行 CSV：延迟、HTTP 状态、内容字数、期望结构检查通过数，
   以及 **usage tokens 从端点响应的 `usage` 字段原样拉取**（`prompt_tokens/completion_tokens/total_tokens`）。
   端点没返回 `usage` → 记账列留空并置 `usage_present=False`，**runner 永不自行估算 token**；
   **runner 不计算金额**（无价目表，算钱就是估算）——计价留待离线用原始 usage 与账单对账。
3. **无真实端点时诚实标注 MOCK**。`--mock` 用 f2 式内嵌 OpenAI 兼容服务器（`tests/f2_ai_track_e2e.py`
   同款 `http.server`）验证 runner 通路（传输/解析/结构检查/CSV 落盘全链），但所有输出在
   CSV `mode` 列与摘要行标注 `MOCK`，计量数字（含 mock 返回的 usage）**不代表任何真实端点账单**。

## 用法

```bash
# 真实端点（推荐: 先小 repeats 探通路）
python benchmark/run_benchmark.py \
    --endpoint https://api.example.com/v1/chat/completions \
    --model your-model --api-key-env MY_API_KEY --repeats 3

# 本地 mock 通路验证（无需任何端点/密钥）
python benchmark/run_benchmark.py --mock --repeats 2

# 错误通路验证（服务器 500 → runner 逐请求记 ok=False 不崩）
python benchmark/run_benchmark.py --mock --mock-mode error
```

参数：`--endpoint`（URL 或环境变量 `DM_BENCH_ENDPOINT`）、`--model`、`--api-key-env`（存密钥的
环境变量**名**，密钥不落盘不进 CSV）、`--tasks`（默认 `tasks/`）、`--out`（默认 `results/`）、
`--repeats`（默认 3）、`--timeout`（秒，默认 120）、`--tag`（本次运行标签，进文件名）、
`--mock` / `--mock-mode good|error`。

输出：`results/bench_<UTC时间戳>_<tag>.csv`（`benchmark/results/` 已被 `.gitignore` 忽略，
运行产物不入库）+ 终端摘要（每任务通过率 / p50 与均值延迟 / usage 汇总 / 运行模式声明）。

## CSV 列

| 列 | 含义 |
|---|---|
| `run_id` / `ts_utc` / `mode` | 本次运行 ID / 逐请求 UTC 时间戳 / `REAL` 或 `MOCK` |
| `task_id` / `model` / `request_no` | 任务 ID / 模型名 / 该任务第几次请求（1 起） |
| `latency_ms` / `http_status` | 端到端耗时 / HTTP 状态码（0=未达响应） |
| `ok` / `error` | 请求级成败 / 失败原因（异常类型+摘要） |
| `prompt_tokens` / `completion_tokens` / `total_tokens` | 端点 `usage` 原值，缺失留空 |
| `usage_present` | 端点是否返回了 `usage` 字段 |
| `content_chars` / `checks_passed` / `checks_total` / `checks_detail` | 内容字数 / 期望结构检查 通过数·总数·明细 |
| `content_head` | 返回内容前 64 字符（人读对账锚） |

## 固定任务集（tasks/）

| 文件 | 任务 | 期望结构要点 |
|---|---|---|
| `task1_mecha_storyboard.json` | 15s 短视频分镜（机甲/暴雨码头/护盾） | JSON：分镜表≥5 镜，每镜含 镜号/景别/运镜/焦段/时长/画面焦点；总时长秒>0；必含标记 机甲·码头；禁含词 震撼·完美·作为AI |
| `task2_drama_screenplay.json` | 800-1200 字短剧本（父女/厨房/凤梨罐头） | 文本：≥600 字；必含标记 内景·父亲·女儿·凤梨；禁含词 masterpiece·作为AI·placeholder |
| `task3_ad_storyboard.json` | 60s 广告分镜（智能手表） | JSON：分镜表≥6 镜，每镜含 镜号/画面焦点/声音（同期声枚举）；必含标记 手表；禁含词 完美·震撼·作为AI |

任务 JSON schema：`{id, 名称, messages:[{role,content}...], 参数:{temperature,max_tokens}, 期望结构:{格式, 必含键, 列表键, 每镜必含键, 最少镜数, 最少字数, 必含标记, 禁含词}}`。
新增任务 = 新增一个 JSON 文件，runner 自动发现；期望结构只写"能机器判定的"，判不了的不要写。

## 退出码

`0` 全部请求请求级成功（结构检查不过只记录、不改变退出码——检查结果是数据不是 runner 故障）；
`1` 任一请求级失败（网络/HTTP/解析）；`2` 参数或环境错误（缺 endpoint、缺密钥环境变量等）。

## 与仓库其他件的关系

- 判例库（`knowledge_base/quality_precedents/` NP-001…NP-012）是质量口径的沉淀；本目录把口径
  里可机器判定的部分（必含标记/禁含词/结构键）搬进 `期望结构`，对真实模型逐请求打分。
- `手法去重`/`卖点映射`（aggregator/cinematic_studio.py）属引擎内建校验，不依赖本目录；
  本目录测的是"外部模型端点"同类口径的遵守率。
