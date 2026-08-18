# 全功能审核 + 端到端落地测试计划

> **目标**：每实施一步都有"自检 → 互审 → 落地"三道关卡，确保 0 破现有 + 100% 真实可用。

---

## 1. 测试分层

| 层 | 文件 | 触发时机 | 期望时长 |
|---|---|---|---|
| L0 静态语法 | `py_compile` 全部 .py | 每次代码改动 | <5s |
| L1 单元自检 | `test_full_audit.py` | 每次代码改动 | <10s |
| L2 决策层注入 | `test_decision_layer.py` | Phase 3 完成 | <5s |
| L3 E2E 落地 | `test_e2e_full.py` | Phase 6 完成 | <60s |
| L4 双 AI 互审 | `audit_report.md` | 所有阶段完成 | 手动 |

---

## 2. L0 静态语法（每次改动必跑）

```bash
cd D:\minimax\comfyui-prompt-node-extracted\ComfyUI-PromptLibraryNode
python -m py_compile __init__.py director_engine.py director_pro.py \
    engine_story_arc.py pln_*.py modes_*.py knowledge_base/*.py \
    format_templates.py story_sense_data.py 2>&1
```

期望：无任何输出

---

## 3. L1 单元自检（121 项）

```bash
python test_full_audit.py
```

期望：121/121 通过

**关键检查点**（不要破的）：
- ✅ NODE_CLASS_MAPPINGS 仍有 2 个节点
- ✅ NODE_DISPLAY_NAME_MAPPINGS 名称不破
- ✅ WEB_DIRECTORY="web"
- ✅ 63 导演下拉框 ≥ 70 项
- ✅ 细分标签 ≥ 67 项
- ✅ INPUT_TYPES 24 模式齐全
- ✅ RETURN_TYPES 5 端口 / 2 端口齐全
- ✅ OUTPUT_NODE=True

---

## 4. L2 决策层注入测试（新增）

**目标**：验证 4 个决策层 dict 真实注入 prompt。

**测试用例**（10 项）：
```python
# test_decision_layer.py

def test_director_decision_injected():
    """选导演 希区柯克, system_prompt 包含 trigger/failure_modes 关键词"""
    eng = DirectorPromptBuilder(mode="电影分镜", director_keys=["hitchcock"], ...)
    sys_p = eng.build_system_prompt(0, None, "")
    assert "jump scare" in sys_p.lower() or "悬疑" in sys_p or "麦格芬" in sys_p
    assert "失败模式" in sys_p or "failure" in sys_p.lower() or "避免" in sys_p

def test_narrative_decision_injected():
    """选叙事结构 英雄之旅, prompt 包含英雄之旅相关关键词"""
    eng = DirectorPromptBuilder(mode="电影分镜", narrative_structure="英雄之旅", ...)
    sys_p = eng.build_system_prompt(0, None, "")
    assert "英雄" in sys_p or "启程" in sys_p or "hero" in sys_p.lower()

def test_tag_taxonomy_injected():
    """选细分类型 科幻/赛博朋克, prompt 体现赛博朋克特征"""
    eng = DirectorPromptBuilder(mode="电影分镜", subdivision="电影/赛博朋克", ...)
    sys_p = eng.build_system_prompt(0, None, "")
    assert "赛博" in sys_p or "cyberpunk" in sys_p.lower() or "霓虹" in sys_p

def test_director_pipeline_injected():
    """选短剧类型 隐藏身份, prompt 包含短剧相关指导"""
    eng = DirectorPromptBuilder(mode="短剧模式", short_drama_type="隐藏身份", ...)
    sys_p = eng.build_system_prompt(0, None, "")
    assert "短剧" in sys_p or "钩子" in sys_p or "前3秒" in sys_p

def test_all_decision_layers_combined():
    """4 个决策层同时启用, prompt 长度 > 2000 字符且包含全部关键词"""
    eng = DirectorPromptBuilder(
        mode="电影分镜",
        director_keys=["hitchcock"],
        narrative_structure="悬疑揭秘",
        subdivision="电影/心理惊悚",
        short_drama_type="",
    )
    sys_p = eng.build_system_prompt(0, None, "")
    assert len(sys_p) > 2000
    assert "希区柯克" in sys_p or "hitchcock" in sys_p.lower()
    assert "失败" in sys_p or "避免" in sys_p
```

---

## 5. L3 端到端测试（200+ 项）

**目标**：覆盖所有用户场景的快乐路径 + 边界路径。

**测试矩阵**：

| 类别 | 场景 | 用例数 |
|---|---|---|
| 节点注册 | 2 节点 + 23 模式 | 25 |
| 提示词库读取 | 8 读取模式 × 5 循环模式 × 3 文件类型 | 120 |
| 主体过滤 / 关键词筛选 / 标签筛选 | 4 类规则 × 5 模式 | 20 |
| AI 生成 / 润色 / 翻译 | 3 类 × 5 提示词 | 15 |
| 故事板 9 模式 × 3 风格 × 3 景别 | | 81 → 采样 30 |
| 绘本 / 短剧 / 儿童 6 模式 | | 6 |
| 设计 8 模式 × 4 角度/布光/背景 | | 32 → 采样 16 |
| 63 导演 × 故事板 5 模式 | | 315 → 采样 50 |
| 决策层注入 4 层 × 5 模式 | | 20 |
| output_focus 5 维 × 3 模式 | | 15 |
| 边界：空 API | 24 模式全部空 API 跑 | 24 |
| 边界：空文件夹 / 无效路径 / 编码 | | 12 |
| 性能：60 镜头批次输出 | | 5 |

**总用例：~350，期望 <60s 跑完。**

---

## 6. L4 双 AI 互审

**A 角色（开发）**：负责写代码 + 自测
**B 角色（Verifier agent）**：负责独立审查

**B 的检查清单**：
1. ✅ 代码改动是否破现有 121 测试
2. ✅ 知识库数据是否专家级（不是 AI 臆造）
3. ✅ 引擎注入路径是否真接通（不能只是引用变量）
4. ✅ 边界条件是否覆盖
5. ✅ 性能是否合理（单镜头 < 2s，60 镜头 < 60s）
6. ✅ 文档是否完整可用
7. ✅ 是否符合 ComfyUI 节点开发规范

**B 抽查 5 个导演 + 5 个模式 + 5 个边界场景**。

---

## 7. 测试执行命令

```powershell
# L0 静态
cd "D:\minimax\comfyui-prompt-node-extracted\ComfyUI-PromptLibraryNode"
python -m py_compile *.py knowledge_base\*.py

# L1 自检
python test_full_audit.py

# L2 决策层（新增）
python test_decision_layer.py

# L3 E2E（新增）
python test_e2e_full.py

# L4 双 AI 互审（手动）
# 启动 verifier agent 给一段 prompt 让它审查
```

---

## 8. 验收门槛

### 必须 100% 通过
- L0 静态无错误
- L1 121/121 不破
- L2 决策层注入 5/5
- L3 E2E ≥ 95%（允许 5% 边界场景降级）
- L4 双 AI 互审无重大问题

### 失败处理
- 任何 L0 失败 → 立即修复，不进入下一阶段
- L1 失败 → 回滚改动，重新设计
- L2 失败 → 检查注入逻辑
- L3 失败 → 标记为"已知边界"或修复
- L4 重大问题 → 重新设计该模块

---

## 9. 自动化建议（未来）

- 加 GitHub Actions 每次提交跑 L0+L1
- 加 pre-commit 钩子跑 py_compile
- 加 ruff/black 格式检查
- 加 mypy 类型检查
- 加 Codecov 覆盖率检查

---

## 10. 时间预算

| 阶段 | 实施 | 测试 | 互审 | 总计 |
|---|---|---|---|---|
| Phase 0 诊断 | 5min | 2min | - | 7min |
| Phase 1 63导演 | 30min(并行) | 5min | 5min | 40min |
| Phase 2 45作品 | 20min | 3min | 3min | 26min |
| Phase 3 决策层 | 15min | 5min | 3min | 23min |
| Phase 4 output_focus | 10min | 3min | 3min | 16min |
| Phase 5 dimension | 10min | 3min | 3min | 16min |
| Phase 6 E2E | 20min | 30min(执行) | 5min | 55min |
| Phase 7 文档 | 15min | - | 10min | 25min |

**总：~3.5h 达到 95% 世界顶级。**
