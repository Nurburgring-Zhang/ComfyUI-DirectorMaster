---
mode_id: script-full-length-screenplay
node: DirectorMasterScript
name: 完整长片剧本
one_liner: 120min 级完整剧本：35 场专业场次格式+架构+角色弧一次成型
applicable: [电影长片, 网络电影, 剧情长片, 精品网剧]
intensity: high
style_tags: [长片体量, 专业场次格式, 结构完整, 可直接拍摄]
aliases: []
---

## 意图

输入场景与导演风格，直接产出可拍摄的完整长片剧本：专业场次格式正文 + 剧本架构 + 角色弧光三段合一。与"三幕剧长片"等结构模式的本质差别：本模式是通用长片，叙事结构由"叙事结构"下拉真实驱动（V14.2 起不再被模式名静默覆盖），可选 30+ 结构变体。

## 核心手法

- 默认落 `_build_full_screenplay`：120min 默认按 `get_beat_map` 工业阶梯出 35 场（90-150s 一场），每场带 幕次/阶段/戏剧张力/情绪 标注的 heading。
- 节拍由 feature engine 按 叙事结构+类型+情绪+导演 实时计算，再经 `_shape_tension_curve` 重塑为波浪上升→88% 高潮顶点→释放的电影张力弧。
- 对白跨场次无放回抽样 + 同模板全片最多复用 3 次的复用预算，消除复读感；开场/收束场强制锚定用户场景地点。
- 输出尾部并入 strip_decor 版剧本架构与角色弧光，再附 大师剧本 DNA（15 大师命中时）与 120 场景库匹配块（tests/test_all_modes.py 有"大师剧本DNA注入/120场景库注入"断言）。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 剧本模式 | 完整长片剧本 | 非法值在 build() 回落"完整剧本"键 → 仍走 `_build_full_screenplay`，不报错 |
| 叙事结构 | 无(默认)→三幕剧(经典) | 选任意 30+ 结构真实生效；`🎲 随机` 从结构表随机选 |
| 目标时长(分钟) | 0（自动→120） | ≥110 归 120、≥80 归 90、≥50 归 60、≥20 归 30；>0 保留秒级小数（下限 0.05）；非数字字符串解析失败维持原值 |
| 对白密度 | 无(默认)→适中(标准对白) | "零对白(纯视觉)"→dial_override=none→全片对白池置空，纯视觉叙事 |
| 潜文本强度 | 无(默认)→中(每句1层) | 零→不渲染〔潜文本〕行；弱=每4场1行；中=每2场1行；强/极强=每场1行 |
| 核心数据包 | Core.核心数据包 | 为空时场景/导演/情绪全走默认（导演=王家卫、情绪=孤独），本节点无独立场景输入 |

## 已知坑

- 15 大师 DNA 注入是子串匹配：导演名不含 15 大师表内名字（塔可夫斯基/王家卫/诺兰/小津/侯孝贤/是枝裕和/黑泽明/库布里克/伯格曼/贾樟柯/奉俊昊/李安/蔡明亮/李沧东/毕赣）时该块静默缺失，不报错。
- 120 场景库匹配按关键词重合度打分，场景描述过短（<2 字词）或与库内 120 场景零重合时匹配块为空。
- 叙事编排重排走 try/except，失败时 stderr 写"[DirectorMaster] 叙事编排降级"后保原序继续，输出不中断。

## 节点映射

- 实现文件：aggregator/script_studio.py
- 分支/函数：build() 模式分发（:1664）→ TEMPLATE_BUILDERS 无此键 → 默认 `_build_full_screenplay()`（:1413）；时长桶化 :1691-1696；`STRUCTURE_THEORY_MAP` 不含本模式（:1547，V14.2 有意移除）
- 数据来源：aggregator/pro_format.py::build_standard_screenplay_scenes（:217）+ aggregator/feature_film_engine.py::generate_feature_scenes（:2632）；注入库 director_real_scripts.ALL_DIRECTORS（15 位）、scene_library.SCENES（120 场景）
