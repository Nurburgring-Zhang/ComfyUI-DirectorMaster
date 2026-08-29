---
mode_id: cinematic-dialogue-long-take
node: DirectorMasterCinematic
name: 对话长镜
one_liner: ≤30s双人对切长镜组叠化，一整段对话不被剪碎
applicable: [深度对话, 情感对峙, 潜台词场面]
intensity: low
style_tags: [对话长镜, 阿巴斯, 李安, 双人对切, 潜台词]
aliases: []
---

## 意图

让对话的时间不被剪辑：双人对切中景 30s 内一组、叠化衔接，语言与沉默的重量自己显现。与 长镜大师 的差别是构图（双人 vs 单人日常）与声音主体（对白 vs 环境音）。

## 核心手法

- 分支 A：`MODE_TO_PACING["对话长镜"]="对话长镜"` —— per_shot_max=30.0，镜数=ceil(场秒/30)，cut=叠化；90s 对话=3 镜各 30s。
- 模板档型：`PACING_STYLES["对话长镜"]` 中景双人对切 50mm、平视/微微过肩、dur=60（模板语义）——focus_tpl="{c1} 和 {c2} 对坐/并排, 60s 不切, 一整段对话/沉默"；sound_tpl="完整对话 + 留白 + 呼吸, 偶尔环境音, 不配乐"。
- 角色绑定：c1/c2 来自场景解析 characters（不足 2 人时 c2=c1 复用）——对切双方与输入角色一致；导演池 8 条（李安式饭桌=战场/筷子=武器…）按镜号哈希注入 director_note。
- 时间切片：开始/中段/收束切片提示标注对话的微观推进（沉默→试探→摊牌）。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 目标时长(分钟) | 对话场（0.5-3min） | 镜数=场秒/30；60s→2 镜——"完整对话"语义靠 dur 覆盖保证 |
| 节奏风格 | 无(默认)=已钉 | 与 节奏风格="对话长镜" 同键；"🎬 随机"不存在——"🎲 随机" 不生效保持钉死 |
| 核心数据包 | Core 32 字段 JSON | _潜文本强度 影响剧本侧潜文本渲染；分镜侧对峙感来自 stage_emotion 张力档与 actor_note 池（"沉默=台词"等 8 条） |
| 景别偏好 | 无(默认) | 非 ND 覆写"中景双人对切"——改特写会变正反打碎切语义，改全景丢表情，建议保持 ND |

## 已知坑

- 场景只解析出 1 个角色时 c2=c1——出现"自己和自己对坐"的模板文案；双人对话请确保场景描述含两个角色。
- 模板 dur=60 与分支 A 实际 dur（≤30s）不一致（同游走长镜，模板文案未同步）——以 dur 字段为准。
- "中景双人对切"是复合景别，不参与 D1 景别 ±1 档偏移（仅单一标准景别参与）——同簇差异化靠焦点/角度变体。

## 节点映射

- 实现文件：aggregator/cinematic_studio.py；aggregator/pacing_engine.py；aggregator/feature_film_engine.py
- 分支/函数：MODE_TO_PACING["对话长镜"]="对话长镜" → generate_feature_shots 分支 A（per_shot_max=30.0）→ _make_pacing_shot（director_notes_by_pacing["对话长镜"] 8 条池 + 时间切片）
- 数据来源：pacing_engine.PACING_STYLES["对话长镜"]（阿巴斯/李安/王家卫 masters）；aggregator/scene_engine.parse_scene characters
