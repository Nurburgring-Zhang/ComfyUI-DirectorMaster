---
mode_id: archive-save-production-manual
node: DirectorMasterArchive
name: 保存制作手册
one_liner: 制作手册按【】标题分节写盘, 支持多格式逐份真实转换
applicable: [手册归档, 制片交付, 版本基线]
intensity: low
style_tags: [写盘归档, 分节结构, 版本提交]
aliases: [归档手册]
---

## 意图

把 Final.完整制作手册 归档为可分节检索的文档时选它。与 保存剧本 的差别: 结构化走 split_sections 按 【…】 标题切节, 不做场次/镜头解析 — 适合 42 环节流程类多节文本。

## 核心手法

1. 资产装配: assets=[("制作手册", 制作手册 or 输入文本, "txt")]。
2. 分节解析: format_export.split_sections() 逐行匹配 【…】 标题, 标题后正文聚为节对象; JSON → sections 数组, MD → ## 节标题+正文, HTML → h2+pre.script 块。
3. 默认双格式: TXT 原文 + JSON 分节副本; 手册无 【】 标题时整本成单节 (title 空串, 仅 body 非空才保留)。
4. 自动版本提交: 手册常是最大体量资产, 版本评分的体量分 (字符/40000) 主要由它拉动。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 制作手册 | Final.完整制作手册 (forceInput) | 空 → 回退 输入文本; 全空不写盘 |
| 保存格式 | TXT,JSON | 加 MD/HTML 时按节渲染; HTML 内嵌暗色 CSS 并全量实体转义 |
| 输出目录 | 空 | 三级回退 (手动 → ComfyUI output → 插件 output); 手动路径支持 ~ 与环境变量展开 |
| 版本名称 | 空 | 留空自动编号 vN (N=当前 order 长度+1); 与 版本备注/版本标签 同次提交生效 |

## 已知坑

- 空标题节 (【】内无字) 会被 split_sections 过滤; 正文空只有标题的节保留 — 分节完整性以"节标题存在"为准。
- 手册里的分镜表/剧本片段不会被二次解析成对应结构 — 混合内容统一按节处理, 想要逐镜对象需另走 保存分镜。
- 文件名时间戳精度为秒: 同一秒内重复保存同项目同资产类型会互相覆盖 (fname 含 %H%M%S)。

## 节点映射

- 实现文件：aggregator/archive_master.py
- 分支/函数：build() elif mode == "保存制作手册" + _save(); 分节转换 aggregator/format_export.py :: split_sections()/to_md() else 分支/to_html() else 分支
- 数据来源：仅上游手册文本; 无内置数据库。
