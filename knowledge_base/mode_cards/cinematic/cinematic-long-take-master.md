---
mode_id: cinematic-long-take-master
node: DirectorMasterCinematic
name: 长镜大师
one_liner: 全场戏固定机位长镜组（单镜≤30s叠化模拟），侯孝贤/是枝裕和式凝视
applicable: [艺术片, 日常记录, 情感积蓄段落]
intensity: low
style_tags: [固定长镜, 侯孝贤, 是枝裕和, 叠化, 真实感]
aliases: [固定长镜]
---

## 意图

把全场戏钉在固定机位上：不靠剪辑制造情绪，靠时间的真实流动。输出为"多镜 ≤30s + 镜间叠化"的长镜组（连续感模拟），与 游走长镜（移动跟拍）、对话长镜（双人对切）的差别是机位不动、焦点在日常物件与留白。

## 核心手法

- 节奏钉死：`MODE_TO_PACING["长镜大师"]="固定长镜"`，全场戏走 `generate_feature_shots` 分支 A——`per_shot_max=30.0`，`base_shots=ceil(场秒/30)`，每镜 dur=场时长/镜数（≤30s），target_shots>1 时 cut=叠化。
- 模板取材：`PACING_STYLES["固定长镜"]` 提供中景/50mm/平视模板与"60s 真实时间、不配乐、同期声+留白"的声音设计；focus_tpl 注入 "{c1}在{location}中…让观众'住在'这一分钟里"。
- 时间切片标注：`_make_pacing_shot` 对 固定/对话/游走 三类长镜按镜序加"开始切片（物件先于人物）/中段切片（人物进入动作被稀释）/收束切片（人物没动物件被光移动）"提示。
- 物件细节池：焦点由通用物件变体池（6 模板：被光线照出细节/静静待在原处/使用过的痕迹…）按 mode_seed+镜号哈希选取，避免"被光线照出细节"复读。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 核心数据包 | Core 32 字段 JSON | _情绪基调 带"孤独/空"等词且启用直觉风险时触发 R4 孤独不对称角标——与长镜的静观语义叠加，属预期强化 |
| 节奏风格 | 无(默认)=模式已钉固定长镜 | 显式选其他节奏（如抖音超快）会整场替换长镜——本模式与该下拉互斥使用；"🎲 随机" 不生效 |
| 运镜风格 | 无(默认) | 非 ND 逐镜覆写"固定"签名运镜（长镜身份消失）；"🎲 随机" 把字面量写进运镜字段 |
| 目标时长(分钟) | 与场戏规划一致 | 分支 A 镜数=ceil(场秒/30)，时长只改镜数不改长镜属性；±1% 总时长覆盖仍成立（无剪辑节奏/直觉干预时） |

## 已知坑

- MODE_PACING 里 dur_scale=6.0 对本模式无效：pacing 模式不叠加密度（density_scale 恒 1.0），镜数完全由分支 A 公式决定；note 只进版本行"节奏签名"。
- 30s 上限是设计行为（V14.3 红队P1：固定/对话长镜 ≤30s 多镜叠化模拟），模板文案里的"60s 不切"是修辞——真单镜请用 一镜到底（per_shot_max=整场时长）。
- 焦段/角度的 D1 变体（45/43/58mm 等同档池）会让同输入两次生成焦段字样略不同，这是 V14.3 D1 差异化，非漂移。

## 节点映射

- 实现文件：aggregator/cinematic_studio.py；aggregator/pacing_engine.py；aggregator/feature_film_engine.py
- 分支/函数：MODE_TO_PACING["长镜大师"]="固定长镜" → generate_feature_shots 分支 A（per_shot_max=30.0）→ _make_pacing_shot（时间切片 + 物件变体池）
- 数据来源：pacing_engine.PACING_STYLES["固定长镜"]（masters/shot_sequence）；_FOCAL_VARIANTS/_STATE 后缀池；format_templates.MASTER_VIDEO_PRINCIPLES
