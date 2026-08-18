# Agent Rules — 项目 AI 协作规则库

本目录存放本项目所有 AI 协作规则,**取代 `.minimax/` 品牌目录**,能力完全融入本项目。

---

## 📚 文件清单

| 文件 | 用途 | 适用范围 |
|------|------|---------|
| **general-dev.md** | 通用 SKILL — 5 错误模式 + 7 硬约束 + 10 铁律 | 任何项目 (跨项目通用) |
| **general-harness.md** | 通用 HARNESS — 开发前/中/后必做清单 | 任何项目 (跨项目通用) |
| **director-soul.md** | 项目特定 SKILL — 41 节点 L5 导演级 ComfyUI 节点集 | 本项目 (ComfyUI-PromptLibraryNode) |
| **director-soul-harness.md** | 项目特定 HARNESS — 项目特定必做项 | 本项目 (ComfyUI-PromptLibraryNode) |

---

## 📖 阅读顺序

1. **先读通用**: `general-dev.md` → `general-harness.md`
2. **再读项目特定**: `director-soul.md` → `director-soul-harness.md`
3. **开发前/中/后**: 逐项打勾 `general-harness.md` 清单
4. **修改项目代码**: 必读 `director-soul.md` (节点规范/14 段/6 反 AI 铁律)

---

## 🔄 历史迁移

| 旧路径 (`.minimax/`) | 新路径 (`docs/agent-rules/`) |
|---------------------|----------------------------|
| `.minimax/skills/general-dev/SKILL.md` | `docs/agent-rules/general-dev.md` |
| `.minimax/harness/general-dev/HARNESS.md` | `docs/agent-rules/general-harness.md` |
| `.minimax/skills/director-soul-dev/SKILL.md` | `docs/agent-rules/director-soul.md` |
| `.minimax/skills/director-soul-dev/HARNESS.md` | `docs/agent-rules/director-soul-harness.md` |

**迁移原因**: 不使用品牌类型目录,能力完全融入本项目。

---

## 🎯 核心 5 错误模式 (来自 `general-dev.md`)

1. **自我设限** — 用户说"全量"+"严格"+"极端丰富"时,不打折扣
2. **演示欺骗** — 双测试 (功能 + 内容), 不依赖自评, 跨场景真不同
3. **模板化** — 输出长度 ≥ 500 字符 + 字段填充率 ≥ 80% + 5 维具体化
4. **没全局观** — 5 维度工作分解 + 完整补全开发计划 + 风险评估
5. **子 agent 失控** — 任务完成标准 + 自检 + 不抢断 + 自动清理

---

**能力完全融入本项目, 不使用品牌类型目录.**
