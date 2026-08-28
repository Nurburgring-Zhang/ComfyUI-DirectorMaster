# Legacy 模块诚实审计（V16.3.0）
> 生成方式：AST 全仓静态依赖分析（`_dm_audit/legacy_dep_audit.py`），非目测。
> 结论时点：V16.3.0 随机性修复之后。此前 grep 子串匹配曾把 `from director_pro` 误判为被引用
> （实为 `from director_profiles_*` 的子串误匹配），AST 解析已纠正。

## 一、结论速览

根目录 78 个模块分类如下：

| 类别 | 数量 | 说明 |
|---|---|---|
| A. 被超级节点（aggregator/）真实 import | 29 | 活跃引擎/数据，V16.3 运行时必达 |
| B. 仅被其他根模块引用（legacy 内部链） | 8 | 只在 `DIRECTORMASTER_LEGACY_NODES=1` 时可达 |
| D1. legacy 注册表内的节点模块（经文件加载器可达） | 37 | 同上，为 legacy 节点本体（加载器按文件名加载，故静态零 import 属预期） |
| D2. **真死代码**（不在 legacy 注册表、零引用） | 1 | `director_pro.py`（及其私有依赖 `director_engine.py`、`engine_story_arc.py`） |
| E. 独立入口工具（合理零引用） | 3 | `doctor.py`、`fix_disabled_blocks.py`、`validate_workflows.py` |

## 二、A 类：超级节点真实引擎（29 个，全部有 aggregator 侧 import 语句为证）

anti_ai_vocab, asset_registry, asset_registry_data, comic_drama_pro, director_data_unified,
director_profiles_animation, director_profiles_creative_ad, director_profiles_extended,
director_profiles_film, director_profiles_short_video, director_profiles_tv_drama,
director_real_scripts, format_templates, h3_context_ir_node, market_audience_pro,
master_director_data, master_orchestrator, modes_book, modes_child, modes_design, modes_drama,
modes_storyboard, mv_pro, picture_book_pro, pln_llm, pln_random, scene_library,
story_sense_data, style_prefix_data

（其中 asset_registry / comic_drama_pro / h3_context_ir_node / market_audience_pro / mv_pro /
picture_book_pro 同时也在 legacy 注册表内——双重身份，实际为超级节点引擎。）

## 三、B 类：仅 legacy 链内部引用（8 个）

aesthetic_judgment_pro, director_engine, director_mastery_v2, director_soul, engine_story_arc,
pln_utils, production_pipeline_v3, prompt_builder

- `director_engine` / `engine_story_arc` 被 `director_pro` 引用 → 随 D2 一并处置。
- `director_mastery_v2` 被 hook_master_pro / vertical_short_drama_pro / character_arc_pro 引用（legacy 链）。
- `pln_utils` / `prompt_builder` / `production_pipeline_v3` 仅被 legacy 模块引用。
- `aesthetic_judgment_pro` / `director_soul` 为 legacy 节点本体（注册表内）。

## 四、D2 类：真死代码（本轮发现，待主人裁决处置方式）

| 文件 | 证据 | 建议 |
|---|---|---|
| `director_pro.py` | 不在 `_LEGACY_MODULES`；全仓 AST 零 import（早前 grep 误报为被 director_data_unified 引用，AST 证实为 `director_profiles_*` 子串误匹配） | 可删除或移 attic；删除前需主人确认 |
| `director_engine.py` | 仅被 director_pro 引用 | 随 director_pro 连带处置 |
| `engine_story_arc.py` | 仅被 director_pro 引用 | 随 director_pro 连带处置 |

## 五、E 类：独立入口工具（3 个，保留）

- `doctor.py` — 用户自检入口（README 推荐 `python doctor.py`），独立运行属正常。
- `validate_workflows.py` — 工作流校验开发工具，独立运行。
- `fix_disabled_blocks.py` — 历史修复脚本，独立运行；可考虑移入 tools/ 目录（待裁决）。

## 六、过时文档声明（V6/V7 时代，内容与 V16.3 代码已脱节）

以下文档保留作历史存档，已在文件头部加"历史文档"横幅，不应作为当前功能依据：

- `WORKFLOW_DOC_V6.1.md`
- `RELEASE_NOTES_V7.0.md`
- `PHASE_NODES_REFERENCE.md`（节点数/模式数口径为旧版）
- `PLAN_COMPARE_V6.3_VS_V7.md`

## 七、处置原则（本轮执行）

本轮（V16.3.0）**只标注、不删除**——删除属于破坏性动作，且 legacy 层（46 节点 +
`DIRECTORMASTER_LEGACY_NODES=1`）为 V14.2 起承诺的兼容机制，18 个 `workflows/legacy/*.json`
仍引用它们。是否删除 D2 三文件与 legacy 层瘦身，留给项目主人裁决。
