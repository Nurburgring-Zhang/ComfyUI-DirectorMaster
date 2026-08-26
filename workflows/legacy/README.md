# legacy 工作流存档

此目录为 Phase 36.6 时期的历史工作流存档，引用已收敛的旧节点类型
（`DirectorMasteryNode` / `CinematicStudio` / 各细粒度 Pro 节点等），
默认 17 节点注册下**不可加载**。

仅当设置环境变量 `DIRECTORMASTER_LEGACY_NODES=1`（恢复注册全部 63 节点）时可用。
注意：现行校验 `tests/test_workflows.py` 只覆盖顶层目录的两个现行管线，不覆盖本目录；
本目录为存档性质，不再随版本演进维护。

现行管线请使用上级目录的 `MINIMAL_PIPELINE_V8.2.json` / `MEGA_PIPELINE_V8.3.json`。

---

## 存档清单（节点数 / links 为 2026-08 实测值）

### WORKFLOW_* 系列（17 个）

| 文件 | 节点数 | links |
|---|---:|---:|
| `WORKFLOW_FILM_PRODUCTION.json` | 23 | 80 |
| `WORKFLOW_FEATURE_SCRIPT.json` | 11 | 32 |
| `WORKFLOW_STORYBOARD.json` | 10 | 29 |
| `WORKFLOW_INTERACTIVE_DRAMA.json` | 10 | 29 |
| `WORKFLOW_3D_ANIMATION.json` | 10 | 28 |
| `WORKFLOW_SHORT_DRAMA_30S.json` | 10 | 28 |
| `WORKFLOW_BRAND_FILM.json` | 10 | 27 |
| `WORKFLOW_QA_PUBLISH.json` | 10 | 27 |
| `WORKFLOW_SOUND_DESIGN.json` | 10 | 27 |
| `WORKFLOW_VERTICAL_SHORT_DRAMA.json` | 10 | 26 |
| `WORKFLOW_UNIVERSAL_6MODELS.json` | 9 | 24 |
| `WORKFLOW_MV.json` | 9 | 23 |
| `WORKFLOW_DOUYIN_HOOK.json` | 9 | 22 |
| `WORKFLOW_PICTURE_BOOK.json` | 8 | 19 |
| `WORKFLOW_H3_PRODUCTION.json` | 8 | 19 |
| `WORKFLOW_COLOR_GRADING.json` | 8 | 18 |
| `WORKFLOW_MINIMALIST_PRODUCT_AD.json` | 8 | 18 |

### MEGA_* 系列（6 个）

| 文件 | 节点数 | links |
|---|---:|---:|
| `MEGA_ALL_NODES_TOTAL_EXAMPLE.json` | 43 | 180 |
| `MEGA_STORYBOARD_8_SHOTS.json` | 49 | 71 |
| `MEGA_AUDIO_VIDEO_4_PARALLEL.json` | 28 | 37 |
| `MEGA_TEXT_TO_VIDEO_FILM.json` | 17 | 21 |
| `MEGA_IMAGE_TO_VIDEO_SHORT_DRAMA.json` | 16 | 17 |
| `MEGA_CONCEPT_TO_VIDEO.json` | 12 | 13 |

> 存档工作流均包含 `DirectorMasteryNode` 旧锚点节点；MEGA_* 系列还混用 ComfyUI
> 原生节点（KSampler / CLIPLoader / VAEDecode 等），需对应模型环境才能完整运行。
