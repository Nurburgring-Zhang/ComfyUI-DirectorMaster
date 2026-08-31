# 工作流目录 — 现行管线 + legacy 存档

**项目**: ComfyUI-DirectorMaster
**版本**: V16.1.1-MERGED

---

## 📂 现行管线（默认 17 节点注册即可加载）

| 文件 | 说明 | 节点数 | links |
|---|---|---:|---:|
| `MINIMAL_PIPELINE_V8.2.json` | 最小端到端管线 Core→Script→Cinematic→Final | 4 | 5 |
| `MEGA_PIPELINE_V8.3.json` | 全能力管线 Core/Script/Vibe/Art/Sound/Cinematic/Router/Archive/Final | 9 | 18 |

两个管线只引用现行注册节点类型（`DirectorMasterCore` 等 17 个注册节点），
拖入 ComfyUI 画布即可加载，端到端可运行。
校验命令: `python tests/test_workflows.py`（核对节点类型在注册表、widget 类型、链接完整性）。

---

## 📂 legacy/ 存档

`legacy/` 为 Phase 36.6 时期的历史工作流存档（17 个 `WORKFLOW_*.json` + 6 个 `MEGA_*.json`，共 23 个），
引用已收敛的旧节点类型（`DirectorMasteryNode`、`CinematicStudio`、各细粒度 Pro 节点等），
默认 17 节点注册下**不可加载**；设置环境变量 `DIRECTORMASTER_LEGACY_NODES=1`
（恢复注册全部 63 节点）后可用。详见 `legacy/README.md`。

现行使用请直接采用本目录顶层的两个管线 JSON。

---

## 🏗️ 现行管线架构

```
MINIMAL (4 节点):
  DirectorMasterCore → DirectorMasterScript → DirectorMasterCinematic → DirectorMasterFinal

MEGA (9 节点):
  DirectorMasterCore ─┬→ DirectorMasterScript ─┐
                      ├→ DirectorMasterVibe    ├→ DirectorMasterCinematic → DirectorMasterFinal
                      ├→ DirectorMasterArt     │                              ↓
                      └→ DirectorMasterSound ──┘                 DirectorMasterRouter
                                                                    ↓
                                                        DirectorMasterArchive
```

- 节点 output 允许"备而不用"（ComfyUI 节点 output 不必全部被消费，用户按需连接）。
- 节点可复用、可拆分组合；现行 18 注册节点均可单独使用或自行组网。

---

**V16.1.1-MERGED: 顶层 2 个现行管线（实测可加载）+ legacy/ 23 个历史工作流存档（环境变量开关）。**
