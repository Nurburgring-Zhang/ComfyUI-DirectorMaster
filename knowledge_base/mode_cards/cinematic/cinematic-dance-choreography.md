---
mode_id: cinematic-dance-choreography
node: DirectorMasterCinematic
name: 舞蹈编排
one_liner: 全景-跟拍-脚部-环绕四镜组，多机位舞步同步
applicable: [舞蹈, 群戏仪式, 舞台表演]
intensity: medium
style_tags: [舞蹈编排, 法哈蒂, 毕赣, 多机位, 群戏]
aliases: []
---

## 意图

舞步的多机位语法：3s 全景群舞 → 2s 跟拍领舞 → 1.5s 脚部特写 → 3s 环绕收束，节拍同步。与 演唱会纪录 的差别是对象（舞蹈 vs 演唱）与机位节奏（5s 组 vs 8s 均值）。

## 核心手法

- 组公式：`PACING_GROUP_FORMULAS["舞蹈编排"]=(5.0s, 3镜, 18组上限)` 分支 C——组数=ceil(场秒/5)，动态加组硬顶 600；`PACING_TARGET_AVG_DUR["舞蹈编排"]=3.0`。
- 四镜模板：`PACING_STYLES["舞蹈编排"]` —— 全景 35mm 固定 3.0s（音乐+脚步）→ 中景 50mm 跟拍 2.0s → 特写 85mm 俯拍脚/手 1.5s（脚步+节拍）→ 全景 24mm 环绕 3.0s（音乐高潮）。
- 缩放覆盖：expand_pacing_shots 缩放+归一；脚部特写承担细节锚点（物件/服装细节由场景 objects 补充）。
- 声音设计：脚步/节拍声景 + 4 层配比——舞蹈的节奏主体在声音字段。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 目标时长(分钟) | 舞段（0.5-5min） | 镜数=场秒/5 均值；60s 约 12 镜 3 组 |
| 节奏风格 | 无(默认)=已钉 | 与 节奏风格="舞蹈编排" 同键；"🎲 随机" 不生效 |
| 核心数据包 | Core 32 字段 JSON | 舞蹈人数/队形依赖场景描述——未写时 c3 补名（年代池），"群戏"语义弱化为 2-3 人 |
| 运镜风格_多选 | 空 | 多机位语义已由模板四镜承担；填弧值会覆盖非保留镜的模板运镜，破坏机位设计 |

## 已知坑

- _classify_pacing 把 "舞蹈编排" 归"蒙太奇"大类——导演偏置替换只在 auto 路径生效，本模式钉死后该归类不参与。
- 舞步细节（舞种/动作名）不在模板——芭蕾/街舞/民族舞产出同一组机位文案，舞种感需场景描述与上游美术/角色输入补充。
- 组上限 18→动态 600：超长舞段会机械循环四镜组，编排感递减。

## 节点映射

- 实现文件：aggregator/cinematic_studio.py；aggregator/pacing_engine.py；aggregator/feature_film_engine.py
- 分支/函数：MODE_TO_PACING["舞蹈编排"]="舞蹈编排" → generate_feature_shots 分支 C → PACING_GROUP_FORMULAS["舞蹈编排"] → expand_pacing_shots
- 数据来源：pacing_engine.PACING_STYLES["舞蹈编排"]（法哈蒂/毕赣/皮娜·鲍什 masters + 4 镜序列）；pacing_engine._classify_pacing
