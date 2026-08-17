# ComfyUI-DirectorMaster

**导演级影视提示词聚合节点系统** — 13 个超级节点 / 534 导演数据库 / 246 创作模式，覆盖剧本 → 创意 → 美术 → 声音 → 分镜 → 角色/资产 → 汇总 → 视频模型路由 → 归档版本控制的完整创作链路。

当前版本：**V14.3-MERGED**（V14.2 审计基线 + V14.1-clean 分叉合并 + 阶段 1/2 质量深化）。

---

## 特性

- **导演风格数据库**：534 位导演 × 12 维风格档案（镜头/光/节奏/色彩/表演/构图/声音/情绪/物件/年代/5维标签），选导演即锁定其风格，支持模糊搜索（王家卫 / Kubrick / 诺兰 均可）
- **剧本引擎**：46 模式，30+ 叙事结构真实下场（三幕/五幕/救猫咪15拍/英雄之旅/起承转合/皮克斯22条/双线/非线性…），结构硬指标达标（中点≈50%，灵魂黑夜 70-73%，高潮 82-92%）
- **分镜引擎**：63 模式，节奏大师系统（快闪/长镜/蒙太奇/慢镜 4 类 21 种节奏风格），镜头语法指纹 63/63 唯一，总时长恒覆盖片长（±1% 内）
- **形态专精**：短视频/动漫/绘本/MV/广告/纪录片/互动剧/直播等 24 种形态各有专属场次骨架与执行层（同档期形态正文相似度 0.27-0.56）
- **互动剧分支树**：可解析 JSON 节点图（选择点 × ≥2 选项 × 多结局，零悬空引用）
- **AI 增强轨**：任意节点可接 OpenAI 兼容端点做剧本/分镜润色，内置质量门控（长度门/照抄 bigram 检测/反AI套话全词表扫描/SSRF 防护），无端点时走确定性模板轨
- **归档与版本控制**：真实写盘 + 磁盘持久化版本库（blob 去重 + gzip，并发安全，回滚逐字节还原），TXT/JSON/MD/HTML 多格式导出
- **零虚假设计**：无 mock/占位/硬编码空数据；注入的知识库全部为真实制作知识（120 场景库/15 大师剧本 DNA/14 真实短剧案例等），降级路径诚实上报

## 安装

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/Nurburgring-Zhang/ComfyUI-DirectorMaster.git
```

重启 ComfyUI 即可。无第三方依赖（可选 torch/PIL/numpy 用于 IMAGE 参考槽）。

安装后自检：

```bash
cd ComfyUI-DirectorMaster
python doctor.py
```

6 类诊断：安装路径 / Python 环境 / 模块导入 / 节点注册 / 知识库完整性 / 数据库接线消费验证。

## 快速上手

最小链路：

```
DirectorMasterCore → DirectorMasterScript → DirectorMasterCinematic → DirectorMasterSummary → DirectorMasterArchive
```

1. **DirectorMasterCore**：填项目名/导演/场景/情绪等 11 维，输出统一电影提示词 + 核心数据包
2. 下游节点用 forceInput 槽接核心数据包，按需接剧本/创意/美术/声音/角色/资产六维上游
3. **DirectorMasterSummary** 汇总为完整制作手册 + JSON 交付包
4. **DirectorMasterArchive** 写盘归档，可做版本提交/对比/回滚/选优

现成工作流在 `workflows/`：`MINIMAL_PIPELINE_V8.2.json`（最小管线）、`MEGA_PIPELINE_V8.3.json`（全链路）。

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

V14 之前的 46 个 legacy 细粒度节点已在 V14.3 彻底移除，其能力由 13 超级节点的模式下拉全覆盖。

## 数据聚合（真实消费，非装饰）

534 导演 12 维档案、120 影视场景库、15 大师剧本 DNA、25 故事感总纲、儿童年龄分级、14 真实短剧案例、Seedance 2.5 能力边界、Higgsfield 6 份项目记忆文档、CINEDANCE 15 块视觉骨架、AIGC 42 环节 + 留白/运镜三定律、大师级影视语言原则、8 设计模式系统。全部惰性导入 + 异常降级（stderr 诚实上报），缺失零影响。

## 质量验证（实测指标）

- 全模式执行：246 模式全通过，输出唯一性按节点 46/23/3/4/63/42/41/7/6/11
- Cinematic 镜头语法指纹（景别/运镜/焦段/时长）：63/63 唯一（含 4 个同节奏簇）
- 同档期形态模式正文相似度：0.27-0.56（门槛 <0.7）
- 互动剧分支树：可解析 JSON，2 选择点 × ≥2 选项，3 结局，零悬空引用
- 版本存储：15 轮提交 9.7KB（blob 去重 + gzip），回滚逐字节还原（sha256 校验），并发提交零丢失
- 时长覆盖：90/120min 全部 63 模式 ±1% 内
- 浮点伪影：0（情感强度/张力/节拍表统一 1 位小数）
- 结构硬指标：中点≈50%，灵魂黑夜 70-73%，高潮 82-92%
- 安全：密钥扫描 0 命中，SSRF 防护（禁 link-local/云 metadata/重定向），归档路径消毒

## 测试

```bash
python doctor.py                     # 6 类自检
python tests/test_all_modes.py       # 13 节点 × 全模式回归 (265 断言)
python tests/test_workflows.py       # 工作流 JSON 有效性
python tests/ten_rounds.py           # 十轮全量测试 (40 断言: 部署/功能/数据/链路/AI/质量)
python tests/f2_ai_track_e2e.py      # AI 轨端到端 (本地 OpenAI 兼容服务器, 真实 HTTP)
python tests/d1_grammar_probe.py     # 同簇镜头语法唯一性
python tests/d2_similarity_probe.py  # 形态模式正文相似度
```

## 目录结构

```
├── __init__.py              # 13 节点注册 (LEGACY=1 时 59 节点)
├── doctor.py                # 安装自检
├── aggregator/              # 13 超级节点 + 引擎 (场景/节拍/节奏/长片/LLM/版本存储/格式导出)
├── knowledge_base/          # 17 个知识库子模块 (摄影/叙事/类型/表演/镜头语汇/转场…)
├── workflows/               # 现行管线 (MINIMAL/MEGA) + legacy 存档
├── tests/                   # 回归与探针测试
└── docs/                    # 历史开发文档
```

## 版本历史

- **V14.3-MERGED**：V14.2 + V14.1-clean 合并（9 项数据库接线复活），阶段 1/2 质量深化（镜头语法差异化/形态骨架/互动剧分支树/版本存储工程化），并发安全与安全加固
- **V14.2**：P0 根治（假分镜/数据损坏/密钥清除），模式坍缩根治，结构节拍归位，4 项能力接线，保存格式多选
- **V14-FINAL**：节点收敛 59 → 13 超级节点

## 定位说明

本系统是导演级提示词转译与创作引擎：把导演的已知风格特征与剧作方法论转译成结构化剧本/分镜/视频模型提示词。最终画面质量取决于下游视频模型。
