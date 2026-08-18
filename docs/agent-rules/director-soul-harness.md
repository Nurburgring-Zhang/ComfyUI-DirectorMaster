# DirectorSoulNode 项目特定 HARNESS

**项目**: D:\minimax\comfyui-prompt-node-extracted\ComfyUI-PromptLibraryNode
**类型**: 41 节点 L5 顶级导演级 ComfyUI 节点集
**引用**: 通用 HARNESS 在 `docs/agent-rules/general-harness.md`

---

## 一、本文件用途

通用 HARNESS (`docs/agent-rules/general-harness.md`) 已覆盖开发前/中/后必做项。
本文件**只补充项目特定必做项**, 不重复通用内容。

---

## 二、项目特定必做项 (在通用基础上)

### 必跑测试 (项目特定)
```bash
# 通用 + 项目特定
python tests/test_full_audit.py       # 92
python tests/test_e2e_full.py          # 200
python tests/test_phase13_audit.py     # 305
python tests/_test_phase28.py          # 60
python tests/_test_phase28_p1p2.py     # 50
python tests/_test_workflows.py        # 108
python tests/_test_phase35_soul_real.py  # 14
python tests/_test_phase35_7.py        # 22
python tests/_check_5elem_all_nodes.py  # 5 要素核对
python tests/_check_anti_ai_all_nodes.py  # anti_ai 全节点
```
**期望**: 851/851 全过 + 5 要素 ≥ 30/41 OK + 4 节点 anti_ai 0 命中

### 节点规范 (ComfyUI 限制)
- 41 节点 .py 必须在根目录 (ComfyUI 加载限制)
- 11 个 phase14_*.py 同上
- `__init__.py` 必注册 41 节点
- INPUT_TYPES / RETURN_TYPES / RETURN_NAMES / FUNCTION 必填
- CATEGORY 必须 `PromptLibrary/<功能>`

### 灵魂 addon 注入
- 起点节点 (4): 纯 widget, 无 addon
- 36 个 Production 节点: 6 个 STRING addon (灵魂/审美/风格/经验/控制/节奏)

### 14 段灵魂注入
- DirectorSoulNode 输出 14 段 (EDITING/PERFORMANCE/SILENCE/...)
- 每段含: 场景锚点 / 主导情感 / 8 维导演风格 / 5-8 条具体指令 / 反 AI 例
- 跨场景 3 场景 (雨夜/驾驶舱/婚礼) 14 段全部唯一
- 跨导演 3 导演 (王家卫/诺兰/奉俊昊) 14 段全部唯一

### 5 维具体化
- 智能解析: `_extract_5d_specifics(scene, director)`
- 5 维: 时代/地点/品牌/数字/物件
- 兜底默认: 35 导演 × 5 维

### 6 个反 AI 铁律 (项目特定)
1. 不许"眼神坚定" → 具体动作 + 频率
2. 不许"陷入沉默" → 物件 + 接触声 + 秒数
3. 不许"温暖色调" → 色温 + 饱和度 + 阴影
4. 不许"钢琴配乐" → 单音 + 频率 + 次数
5. 不许"保持空间一致" → 位置 + 距离 + 轴线
6. 不许"特写表现情绪" → 固定机位 + 时长 + 节奏

### 文件结构
- README.md 留根 (GitHub 必要)
- 41 节点 + 11 phase14 留根 (ComfyUI 限制)
- 其他 .py 留根 (代码模块)
- tests/ / tools/ / workflows/ / knowledge_base/ / docs/ 子目录
- archive/_trash/ 备份 (可恢复)

---

## 三、项目特定子 agent 经验

### 失败的 5 子 agent (Phase 35.9)
- bg_67428b86 场景专家: 改了 world_building_pro.py + phase14_spatial_layout.py
- bg_f66778d3 演员专家: 改了 performance_direction_pro.py
- bg_e2e9026a 分镜专家: 改了 phase14_30s_six_act.py
- bg_9fcece90 色彩专家: 改了 style_guide_pro.py
- bg_69b6a832 理论专家: 改了 script_architecture_pro.py
- **5 子 agent 因提前停止, 9 临时文件残留, phase14_30s_six_act.py bug**
- **教训**: 任务完成标准 + 不抢断 + 自动清理

### Phase 36 子 agent 失败
- bg_a29e53f2 场景专家: 因 Token Plan 用完失败
- **教训**: 主线程备 plan, 子 agent 失败立即自己扛

---

## 四、5 要素架构核对详情

### 当前状态 (2026-08-09)
- OK (5 要素全): 30/41 节点
- PARTIAL (3-4 要素): 6 节点
- FAIL (1-2 要素): 5 节点

### 修复目标
- 6 PARTIAL 节点逐一补 data/context_summary/skill_harness
- 5 FAIL 节点 (Phase14ActingSkill/Phase14_CinematicStudio/CleanupPassPro/FormatOutputPro/ProjectArchivePro) 真正重写

### 跑核对
```bash
python tests/_check_5elem_all_nodes.py
```

---

## 五、anti_ai 演示欺骗 5 次揭穿 + 修复

| Phase | 欺骗内容 | 修复 |
|-------|----------|------|
| 30 | 硬编码周慕云/苏丽珍 | kwargs 动态化 |
| 33 | 14 段说谎 | 真实施 14 段 |
| 35 R2 | 13/14 段场景相同 | 14 段加 scene 锚点 |
| 35.8 | 根目录 .md 重复 | 删根 + 留 docs/ |
| 35.9 | anti_ai 词表当内容 | 移除"反 AI 指南"段 |

**当前状态**: 4 节点 (HookMasterPro/DialogueMasterPro/DirectorIntentPro/DirectorSoulNode) anti_ai 0 命中

---

## 六、必读文件

- **通用 SKILL**: `docs/agent-rules/general-dev.md`
- **通用 HARNESS**: `docs/agent-rules/general-harness.md`
- **项目特定 SKILL**: `docs/agent-rules/director-soul.md` (41 节点 / 14 段 / 5 维具体化 / 6 反 AI 铁律)
- **本文件**: 项目特定 HARNESS (项目补充)

---

**先读通用, 再读项目特定, 必逐项遵守.**
