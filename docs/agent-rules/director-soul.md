---
name: director-soul-dev
description: DirectorSoulNode 项目特定 sub-skill — 41 节点 L5 顶级导演级 ComfyUI 节点集, DirectorSoulNode 14 段灵魂总控, 35 导演 + 100 场景联网整合. 引用通用 general-dev SKILL + 加项目特定规则.
---

# DirectorSoulNode 项目特定 sub-skill

**项目**: D:\minimax\comfyui-prompt-node-extracted\ComfyUI-PromptLibraryNode
**类型**: 41 节点 L5 顶级导演级 ComfyUI 节点集
**引用**: 通用规则见 `docs/agent-rules/general-dev.md`
**HARNESS**: `docs/agent-rules/general-harness.md`

---

## 一、项目状态 (2026-08-09)

- 41 节点: 起点 4 + 剧本 3 + 短剧 4 + 导演附件 4 + 生产 14 + Phase14 7 + Phase17-28 5
- DirectorSoulNode: 14 下游 addon 段 (EDITING/PERFORMANCE/SILENCE/...)
- 35 导演 + 100 场景 + 30 名言 + 20 数据 (联网整合 79KB)
- 5 维具体化智能解析 (时代/地点/品牌/数字/物件)
- 测试 851/851 全过
- 演示欺骗 5 次揭穿 + 修复 (Phase 30/33/R2/35.8/35.9)

---

## 二、项目特定约束 (在通用规则之上)

### 约束 8: 节点必须 ComfyUI 规范
- 41 节点 .py 必须在根目录 (ComfyUI 加载限制, 不能移到子目录)
- 11 个 phase14_*.py 同上
- INPUT_TYPES / RETURN_TYPES / RETURN_NAMES / FUNCTION 必填
- CATEGORY 必须 PromptLibrary/<功能>

### 约束 9: 灵魂 addon 注入
- _addon_injector.py 注入 6 个 STRING input slot (灵魂/审美/风格/经验/控制/节奏)
- 起点节点 (4 个) 纯 widget, 无 addon
- 36 个 Production 节点有 addon

### 约束 10: 节点输出格式
- 输出 ≥ 500 字符
- 字段填充率 ≥ 80%
- 5 维具体化 ≥ 3 维
- 不能含 "题材: " "片长: " "集数: " 等空字段

---

## 三、必跑测试 (项目特定)

```bash
# 功能测试 851
python tests/test_full_audit.py       # 92
python tests/test_e2e_full.py          # 200
python tests/test_phase13_audit.py     # 305
python tests/_test_phase28.py          # 60
python tests/_test_phase28_p1p2.py     # 50
python tests/_test_workflows.py        # 108
python tests/_test_phase35_soul_real.py  # 14
python tests/_test_phase35_7.py        # 22

# 5 要素 + anti_ai
python tests/_check_5elem_all_nodes.py
python tests/_check_anti_ai_all_nodes.py
```

---

## 四、关键 5 要素架构

每个 Production 节点必须 5 要素完整:
- **数据**: `knowledge_base/` 23 文件 + `web_research_director_db.py` 79KB
- **上下文缩略**: `_extract_5d_specifics` 智能解析
- **skill/harness**: DirectorSoulNode 14 addon 段注入
- **经验矩阵**: 39 导演 8 维风格 + 12 套理论 + 9 维光照
- **AI 深度处理**: kwargs 动态生成, 跨场景差异化

---

## 五、灵魂 addon 14 段 (DirectorSoulNode 输出)

```
===EDITING_ADDON=== ===PERFORMANCE_ADDON=== ===SILENCE_ADDON=== ===COLOR_ADDON===
===WORLDBUILDING_ADDON=== ===THEME_ADDON=== ===ART_ADDON=== ===SPATIAL_ADDON===
===SOUND_ADDON=== ===MUSIC_ADDON=== ===INTENT_ADDON=== ===STORYBOARD_ADDON===
===CHARACTER_ADDON=== ===QA_ADDON===
```

每段含:
- 场景锚点 (scene[:80])
- 主导情感 (emo_name)
- 8 维导演风格 (d8d)
- 具体指令 (5-8 条)
- 反 AI 例

---

## 六、6 个反 AI 铁律 (项目特定)

1. 不许"眼神坚定" → 具体"拇指杯沿摩挲 0.6Hz"
2. 不许"陷入沉默" → 具体"杯底触桌 0.3 秒 + 8 秒无对白"
3. 不许"温暖色调" → "色温 4200K, 饱和度 -15, 蓝绿阴影, 琥珀高光"
4. 不许"钢琴配乐烘托悲伤" → "单音 C4→E4→G4, 出现 3 次"
5. 不许"保持空间一致" → "男主窗边 (西侧), 女主门口 (东侧), 距离 3.5 米"
6. 不许"特写表现情绪" → "固定机位 14s, 男主背影, 雨刷 1Hz"

---

## 七、目录结构 (项目特定)

```
ComfyUI-PromptLibraryNode/
├── README.md  # GitHub 必要
├── __init__.py  # 41 节点注册
├── _addon_injector.py  # 6 addon 注入器
├── 41 节点 _pro.py  # 必须根
├── 11 个 phase14_*.py  # 必须根
├── 5 个 director_*.py + 7 个辅助模块 + 5 个 modes_*.py + 3 个 pln_*.py
├── tests/  # 30 个测试
├── tools/  # 32 个工具 (_audit/_check/_gen/_push/_self_question 等)
├── workflows/  # 9 个 + 5 个 presets
├── knowledge_base/  # 23 + web_research_director_db
├── docs/
│   ├── agent-rules/  # 通用 + 项目特定 SKILL/HARNESS
│   │   ├── general-dev.md       # 通用 5 错误模式 + 7 硬约束
│   │   ├── general-harness.md   # 通用开发前/中/后清单
│   │   ├── director-soul.md     # 项目特定 SKILL
│   │   └── director-soul-harness.md  # 项目特定 HARNESS
│   ├── phase-reports/  # PHASE_*.md 阶段报告
│   └── *.md  # 其他文档
└── archive/_trash/  # 129 临时文件 (备份)
```

---

## 八、与通用规则的关系

- **通用规则**: `docs/agent-rules/general-dev.md` (5 错误模式 + 7 硬约束)
- **通用检查**: `docs/agent-rules/general-harness.md` (开发前/中/后)
- **项目特定**: 本文件 (节点规范/14 段/6 反 AI 铁律/必跑测试)
- **项目特定 HARNESS**: `docs/agent-rules/director-soul-harness.md`

**先读通用, 再读项目特定, 必逐项遵守.**

---

**DirectorSoulNode 项目必遵守 通用 + 项目特定 全部规则, 不接受"差不多"借口.**
