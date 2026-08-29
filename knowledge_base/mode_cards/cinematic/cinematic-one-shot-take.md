---
mode_id: cinematic-one-shot-take
node: DirectorMasterCinematic
name: 一镜到底
one_liner: 每场一镜无切覆盖整场时长，索科洛夫/席佩尔式极限调度
applicable: [技术极限段落, 舞台剧感, 沉浸整段]
intensity: low
style_tags: [一镜到底, 索科洛夫, 俄罗斯方舟, 无切, 穿越调度]
aliases: []
---

## 意图

时间不被剪辑：每场输出 1 镜、时长=整场时长、cut=无切，观众呼吸与电影同步。与 游走长镜（≤60s 多镜）的差别是真单镜——V14.3 红队P1 专门分化了四类长镜的单镜上限，本模式是唯一"1 镜=整场"的实现。

## 核心手法

- 分支 A 特例：`MODE_TO_PACING["一镜到底"]="一镜到底"` → 分支 A——`per_shot_max = max(60.0, 场时长秒)`，base_shots=ceil(场秒/上限)=1，target_shots=1，per_shot_dur=场时长，cut="无切"。
- 模板档型：`PACING_STYLES["一镜到底"]` 全景到中景 35mm 环绕调度、dur=480——focus_tpl="整段 8 分钟一镜, 穿越多个时代/空间…观众的注意力全在调度"；sound_tpl="完整时空, 同期声+音乐进入+时代切换音"。
- 时长覆盖：单镜即场时长 → 总时长覆盖天然成立（±1%）；密度参数对本模式无效（pacing 模式不叠 density）。
- 时间切片豁免：时间切片提示只给 固定/对话/游走 三类——一镜到底走"穿越"语义不切片。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 目标时长(分钟) | 段落级（1-8min/场） | 场数=场数梯（如 3min→3 场）→ 输出 3 镜（每场 1 镜）；"全片一镜"需单场输入——多场输入是每场一镜不是整片一镜 |
| 节奏风格 | 无(默认)=已钉 | 与 节奏风格="一镜到底" 同键；"🎲 随机" 不生效 |
| 剪辑节奏 | 无(默认) | 变速/动静交替会奇偶改写 dur 且不再归一——无切长镜时长失真最刺眼；留白/跳切等 7 档无效果 |
| 运镜风格 | 无(默认) | 非 ND 覆写"一镜到底跟拍"签名——覆盖后 note 仍标一镜到底但运镜字段已变，语义分裂 |

## 已知坑

- "一镜到底"以场为单位：get_beat_map 会按目标时长拆场（30min→8 场→8 镜），想要"真·整段一镜"必须让输入对应单场（或接受每场一镜的拼接语义）。
- focus 的"480s/8 分钟"是模板修辞，实际 dur=场时长（可能 60s 也可能 600s）。
- per_shot_max=max(60, 场时长)：场时长 <60s 时单镜仍 60s 起——会被分支 A 的 per_shot_dur=场时长/1 覆盖回真实场时长，60s 只是下限声明。

## 节点映射

- 实现文件：aggregator/cinematic_studio.py；aggregator/pacing_engine.py；aggregator/feature_film_engine.py
- 分支/函数：MODE_TO_PACING["一镜到底"]="一镜到底" → generate_feature_shots 分支 A（per_shot_max=max(60.0, duration_min*60) 特例）→ _make_pacing_shot
- 数据来源：pacing_engine.PACING_STYLES["一镜到底"]（索科洛夫《俄罗斯方舟》/席佩尔《维多利亚》masters）
