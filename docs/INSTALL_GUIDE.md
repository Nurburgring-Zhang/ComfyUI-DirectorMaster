# ComfyUI-PromptLibraryNode 安装与故障排查指南

> **节点找不到？模式没出来？** 看这里。

---

## ✅ 3 种安装方式（选一种即可）

### 方式 1：ComfyUI Manager 安装（最推荐）

1. 启动 ComfyUI
2. 打开节点搜索框旁边的 **Manager** 按钮
3. 搜索 `PromptLibraryNode`
4. 找到 **"PromptLibraryNode Pro V20.5"** 或 **"导演分镜批次输出 V2.0"** → 点 Install
5. **重启 ComfyUI**（必须！）

### 方式 2：Git 克隆（推荐给中国大陆用户）

```bash
# 进入 custom_nodes 目录
cd ComfyUI/custom_nodes/

# 中国大陆用户用镜像加速
git clone https://mirror.ghproxy.com/https://github.com/Nurburgring-Zhang/ComfyUI-PromptLibraryNode.git

# 海外用户直接
git clone https://github.com/Nurbururgring-Zhang/ComfyUI-PromptLibraryNode.git

# 重启 ComfyUI
```

### 方式 3：手动下载 ZIP（最简单的方案）

1. 打开 https://github.com/Nurburgring-Zhang/ComfyUI-PromptLibraryNode
2. 点 **Code → Download ZIP**
3. **解压 ZIP**
4. **关键：确保目录结构是下面这样：**

```
ComfyUI/custom_nodes/
   ComfyUI-PromptLibraryNode/        ← 这个目录名随意,但里面要有 __init__.py
       __init__.py                  ← 必备
       pyproject.toml
       pln_utils.py
       director_engine.py
       knowledge_base/
       web/
       ...
```

5. 重启 ComfyUI

---

## ❌ 5 大常见错误（90% 用户都踩过）

### 错误 1：把 ZIP 直接放在 custom_nodes 目录（不解压）
```
ComfyUI/custom_nodes/
   ComfyUI-PromptLibraryNode-V10.1-HotShortform.zip   ← 错误!不识别
```
**修复**：解压 ZIP，把里面的 `ComfyUI-PromptLibraryNode` 目录放到 `custom_nodes/` 下。

### 错误 2：目录多套了一层
```
ComfyUI/custom_nodes/
   ComfyUI-PromptLibraryNode-V10.1-HotShortform/        ← 错误
       ComfyUI-PromptLibraryNode/                       ← 正确位置应该在这里
           __init__.py
```
**修复**：把内层 `ComfyUI-PromptLibraryNode` 挪到 `custom_nodes/` 直接子级。

### 错误 3：节点在菜单里找不到
节点在 **"提示词工具"** 分类下（不是英文分类）：
- 在节点搜索框输入 `提示词` 或 `PromptLibrary` 或 `Director`
- 或者展开左侧菜单 → **提示词工具** → **提示词库节点 Pro V20.5**

### 错误 4：节点能加载但模式不工作
- **检查 API 地址**：`API地址` 必须是 OpenAI 兼容的 chat/completions 端点
- 模式选择 ≠ `关闭` 时，必须填 API
- 模式选择 = `关闭` 时，不需要 API，可以走传统提示词库

### 错误 5：装了但 ComfyUI 控制台报 IMPORT FAILED
看 ComfyUI 启动日志最后 50 行，搜索 `PromptLibrary` 或 `ImportError`，找具体是哪个模块出问题。然后：

```bash
# 在 ComfyUI 环境下手动安装依赖
cd ComfyUI/custom_nodes/ComfyUI-PromptLibraryNode
python -m pip install torch Pillow numpy requests
```

---

## 🔧 自检工具：一键诊断

如果还有问题，跑自检：

```bash
cd ComfyUI/custom_nodes/ComfyUI-PromptLibraryNode
python doctor.py
```

会检查 6 大类：
1. ✅ 安装路径
2. ✅ Python 环境
3. ✅ 模块导入
4. ✅ 节点注册
5. ✅ 知识库完整性
6. ✅ API 可达性（可选）

输出示例：
```
== 1. 安装路径检查 ==
  ✓ __init__.py 存在 (49455 字节)
  ✗ 不在 custom_nodes 目录树中!  ← 致命问题
== 2. Python 环境检查 ==
  ✓ Python 3.11.15 (>=3.9)
== 3. 节点模块导入检查 ==
  ✓ 故事感总纲库 (story_sense_data)
  ...
== 诊断总结 ==
  ✗ 1 个致命问题:
     - 不在 custom_nodes 目录树中!  ← 跟着提示修就行
```

---

## 📍 节点应该出现在哪里

启动 ComfyUI 后，按 `Ctrl+Space` 或双击空白处打开节点搜索框：

1. 搜 `提示词库` 或 `PromptLibrary` → 找到 **提示词库节点 Pro V20.5**
2. 搜 `导演分镜` 或 `Director` → 找到 **导演分镜批次输出 V2.0 (世界级导演引擎)**

或在左侧分类菜单找：**提示词工具** → 这两个节点都在那。

---

## 🚀 第一次使用

1. 把 **提示词库节点 Pro V20.5** 拖到画布
2. 填 `主题`（必填）
3. `模式选择` 选一个（默认"关闭"=传统模式）
4. 如果想用 AI：`开启AI生成=True`，填 `API地址` `API密钥` `AI模型名`
5. 接到 **文本显示** 节点，看输出

第一次建议从 **模式选择=电影分镜 + 主题=黑客帝国 + 风格=赛博风** 开始，体验镜头连续性和故事弧。

---

## 📋 系统要求

| 项目 | 最低 | 推荐 |
|---|---|---|
| Python | 3.9+ | 3.11 |
| ComfyUI | 最新版 | 0.3.x+ |
| 显存 | 不需要 GPU（除非你要生成图） | - |
| 网络 | 离线可用 | 联网可补全数据 |
| 磁盘 | 50MB | 100MB |

---

## 🐛 报告问题

如果还是不行：
1. 跑 `python doctor.py` 把输出保存
2. 看 ComfyUI 启动日志最后 30 行
3. 在 GitHub Issues 提交：https://github.com/Nurburgring-Zhang/ComfyUI-PromptLibraryNode/issues
4. 附上：Python 版本、ComfyUI 版本、doctor 输出、ComfyUI 启动日志

---

## 💡 高级：自定义安装位置

如果你不想用默认 `custom_nodes/`，可以这样：

```python
# ComfyUI 启动时指定
python main.py --extra-model-paths-config /path/to/config.yaml
```

或者把节点软链过去：
```bash
ln -s /your/path/ComfyUI-PromptLibraryNode ComfyUI/custom_nodes/
```

---

**安装成功？接下来看 [USAGE.md] 学习怎么用。**
