# ComfyUI-DirectorMaster V14.3-MERGED

导演级影视提示词聚合节点系统 — 13 个超级节点，534 导演数据库驱动。

V14.3-MERGED = V14.2 审计基线（全部 P0 修复）+ V14.1-clean 分叉合并（9 项孤儿库复活接线）+ 阶段 1/2 质量深化。

## 安装

整个目录放入 `ComfyUI/custom_nodes/`，重启 ComfyUI。无第三方依赖（可选 torch/PIL/numpy 用于 IMAGE 参考槽）。

自检：`python doctor.py`（6 类诊断：安装路径/环境/模块导入/节点注册/知识库/复活接线消费验证）。

## 13 节点

| 节点 | 能力 |
|---|---|
| DirectorMasterCore | 起点：统一电影提示词 + 核心数据包（11 维 + 534 导演库） |
| DirectorMasterScript | 剧本 46 模式（长片/短剧/短视频/动漫/绘本/MV/广告/纪录片/互动剧/钩子/对白/角色弧） |
| DirectorMasterVibe | 创意 23 模式（15 创意 + 8 设计：电商/海报/品牌/PPT/图表/三视图/爆炸图/流水线图） |
| DirectorMasterArt | 美术 3 模式（美术指导/空间一致性/空间布局） |
| DirectorMasterSound | 声音 4 模式（声音设计/音乐/声音层/沉默） |
| DirectorMasterCinematic | 分镜 63 模式（电影工作室/节奏大师/短剧/动漫/绘本/MV/广告/纪录片分镜） |
| DirectorMasterCharacters | 角色 42 模式（角色/环境/服化道/参考图 → 6 路输出） |
| DirectorMasterAsset | 资产 41 模式（含 HellGrind 资产库 → IP-Adapter/参考图锁定） |
| DirectorMasterSummary | 终极汇总 3 路（完整制作手册/JSON 交付包/项目索引） |
| DirectorMasterRouter | 通用路由（7 目标模型，H3 深度 IR 5 模式 + EDL） |
| DirectorMasterVideoRouter | 5 视频模型超级路由（Seedance/LTX/Wan/Hailuo/Sora） |
| DirectorMasterArchive | 归档（真实写盘 + 磁盘持久化版本控制 + TXT/JSON/MD/HTML 格式多选） |
| DirectorMasterFinal | Summary 兼容别名 |

旧工作流兼容：设环境变量 `DIRECTORMASTER_LEGACY_NODES=1` 恢复全部 59 节点。

## 数据聚合（真实消费，非装饰）

534 导演 12 维档案、120 影视场景库、15 大师剧本 DNA、25 故事感总纲、儿童年龄分级、14 真实短剧案例、Seedance 2.5 能力边界、Higgsfield 6 份项目记忆文档、CINEDANCE 15 块视觉骨架、AIGC 42 环节 + 留白/运镜三定律、大师级影视语言原则、8 设计模式系统。全部惰性导入 + 异常降级，缺失零影响。

## V14.3-MERGED 关键指标（实测）

- 全模式执行：246 模式全通过，输出唯一性按节点 46/23/3/4/63/42/41/7/6/11
- Cinematic 镜头语法指纹（景别/运镜/焦段/时长）：63/63 唯一（含 4 个同节奏簇）
- 同档期形态模式正文相似度：0.27-0.56（审计基线 0.91，门槛 <0.7）
- 互动剧分支树：可解析 JSON，2 选择点 × ≥2 选项，3 结局，零悬空引用
- 版本存储：15 轮提交 9.7KB（blob 去重 + gzip），回滚逐字节还原（sha256 校验）
- 时长覆盖：90/120min 全部 63 模式 ±1% 内
- 浮点伪影：0（情感强度/张力/节拍表统一 1 位小数）
- 结构硬指标：中点≈50%，灵魂黑夜 70-73%，高潮 82-92%

## 测试

```
python doctor.py                     # 6 类自检
python tests/test_all_modes.py       # 13 节点 × 全模式回归
python tests/test_workflows.py       # 工作流 JSON 有效性
python tests/d1_grammar_probe.py     # 同簇镜头语法唯一性
python tests/d2_similarity_probe.py  # 形态模式正文相似度
```

## 工作流

`workflows/MINIMAL_PIPELINE_V8.2.json`（最小管线）、`workflows/MEGA_PIPELINE_V8.3.json`（全链路）。

## 定位说明

本系统是导演级提示词转译与创作引擎：把导演的已知风格特征与剧作方法论转译成结构化剧本/分镜/视频模型提示词。最终画面质量取决于下游视频模型。
