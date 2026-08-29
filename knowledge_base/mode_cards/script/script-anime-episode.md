---
mode_id: script-anime-episode
node: DirectorMasterScript
name: 番剧动漫剧本
one_liner: 24 分钟番剧单集：OP 前冷开场→A/B part→名场面→ED→预告 7 槽
applicable: [番剧单集, 24 分钟动画, 二次元连载]
intensity: medium
style_tags: [番剧格式, OP前冷开场, 名场面, 作画演出]
aliases: [动画剧本]
---

## 意图

写标准 24 分钟番剧单集时选它：结构位按番剧工业格式（冷开场/eyecatch/ED/预告）切分。与热血/校园/奇幻动漫专属模式的差别：本模式是通用番剧格式，不预设战斗/日常/冒险题材。

## 核心手法

- `FORMAT_SCENE_SKELETONS["番剧动漫剧本"]`（script_studio.py:975）7 槽：OP前冷开场·本集悬念→A part·主线推进→Eyecatch·中点过渡→B part·主线情感交汇→名场面·情绪高点→ED·情绪沉淀→下集预告；24min 恰在 ≤24 阈值内，场景数=7 槽。
- 执行层动漫分支（:1196-1201）逐场标注：作画 cut 数（本场 1/2/无作画 cut）、内心独白设计（1 句/无独白纯演出/与环境静默对视）。
- `FORMAT_MODE_FLAVOR`（:909）：A part 22min 主线、eyecatch 定格呼吸、名场面作画/配乐/演出三重叠加。
- 热血/校园/奇幻三模式与本模式共用动漫执行层分支代码，差异化全在骨架槽与 flavor。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 目标时长(分钟) | 0（自动→24） | 显式 ≤24 → 场景数仍=7 槽（骨架覆盖优先）；>24 → 走时长阶梯（30min→8 场），7 槽标签按比例映射 |
| 叙事结构 | 无(默认)→三幕剧(经典) | 节拍随下拉变化；"非线性(闪回/闪前)"适合回忆杀多的番剧集 |
| 对白密度 | 无(默认)→标准对白 | "独白为主(内心戏)"契合动漫内心独白+画面演出并用约定 |
| 核心数据包 | Core.核心数据包 | 角色解析给 A/B part 的人物关系；缺角色时回落"主角/副线" |

## 已知坑

- 24min 是 FORMAT_DURATION_MAP 的默认值也是骨架覆盖的上限边界（`target_minutes <= 24`）：设 24 与 20 输出场数相同（7 场），不会随短时长减场。
- "作画 cut"是给动画执行的演出标注，非分镜表；逐镜分镜由 Cinematic 节点承接。
- 下集预告槽固定要求"必须追的理由"，场景无连载规划时该槽内容为模板化悬念文案。

## 节点映射

- 实现文件：aggregator/script_studio.py
- 分支/函数：`_build_full_screenplay()`（:1413）+ FORMAT_SCENE_SKELETONS["番剧动漫剧本"]（:975）+ 执行层动漫分支（:1196）
- 数据来源：FORMAT_SCENE_SKELETONS/FORMAT_MODE_FLAVOR 内置表 + aggregator/feature_film_engine.generate_feature_scenes（24min→7 场经 scene_target=7）
