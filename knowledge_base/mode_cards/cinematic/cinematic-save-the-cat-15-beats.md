---
mode_id: cinematic-save-the-cat-15-beats
node: DirectorMasterCinematic
name: 电影救猫咪15拍分镜
one_liner: 按Blake Snyder 15拍展开节拍生成分镜，拍点位置受测试约束
applicable: [商业类型片, 强情节长片, 拍点验证]
intensity: high
style_tags: [救猫咪15拍, 商业结构, 节拍引擎, 长片分镜]
aliases: [Save the Cat 分镜]
---

## 意图

用 Blake Snyder 15 拍（开场画面→主题陈述→铺垫→催化剂→争论→进入第二幕→B故事→乐趣与游戏→中点虚假胜利→敌人逼近→失去一切→灵魂黑夜→决定→终局→结尾画面）做全片分镜骨架，适合需要逐拍核对商业节奏的项目。

## 核心手法

- 拍点引擎：`CINE_MODE_THEORY["电影救猫咪15拍分镜"]="救猫咪15拍"` → `_normalize_theory("救猫咪")→"save_the_cat"` → `_beats_save_the_cat` 输出 15 拍（act/story_function/密度/张力/shots 五元组），`_expand_beats_to_n` 按比例插值到 n 场。
- 拍点-节奏联动：auto 节奏按拍名查 STORY_FUNC_PACING——"中点"→一秒三闪、"失去"→一秒三闪、"灵魂的黑夜"→极慢抒情、"乐趣"→蒙太奇、"终局"→子弹时间，形成商业片的快慢交替。
- 密度标注：灵魂黑夜拍 density="low" → 对白低密度 + 全知俯瞰 POV 倾向；终局拍 tension=10 → 色彩/光影/材质/氛围全表拉满档。
- 位置断言兜底：ten_rounds T10 对救猫咪输出断言 中点 0.35-0.62、灵魂黑夜 0.62-0.75、高潮 0.72-0.97——拍点漂移会直接红测。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 目标时长(分钟) | 90-120（商业长片） | 桶化 ≥110→120/≥80→90；短时长（如 3min）15 拍压缩进 3 场，多拍合并为一场的 story_function，拍点位置断言仅对长片梯成立 |
| 核心数据包 | Core 32 字段 JSON | _导演风格=诺兰 → 张力整体 +1 且不跳拍（DIRECTOR_OVERRIDES），黑夜拍也会被推高；王家卫 → 20% 概率跳拍留白 |
| 节奏风格 | 无(默认)=按拍选型 | 钉死某节奏会抹掉 15 拍的快慢交替；"🎲 随机" 原样返回不命中映射，保持按拍选型 |
| 剧本输入 | Script.剧本输出 | 剧本驱动标注只取前 6 块；15 拍对应的剧本段若超过 6 块，后续拍无驱动标注 |

## 已知坑

- 拍点位置断言（中点/黑夜/高潮区间）是硬回归：修改 `_beats_save_the_cat` 拍序或 `_expand_beats_to_n` 比例会挂 ten_rounds。
- 灵魂黑夜拍的 story_function 写作"灵魂的黑夜"，ten_rounds 用 `灵魂的?黑夜` 正则同时兼容两种写法——卡内文案/下游解析须保留该拍名。
- 与 电影三幕分镜 同为 auto+density 1.0，差异在节拍生成器与签名 note（"Blake Snyder 15 拍分镜"）；同输入下两者正文差异主要来自拍点功能不同导致的节奏混编差异。

## 节点映射

- 实现文件：aggregator/cinematic_studio.py；aggregator/feature_film_engine.py
- 分支/函数：CINE_MODE_THEORY["电影救猫咪15拍分镜"] → _normalize_theory("救猫咪")→save_the_cat → THEORY_BEAT_GENERATORS["save_the_cat"]=_beats_save_the_cat → get_beat_map → generate_feature_shots
- 数据来源：_beats_save_the_cat 15 拍表（含每拍 tension/density/shots）；pacing_engine.STORY_FUNC_PACING；tests/ten_rounds.py T10 结构断言
