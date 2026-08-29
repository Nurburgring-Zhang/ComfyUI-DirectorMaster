---
mode_id: archive-save-storyboard
node: DirectorMasterArchive
name: 保存分镜
one_liner: 分镜表写盘并按 16 列固定列宽真实解析为逐镜对象
applicable: [分镜归档, AIGC 投喂基线, 版本基线]
intensity: low
style_tags: [写盘归档, 表格解析, 版本提交]
aliases: [归档分镜]
---

## 意图

把 Cinematic/Summary 的分镜脚本落盘并得到结构化逐镜 JSON 时选它。与 保存剧本 的差别: JSON 走 parse_shot_table 表格解析器, 输出按镜号索引的对象数组, 可直接喂下游程序消费。

## 核心手法

1. 资产装配: assets=[("分镜", 分镜脚本 or 输入文本, "txt")], 兜底逻辑同保存剧本。
2. 分镜表解析: format_export.parse_shot_table() 按 V14.2 短行+子行格式解析 — 表头行前 5 字符须为数字镜号, 固定列宽 [5,6,8,7,8,8,8] 切 镜号/阶段/类型阶段/景别/运镜/焦段/时长, 子行收 焦点/设计 与 声音|色彩|光影|材质|氛围|情绪|转场 七键 (兼容全角冒号, V16.1.1 L-1 修复)。
3. 格式落点: JSON → meta+shots+镜头数; MD → 16 列 Markdown 表格 (设计 转引用行); HTML → 同列真表格, 单元格内竖线替换为斜杠。
4. 自动版本提交与评分同保存剧本 (完整度 0.2)。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 分镜脚本 | Final.分镜脚本 (forceInput) | 非 format_shot_table 列宽格式的自由文本 → shots=[], JSON 只有 meta 无镜头对象, 不报错 |
| 保存格式 | TXT,JSON | 只选 TXT 时不解析原文直存; 加 MD/HTML 时逐镜转表格 |
| 输出目录 | 空 | 空 → ComfyUI output → 插件 output 三级回退; 手动路径展开失败时报"手动目录不可用({e}), 已回退默认" |
| 输入文本 | 空 | 分镜脚本为空时的兜底资产源 |

## 已知坑

- 列宽解析是位置敏感的: 分镜行任一列超宽 (如景别写"大远景特写"挤占运镜列) 会串列, 解析结果静默错位。
- 子行键值按固定七键正则匹配, 自定义子键 (如"音效:") 不入对象, 丢字段无提示。
- 设计 行是独立引用行 (MD/HTML 单独渲染), 只认以"设计:"开头的 4 空格缩进子行。

## 节点映射

- 实现文件：aggregator/archive_master.py
- 分支/函数：build() elif mode == "保存分镜" + _save(); 格式转换 aggregator/format_export.py :: parse_shot_table()/_SHOT_ROW_WIDTHS/_SHOT_SUBKEYS/to_md() 分镜分支/to_html() 分镜分支
- 数据来源：仅上游分镜文本; 列宽常量内置 format_export.py。
