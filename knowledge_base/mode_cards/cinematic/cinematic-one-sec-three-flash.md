---
mode_id: cinematic-one-sec-three-flash
node: DirectorMasterCinematic
name: 一秒三闪
one_liner: 0.3s×3+1s收束的快闪组序列，情绪爆发/嗨爆瞬间专用
applicable: [情绪爆发顶点, 动作高潮, MV高潮段]
intensity: high
style_tags: [一秒三闪, 王家卫, 吴宇森, 快闪, 0.3s]
aliases: [三连闪]
---

## 意图

把"一秒"拍成完整叙事：0.3s×3（表情→动作→反应）+ 1.0s 收束，专用于情绪爆破点。与 抖音超快（持续 0.5-1s 快剪）的差别是三闪是"组"结构——一组 4 镜 1.9s 内完成 看见/做/结果 的闭环。

## 核心手法

- 组公式：`PACING_GROUP_FORMULAS["一秒三闪"]=(1.9s, 4镜, 25组上限)`，走分支 C——镜数=组数×4，组数=ceil(场秒/1.9)，超上限时动态加组（硬顶 600 组）保覆盖；`PACING_TARGET_AVG_DUR["一秒三闪"]=1.0`。
- 四镜模板：大特写 85mm 瞳孔收缩 0.3s（心悸一拍）→ 特写 50mm 快推动作凝固 0.3s → 中景 35mm 快摇环境反应 0.3s（跳切）→ 全景 24mm 拉远 1.0s 叠化收束"让观众回过神"。
- 缩放保护：`expand_pacing_shots` 按场时长缩放每组时长，0.3s 镜受 max(0.3,…) 下限保护不会缩到负值；收束镜承担时长缺口的再归一。
- 大师注释池：director_note 按"一秒三闪"池 8 条哈希选取（王家卫《旺角卡门》开场式/吴宇森慢镜+三连击/诺兰三镜意识流）。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 目标时长(分钟) | 爆点段落（秒级-分钟级） | 只改组数；0.3s 瞬间档型不变；长场靠加组，30s 场约 8 镜 2 组 |
| 节奏风格 | 无(默认)=模式已钉 | 与 节奏风格="一秒三闪" 完全同键；选其他节奏整场替换；"🎲 随机" 不生效 |
| 剪辑节奏 | 无(默认) | 极快×0.3 会把 0.3s 镜乘成 0.09s 显示且不再归一 → 总时长覆盖失效；建议保持 ND |
| 直觉风险 | 无(默认) | chaotic 档 R8 会给运动镜加"跳切"标注、R1 把高张力镜时长×1.5（上限60s）→ ±1% 覆盖失效 |

## 已知坑

- 0.3s 镜在下限保护下不会被缩放改变——整组时长缺口全部由 1.0s 收束镜吸收，收束镜可能被缩到 0.3s，三闪的"回神"节拍消失；对精度敏感时按场拆输入。
- 快闪组与子弹时间同属"快闪"签名簇吗——不是：签名 note 分别为 "0.3s×3 情绪爆发" 与 "0.5-2s 360° 静止环绕"，d1 探针按 note 分簇；同簇内（如与同名节奏风格直选）语法指纹靠 mode_seed 变体唯一。
- ten_rounds T9 对 节奏风格 下拉 19 选项含"一秒三闪"全执行断言——该下拉与本模式同键，跑回归时两者输出同源。

## 节点映射

- 实现文件：aggregator/cinematic_studio.py；aggregator/pacing_engine.py；aggregator/feature_film_engine.py
- 分支/函数：MODE_TO_PACING["一秒三闪"]="一秒三闪" → generate_feature_shots 分支 C → PACING_GROUP_FORMULAS["一秒三闪"] → expand_pacing_shots → _make_pacing_shot（director_notes_by_pacing["一秒三闪"] 8 条池）
- 数据来源：pacing_engine.PACING_STYLES["一秒三闪"]（王家卫/吴宇森/诺兰 masters + 4 镜序列）；feature_film_engine.PACING_TARGET_AVG_DUR
