---
mode_id: script-hero-journey-12-stages
node: DirectorMasterScript
name: 英雄之旅12阶段
one_liner: Campbell 12 阶段冒险骨架，从平凡世界到携宝归来的长片展开
applicable: [奇幻长片, 冒险片, 成长史诗, 神话重构]
intensity: high
style_tags: [英雄之旅, 神话结构, 冒险, 长片体量]
aliases: [英雄之旅]
---

## 意图

主角要走"召唤—门槛—试炼—深渊—复活—归来"完整旅程时选它。与救猫咪的差别：节拍位是坎贝尔神话学 12 阶段，中点不是"虚假胜利"而是"深渊逼近"，高潮位叫"复活"。

## 核心手法

- `STRUCTURE_THEORY_MAP["英雄之旅12阶段"]="英雄之旅12阶段"`：STORY_BEATS 同名 12 阶段附录 + `_normalize_theory`→hero_journey。
- `_beats_hero_journey`（feature_film_engine.py:83）12 骨架拍预设张力曲线：平凡世界 2 → 跨越门槛 7 → 深渊逼近 8 → 最大考验 9 → 复活 10 → 携宝归来 3。
- 场次地点池按拍名关键词分流："试炼/深渊"→ public+transit 池，"最大考验/失去一切"→ climax 池并强制外景。
- 结尾阶段锁定在锚点地点（`_is_edge_scene` 收束场强制用户场景锚），完成"归来"的地理闭环。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 叙事结构 | 无(默认) | 锁定为英雄之旅12阶段；"史诗(命运递进)"下拉在 `_normalize_theory` 里同样映射 hero_journey，节拍同构 |
| 目标时长(分钟) | 0（自动→120→35 场） | 12 骨架拍任意时长完整存在；30min→8 场时每阶段不足一场，靠 expand 合并 |
| 对白密度 | 无(默认)→适中(标准对白) | "独白为主(内心戏)"→dial_override=high，试炼/深渊拍对白量增 |
| 核心数据包 | Core.核心数据包 | 缺失时对手角色按年代补名（古装=故人/旧敌/少侠池），不留"对手"占位词 |

## 已知坑

- 场景描述含"史诗"类关键词时，类型通道（TYPE_BEAT_GENERATORS epic→hero_journey）与结构通道指向同一生成器——换叙事结构下拉可能看不出节拍差异。
- "获得宝物 · 灵魂黑夜"拍张力 9 但密度 low：想要高密度对白的高潮戏，该拍需靠 主题深度/对白密度 之外的手工补写。
- 模式名里"12阶段"不等于 12 场，见目标时长行的场数公式。

## 节点映射

- 实现文件：aggregator/script_studio.py
- 分支/函数：build() :1762 → `_build_full_screenplay()`（:1413）
- 数据来源：aggregator/feature_film_engine.py::_beats_hero_journey（:83）、_normalize_theory（:836）；STORY_BEATS["英雄之旅12阶段"]（script_studio.py:88）
