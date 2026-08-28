> ⚠️ **历史文档（V6/V7 时代存档）**：内容与当前 V16.3.0 代码已脱节，仅作历史参考。当前节点/模式口径以 README.md 与 docs/LEGACY_AUDIT.md 为准。

# 资产/空间/表演/声音/后期/6段/电影 节点代码 - 必须留根说明

**重要**: 这 10 个节点文件**必须留在根目录**，不能移入子目录。

## 当前实际文件名 (Phase 36.4 后)

| 文件 | 主类 | 功能 |
|------|------|------|
| `asset_registry.py` | `AssetRegistry` | 资产注册表 (起点节点) |
| `spatial_layout.py` | `SpatialLayout` | GEO 空间布局 |
| `acting_skill.py` | `ActingSkill` | 表演层专家 |
| `sound_skill.py` | `SoundSkill` | 声音层专家 |
| `iteration_post.py` | `IterationPostPro` | 迭代 + 后期 |
| `thirty_sec_six_act.py` | `ThirtySecSixAct` | 30s 6 段 |
| `cinematic_studio.py` | `CinematicStudio` | 电影工作室 |
| `master_orchestrator.py` | (函数) | 6 层主控编排 |
| `asset_registry_data.py` | (数据) | 资产注册表内部数据 |
| `style_prefix_data.py` | (数据) | 风格前缀 + 15 段结构内部数据 |

## 原因

`__init__.py` 第 51-57 行直接 `from xxx import ...` 顶级导入：

```python
from asset_registry import AssetRegistry                # 51
from spatial_layout import SpatialLayout                 # 52
from acting_skill import ActingSkill                     # 53
from sound_skill import SoundSkill                       # 54
from iteration_post import IterationPostPro              # 55
from thirty_sec_six_act import ThirtySecSixAct           # 56
from cinematic_studio import CinematicStudio             # 57
```

ComfyUI 节点加载时执行 `__init__.py`，期望这些模块在 Python 路径（根目录）下。

## 10 个文件全部被 import (跨文件验证)

| 文件 | 被谁 import |
|------|-------------|
| `asset_registry.py` | `__init__.py` (L51) |
| `spatial_layout.py` | `__init__.py` (L52) |
| `acting_skill.py` | `__init__.py` (L53) |
| `sound_skill.py` | `__init__.py` (L54) |
| `iteration_post.py` | `__init__.py` (L55) |
| `thirty_sec_six_act.py` | `__init__.py` (L56) + `cinematic_studio.py:32-33` |
| `cinematic_studio.py` | `__init__.py` (L57) + `thirty_sec_six_act.py:32-33` |
| `master_orchestrator.py` | character_arc/concept_pitch/director_storyboard/theme_philosophy (4 个) |
| `asset_registry_data.py` | thirty_sec_six_act/cinematic_studio/master_orchestrator (3 个) |
| `style_prefix_data.py` | character_arc/concept_pitch/director_storyboard/thirty_sec_six_act/cinematic_studio/master_orchestrator/theme_philosophy (7 个) |

## 后果

如果移到子目录:
1. `__init__.py` 找不到模块 → 43 节点加载失败
2. 内部 cross-import 失败 → ComfyUI 启动 crash
3. 所有 851+118 = 969 个测试失败

## 解决方案

**保持现状** (推荐) - 这 10 个文件留在根目录 + `__init__.py` 直接顶级导入。

**或者** (如要目录化):
- 改 `__init__.py` 用 `sys.path.insert(0, ...)` + 改所有 import 为相对路径
- 工作量大且风险高，不推荐

## Phase 36.4 命名变更历史

| 旧名 | 新名 | 原因 |
|------|------|------|
| `phase14_asset_registry.py` | `asset_registry.py` | Phase 14 是历史编号，按功能命名 |
| `phase14_spatial_layout.py` | `spatial_layout.py` | 同上 |
| `phase14_acting_skill.py` | `acting_skill.py` | 同上 |
| `phase14_sound_skill.py` | `sound_skill.py` | 同上 |
| `phase14_iteration_post.py` | `iteration_post.py` | 同上 |
| `phase14_30s_six_act.py` | `thirty_sec_six_act.py` | Python 不支持数字开头的标识符 |
| `phase14_cinematic_studio.py` | `cinematic_studio.py` | 同上 |
| `phase14_master_orchestrator.py` | `master_orchestrator.py` | 同上 |
| `phase14_six_documents.py` | `asset_registry_data.py` | 6 段是数据，不是主节点 |
| `phase14_style_prefix.py` | `style_prefix_data.py` | 风格前缀是数据，不是主节点 |

**类名同步重命名**:
- `Phase14AssetRegistry` → `AssetRegistry`
- `Phase14SpatialLayout` → `SpatialLayout`
- `Phase14ActingSkill` → `ActingSkill`
- `Phase14SoundSkill` → `SoundSkill`
- `Phase14_30sSixAct` → `ThirtySecSixAct`
- `Phase14_CinematicStudio` → `CinematicStudio`
- `IterationPostPro` (不变)
