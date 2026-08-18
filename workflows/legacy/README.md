# legacy 工作流存档

此目录为 V14-FINAL 节点收敛 (59→13) 之前的历史工作流存档，引用旧节点类型
(DirectorMasteryNode / CinematicStudio 等)，默认 13 节点注册下**不可加载**。

仅当设置环境变量 `DIRECTORMASTER_LEGACY_NODES=1` (恢复注册全部 59 节点) 时可用，
此时 `validate_workflows.py` 也会一并校验本目录。

现行管线请使用上级目录的 `MINIMAL_PIPELINE_V8.2.json` / `MEGA_PIPELINE_V8.3.json`。
