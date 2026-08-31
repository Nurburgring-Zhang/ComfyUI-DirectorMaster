# DirectorMaster 模式卡 Schema（V16.3.0 批次2 定稿）

> 本文件是 `knowledge_base/mode_cards/` 的唯一卡片规范。`tools/sync_mode_index.py`
> 按本文硬校验（违例逐条列出，exit 1）；对账基准 `tests/mode_manifest.json` 由
> `tools/dump_mode_manifest.py` 从 16 超级节点真实 `INPUT_TYPES()` 探针生成。
> 全部校验零第三方依赖——frontmatter 由 sync 内置手写解析器处理，禁 yaml。

## 1. 文件位置与命名

- 卡片**只允许**放在 `knowledge_base/mode_cards/<slug>/<mode_id>.md`，slug↔节点映射模式节点目录集（随注册增长，当前 11 个）：
  `script→DirectorMasterScript`、`cinematic→DirectorMasterCinematic`、`vibe→DirectorMasterVibe`、
  `art→DirectorMasterArt`、`sound→DirectorMasterSound`、`characters→DirectorMasterCharacters`、
  `asset→DirectorMasterAsset`、`router→DirectorMasterRouter`、`video_router→DirectorMasterVideoRouter`、
  `archive→DirectorMasterArchive`。
- 卡放错目录（frontmatter `node` 与目录归属不一致）= 违例；未知 slug 目录 = 违例。
- 根目录固定四件：`SCHEMA.md` / `_TEMPLATE.md` / `INDEX.md` / `index.json`；其余根级 md/json 文件 = 违例。
- 文件名建议等于 `mode_id`（便于人工对账，非硬校验项）。

## 2. frontmatter（键集封闭，共 8 键）

必填 7 键 + 可空 1 键。值语法：单行 `key: value`；列表用内联 `[a, b, c]`；引号可选（成对单/双引号会被剥除）；
标签/别名/形态值内部禁用逗号与竖线 `|`；键名仅小写字母数字下划线。

| 键 | 约束 | 硬校验 |
|---|---|---|
| `mode_id` | ascii-kebab，全局唯一，`^[a-z0-9]+(-[a-z0-9]+)*$` | 违例 exit 1 |
| `node` | 上述 10 个注册节点名逐字，且必须等于目录归属节点 | 违例 exit 1 |
| `name` | 该节点模式下拉的显示名**逐字**，必须 ∈ `tests/mode_manifest.json` 的 `nodes[node].creative` | 违例（孤儿卡）exit 1 |
| `one_liner` | 一句话 ≤40 字，说清"该模式把输入变成什么"，直接具体零空话 | 超长记 advisory |
| `applicable` | 适用形态列表，非空（如 `[竖屏微短剧, 短视频]`） | 空 = 缺必填，exit 1 |
| `intensity` | `low` / `medium` / `high` / `adaptive` 四值之一 | 违例 exit 1 |
| `style_tags` | 风格标签列表，非空 | 空 = 缺必填，exit 1 |
| `aliases` | 同义词列表，可空（`[]` 或整行省略） | 可空 |

未知键 = 违例（键集封闭）。`name` 与 manifest 枚举逐字不一致时按**孤儿卡**报错——若该选项确属
新增创作模式，须先重跑 `tools/dump_mode_manifest.py` 修订 manifest，禁止先写卡后补口径。

## 3. 正文结构（H2 五节，标题逐字，顺序固定）

```
## 意图        — 用户何时选它、选它后输出与相邻模式的本质差别，≤3 句
## 核心手法    — 该模式真实执行的 2-4 个具体手法，与实现分支一一对应
## 参数表      — 三列表格：参数 | 典型值 | 越界后果
## 已知坑      — 从代码边界条件与既有测试断言提炼，触发条件+表现+规避
## 节点映射    — 实现文件 + 分支/函数指针 + 数据来源
```

参数表硬要求：**有参模式 ≥3 行数据行；无参模式 ≥2 行覆盖节点级共享参数**
（共享参数指该节点所有模式消费的输入，如 `核心数据包`、`导演风格`、`场景描述`、`情绪基调`）。
"越界后果"必须写真实行为（降级/空转/回退到什么），禁止写"可能有问题"式含糊话。
行数不足记 advisory（WaveC 字段完整率硬校验 + 双 AI 互审按红线拒收）。

## 4. 质量红线（互审 reject 级）

1. **节点映射必须给实现文件+分支/函数指针**（如 `aggregator/cinematic_studio.py :: TEMPLATES["电影工作室"]`、
   `aggregator/script_studio.py :: _build_film_long_template()`），只写节点名 = reject。
2. **禁止模板式灌水**：五节内容跨卡可互换、形容词堆砌、空话连篇 = reject。每卡的手法与坑必须因卡而异。
3. **已知坑不得虚构**：只允许从代码边界条件（降级分支、异常路径、已知分派缺口例外，如 script
   儿童绘本与"儿童绘本格式"分派缺口已在卡面如实披露）与既有测试断言（`tests/test_all_modes.py` 执行断言、
   `tests/d1_grammar_probe.py` 语法唯一性）提炼。确无坑可写时写"未发现"，禁止编造。
4. **不虚构参数**：卡内参数必须真实存在于该节点 `INPUT_TYPES()` 或其实现分支。
5. 文风：直接、具体、零空话；`one_liner` ≤40 字。

## 5. 校验工具链

| 命令 | 用途 |
|---|---|
| `python tools/dump_mode_manifest.py` | 生成/刷新 manifest（含审计表与 246 口径诚实阀门） |
| `python tools/dump_mode_manifest.py --verify` | 重探针三方核对（live 枚举 × manifest × 审计规则） |
| `python tools/sync_mode_index.py` | 全量校验 + 写 `INDEX.md` / `index.json` |
| `python tools/sync_mode_index.py --check` | 只验不写 + 索引逐字节漂移比对（漂移 exit 1） |
| `python tools/sync_mode_index.py --node <Node>` | writer 自检子集（缺卡检查限定该节点，不写索引） |

零卡状态下全量 `--check` 预期 **exit 1**（逐节点列出缺卡数）——这是负样本证据，不是工具故障。
`INDEX.md` 与 `index.json` 为自动生成物，禁止手改；手改会在下次 `--check` 漂移比对中暴露。
