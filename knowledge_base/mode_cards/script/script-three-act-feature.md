---
mode_id: script-three-act-feature
node: DirectorMasterScript
name: 三幕剧长片
one_liner: 经典三幕骨架锁定的长片剧本，14 拍节拍展开为 35 场
applicable: [剧情长片, 家庭剧, 爱情长片, 通用叙事]
intensity: high
style_tags: [三幕结构, 经典节拍, 张力弧, 长片体量]
aliases: [三幕剧]
---

## 意图

用户明确要亚里士多德式"建置—对抗—解决"三幕结构时选它。与"完整长片剧本"的差别：叙事结构被模式名锁定为三幕剧，节拍主体强制走 `_beats_drama_three_act`，不随"叙事结构"下拉漂移。

## 核心手法

- `STRUCTURE_THEORY_MAP["三幕剧长片"]="三幕剧"`（script_studio.py:1547）覆盖叙事结构下拉；同一键驱动两条链：STORY_BEATS["三幕剧"] 9 拍附录 + feature engine `_normalize_theory`→three_act。
- `_beats_drama_three_act`（feature_film_engine.py:125）14 拍骨架（起(建立)张力2 → 合(高潮)张力10 → 合(尾声)张力3）按 `_expand_beats_to_n` 扩到目标场数（120min 默认 35 场）。
- `_shape_tension_curve` 按"转 (转折"等关键词识别结构位塑形张力：波浪上升、高潮强制 10、开场钳制 ≤4.5。
- 场次地点按 story_function 关键词选池：高潮/对决/失去 → 强制外景 climax 池。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 叙事结构 | 无(默认)→三幕剧(经典) | 被模式名静默覆盖为"三幕剧"——选"英雄之旅"等只改变附录节拍文本，节拍主体仍是三幕 |
| 目标时长(分钟) | 0（自动→120→35 场） | 90min→25 场、60min→15 场、30min→8 场；<0.5min→1 场 |
| 对白密度 | 无(默认)→适中(标准对白) | "零对白(纯视觉)"→全片对白池 None，场次只余动作行 |
| 核心数据包 | Core.核心数据包 | 缺失时角色回落"主角/副线"，道具按年代默认池（现代=手机/便签/雨伞） |

## 已知坑

- 结构锁定是 V14.2 设计内行为（commit 注释明示"结构即模式定义"），但 UI 上叙事结构下拉仍可选 30+ 值，易被误解为生效——实际只影响尾部【剧情推进】附录。
- 张力曲线塑形对 n<3 的场次表直接跳过；1min 以下输入（1 场）无张力弧可言。
- "动作(任务递进)"等类型结构在 `_normalize_theory` 里也复用商业 15 拍/三幕族生成器，跨模式节拍同构属设计内。

## 节点映射

- 实现文件：aggregator/script_studio.py
- 分支/函数：build() :1762 `if mode in STRUCTURE_THEORY_MAP` → `_build_full_screenplay()`（:1413，story_theory=三幕剧）
- 数据来源：aggregator/feature_film_engine.py::_beats_drama_three_act（:125）、_normalize_theory（:836）、get_beat_map（:2465）；STORY_BEATS["三幕剧"]（script_studio.py:84）
