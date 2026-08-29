---
mode_id: cinematic-freeze-frame
node: DirectorMasterCinematic
name: 定格凝固
one_liner: 单帧凝固镜头组，音乐骤停+一拍静默的港片高潮语法
applicable: [高潮瞬间, 漫画感段落, 经典时刻]
intensity: medium
style_tags: [定格, 吴宇森, 北野武, 港片, 单帧延长]
aliases: [定格]
---

## 意图

把动作/表情钉成单帧：2s 定格 + 音乐骤停 + 一拍静默，让"瞬间"变"永远"。与 子弹时间 的差别是定格完全不动（连环绕都没有），与 慢镜高光 的差别是零运动而非慢运动。

## 核心手法

- 节奏钉死：`MODE_TO_PACING["定格凝固"]="定格"`（下拉名"定格凝固"经 RHYTHM_TO_PACING 同映射"定格"），走分支 C 特殊类——is_fast_pacing 命中（category="特殊"）。
- 单镜模板：`PACING_STYLES["定格"]` 特写 85mm 固定、cut="定格"、dur=2.0——focus_tpl="{c1} 的动作/表情, 凝固 2s, 港片高潮式"；sound_tpl="音乐骤停 + 一拍静默 + 慢放, 时间被拉长"。
- 镜数推导：`expand_pacing_shots` 按模板重复 shots_target 次（mode_seed 偏移起点），dur 缩放到场时长（上限 30s）+ 缺口归一——定格组之间用硬切/叠化衔接由模板 cut 决定。
- 状态后缀：focus 拼接 6 条状态变体池哈希（"在场, 但被时间困住/呼吸比动作先泄露…"），凝固帧带情绪注解。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 目标时长(分钟) | 高潮段（秒-1min） | 镜数=场秒/镜均时长；见下条坑——均值实际按 10.0s 默认推导，短场 1-3 镜 |
| 节奏风格 | 无(默认)=已钉"定格" | 选其他节奏整场替换；"🎲 随机" 不生效保持钉死 |
| 剪辑节奏 | 无(默认) | 变速/动静交替会奇偶交替放大/缩短 2s 模板 → 定格节奏变抖动；其余倍率同样破坏凝固语义且不再归一 |
| 构图法则 | 无(默认) | 非 ND 追加 note"构图: X"——单帧构图的视觉权重交给该下拉是合理用法；"🎲 随机" 字面量入 note |

## 已知坑

- 键名错位：`PACING_TARGET_AVG_DUR` 登记的是旧键 "定格凝固"（1.5），运行时传入键是 "定格" → `.get` 落默认 10.0s/镜——镜数按 10s 均值推导而非注释的 1.5s，短场镜数偏少是代码现状（V16.1.1 L-2 修复了归类但未动该表）。
- 定格模板 native dur=2.0<30 → 缩放上限 30s：长场单镜不会超 30s，但"单帧"语义在 >2s 缩放下会稀释（每镜被拉长成准静止）。
- 签名运镜"固定"在变体池内有同义词（固定/锁定机位/静止机位）——同簇 D1 差异会换词，语义不变。

## 节点映射

- 实现文件：aggregator/cinematic_studio.py；aggregator/pacing_engine.py；aggregator/feature_film_engine.py
- 分支/函数：MODE_TO_PACING["定格凝固"]="定格" + RHYTHM_TO_PACING["定格凝固"] → generate_feature_shots 分支 C（is_fast_pacing）→ expand_pacing_shots → _make_pacing_shot
- 数据来源：pacing_engine.PACING_STYLES["定格"]（吴宇森/北野武/昆汀 masters）；feature_film_engine.PACING_TARGET_AVG_DUR（键名错位现状）；_STATE 后缀池
