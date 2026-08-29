---
mode_id: script-director-storyboard
node: DirectorMasterScript
name: 导演分镜
one_liner: 镜头级分镜表：景别/焦段/机位/运动/时长/声音/转场，镜头数随时长缩放
applicable: [分镜脚本, 拍摄前置, 剪辑参考]
intensity: high
style_tags: [镜头表, 时长感知, 景别焦段, 转场设计]
aliases: [分镜脚本]
---

## 意图

本节点唯一的镜头级输出：每镜给景别/焦段/机位角度/运动/时长/表演焦点/声音/情绪/光影/转场/叙事目的。与 Cinematic 节点分镜的差别：这里跟剧本节点共用输入且按目标分钟数缩放镜头量，输出是文本表而非节奏签名模板。

## 核心手法

- `_build_storyboard_template`（script_studio.py:565）双通道：目标时长 ≥20min 走 feature 引擎 `generate_feature_scenes`+`generate_feature_shots`（feature_film_engine.py:3226）——镜头数随时长缩放（120min 默认实测 873 镜），每场按 story_function 自动选节奏风格（长镜类叠化模拟/快闪密集/慢镜 8-30s 慢放）；<20min 走 `scene_engine.generate_shots`（scene_engine.py:678）固定 6 镜短表。
- 长片镜头 >60 时防输出爆炸：只渲染每场首镜代表，头部注明"镜头表共 N 镜，覆盖 Xmin"（:594-597）。
- 每镜字段含故事弧递进（stage 情绪/色彩/光影/材质/氛围）与"一个镜头只做一件事"五选一叙事目的。
- 情绪演变弧（核心包 `_情绪演变弧`）传入 feature 场次生成，场头情绪随进度推进。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 目标时长(分钟) | 0（自动→120→873 镜） | 20min 阈值切通道：≥20 随时长缩放（3min 反例=6 镜短表），<20 恒 6 镜；≥110 归 120 桶 |
| 节奏控制 | 无(默认)→中速 | 不进分镜通道（维度 footer 声明而已）；节奏风格由每场 story_function 自动定 |
| 情绪基调 | 继承核心包 | 进表头行；`_情绪演变弧` 多值时逐场推进 stage_emotion |
| 核心数据包 | Core.核心数据包 | `_导演意图_观众应感到` 进场次 intent；缺失时占位"核心道具/场景"进焦点文案 |

## 已知坑

- 120min 默认输出 873 镜但正文只渲染 35 行首镜——总镜数与展示镜数不一致是设计内防爆炸行为（头部有覆盖说明），勿把 35 当实际镜头量。
- <20min 短表走 scene_engine 旧通道：不消费 pacing/density_scale（feature 引擎的节奏风格/密度机制只在 ≥20min 生效）——5min 与 15min 输出同为 6 镜。
- 镜级时长达 14.7s 一类小数（长镜 60s 上限切分产生），引用到视频模型时需按目标模型的单镜秒数上限再切。

## 节点映射

- 实现文件：aggregator/script_studio.py
- 分支/函数：TEMPLATE_BUILDERS["导演分镜"]→`_build_storyboard_template()`（:565）；≥20min 分支 :574-578（generate_feature_scenes/generate_feature_shots）；<20min 分支 :579（generate_shots）；截断逻辑 :588-597
- 数据来源：aggregator/feature_film_engine.py::generate_feature_shots（:3226）+ aggregator/scene_engine.py::generate_shots（:678）+ parse_scene
