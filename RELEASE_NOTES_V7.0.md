# comfyui-DirectorMaster V7.0 — 发布说明

**发布日期**: 2026/08/11  
**版本**: V7.0 (双轨 LLM 原生)  
**打包**: directormaster_v7.0.tar.gz (3.0M)

---

## 一、项目概述

ComfyUI 自定义节点包, 把 43 个 legacy 影视导演节点聚合为 **9 个 DirectorMaster 节点**, 通过模式下拉路由 + 核心数据包星型分发, 实现从导演总控到视频生成 API 的完整工作流。

**核心能力**: 有 LLM → 世界顶级导演级输出(533导演档案 few-shot + 7域规则 + Hell Grind 约束原生生成); 无 LLM → 高质量确定性模板(零降级).

---

## 二、9 个节点

| # | 节点 | 角色 | 输入 | 输出 |
|---|------|------|------|------|
| ① | DirectorMasterCore | 起点·总控 | 15 (8必填+7选填) | 11 (含核心数据包) |
| ② | DirectorMasterScript | 剧本链(7合1) | 10 | 3 |
| ③ | DirectorMasterVibe | 创意氛围(13合1+漫剧) | 15 | 3 |
| ④ | DirectorMasterArt | 美术空间(3合1) | 9 | 6 |
| ⑤ | DirectorMasterSound | 声音音乐(4合1) | 15 | 3 |
| ⑥ | DirectorMasterCinematic | 画面执行(4合1+漫剧) | 9 | 10 |
| ⑦ | DirectorMasterFinal | 终极汇总·终点 | 8 | 5 |
| ⑧ | DirectorMasterRouter | 6视频API路由 | 15 | 12 |
| ⑨ | DirectorMasterArchive | 归档·终态(6合1) | 5 | 6 |

---

## 三、架构

```
Core(11输出含核心数据包) ──星型分发──┬→ Vibe ──┐
   (灵魂/审美/风格/意图/AI配置打包)     ├→ Art ──┤
                                        ├→ Sound─┤
                                        ├→ Cine ─┤→ Final(汇总) → Router → Archive
                                        └→ Script┘
```

- **Core 填一次 AI 配置** → 打包进核心数据包 → 所有下游节点自动继承 AI 能力
- 下游保留 ai_api_url/key/model 输入作 override
- 连了 Core → 自动获取场景/导演/反AI/灵魂, 无需重复输入

---

## 四、安装

1. 解压到 ComfyUI `custom_nodes/` 目录:
```bash
cd ComfyUI/custom_nodes
tar -xzf directormaster_v7.0.tar.gz
mv project comfyui-DirectorMaster
```
2. 重启 ComfyUI
3. 节点出现在 `PromptLibrary/聚合/` 分类下

**依赖**: 无强制依赖(纯 Python). 可选: 接 LLM 需 OpenAI 兼容 API (Ollama/lm_studio/openai 均可).

---

## 五、使用

### 无 AI (纯模板, 高质量输出)
直接搭工作流, 不填 ai_api_url, 全链路输出确定性模板.

### 有 AI (世界顶级导演级)
在 Core 节点填:
- `ai_api_url`: OpenAI 兼容地址 (如 http://localhost:11434/v1 for Ollama)
- `ai_api_key`: API key (本地可空)
- `ai_model_name`: 模型名 (gpt-4o / qwen-max / deepseek-chat / llama3.1)

所有下游节点自动获得 AI 能力, 输出达世界顶级导演级.

---

## 六、工作流示例

- `workflows/MEGA_ALL_NODES_9NODE_V6.1.json` — 9节点全链路(含核心数据包星型分发)
- `workflows/MEGA_ALL_NODES_8NODE.json` — 8节点版本
- `workflows/WORKFLOW_MINIMAL_5NODE.json` — 5节点极简

---

## 七、验证

- 9 节点 ComfyUI spec: ✅ (INPUT_TYPES @classmethod / RETURN_TYPES==RETURN_NAMES / OUTPUT_NODE / IS_CHANGED / forceInput)
- 双轨全链路: ✅ (LLM失败→模板零降级 / 无AI→模板 / AI打包继承)
- 31+2 模式矩阵 0 errors (含漫剧)
- `tests/test_v6_aggregators.py`: ✅ 120/120 PASS
- 533导演模糊匹配 + 12灵魂预设 + 8参数预设: ✅

---

## 八、ComfyUI 合规性(联网验证 2025-2026 标准)

| 规则 | 合规 |
|------|------|
| INPUT_TYPES @classmethod | ✅ |
| RETURN_TYPES == RETURN_NAMES 长度 | ✅ |
| optional 用 **kwargs 捕获 | ✅ |
| OUTPUT_NODE=True (终端节点) | ✅ Final/Archive/Router |
| IS_CHANGED 缓存控制 | ✅ 9节点 |
| forceInput (optional 默认可连线) | ✅ 核心数据包+Final上游 |
| JSON-in-STRING 单线传递 | ✅ 社区通用范式 |

---

## 九、文件结构

```
project/
├── __init__.py                      # 9节点注册
├── aggregator/
│   ├── _common.py                    # 公共工具 (parse_core_pack/resolve_ai_config/ai_enhance→generate_native)
│   ├── _presets.py                  # 533导演下拉+12灵魂预设+8参数预设
│   ├── llm_engine.py                # V7.0 LLM原生引擎 (generate_native+DOMAIN_RULES)
│   ├── director_master.py           # ① Core
│   ├── script_studio.py             # ② Script
│   ├── vibe_studio.py               # ③ Vibe
│   ├── art_master.py                # ④ Art
│   ├── sound_master.py              # ⑤ Sound
│   ├── cinematic_studio.py          # ⑥ Cinematic
│   ├── final_master.py              # ⑦ Final (终点)
│   ├── archive_master.py            # ⑨ Archive
│   └── ...
├── universal_director_prompt_node.py # ⑧ Router
├── comic_drama_pro.py               # 漫剧节点 (V6.3新增)
├── director_data_unified.py         # 533导演数据库
├── pln_llm.py                       # LLM调用封装
├── *.py                             # 43个legacy节点(内部库)
├── workflows/                       # 示例工作流JSON
├── tests/                           # 测试 (权威: test_v6_aggregators.py)
└── WORKFLOW_DOC_V6.1.md             # 全链路文档(V6.2/V7.0已更新)
```

---

## 十、版本历史

- V6.0: 43→8 聚合重组
- V6.1: Core核心数据包星型分发 + Final终极汇总节点
- V6.2: Core 3输入下拉化(533导演/12灵魂/8参数预设) + AI能力打包继承
- V6.3: ComfyUI合规(OUTPUT_NODE/IS_CHANGED/forceInput) + 漫剧 + 导演few-shot注入
- **V7.0: LLM原生双轨引擎 (generate_native取代后处理) ← 当前版本**
