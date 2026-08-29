---
mode_id: vibe-ppt-design
node: DirectorMasterVibe
name: PPT设计
one_liner: 生成一页一观点/视觉为主/结论先行/全篇一致的 PPT 设计指令
applicable: [路演汇报, 提案评审, 教学课件]
intensity: medium
style_tags: [一页一观点, 结论先行, 版式一致]
aliases: [演示文稿设计]
---

## 意图

给汇报/路演出一套版式规范时选它：按"一页一观点+视觉>文字+结论先行标题"输出逐页设计要求。与"逻辑关系图设计"的本质差别：组织的是成套页面版式，不是单张关系拓扑。

## 核心手法

1. modes_design._build_ppt_prompt：一页一观点，信息层级清晰不堆砌。
2. 视觉>文字：图表/图标/图片优先于大段文字，数据必须图表化（柱/饼/线）不用表格堆数字。
3. 留白规则：主体占画面 40-60%；一致性规则：字体/配色/版式/图标全篇统一。
4. 标题规则：每页大标题（结论先行）+小标题（论点）；适配器传 style=扁平矢量（非摄影类）、count=4、内容槽 character_desc=场景解析首个人物或物件（空则"内容待定"）。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 核心数据包 | 含 _视觉调性 的 JSON | 空包时色彩基调落"高对比" |
| 内容主体 | 场景解析首个人物/物件 | 空场景时内容行显示"内容待定"，页位无实料 |
| 数量 count | 4（适配器硬编码） | 页数恒 4，非用户参数 |
| 启用反AI规则 | True | False 时输出保留套话 |

## 已知坑

真实讲稿内容不在此节点输入——内容槽只装场景解析出的一个词，逐页观点要靠场景文本携带或 AI 轨扩写；页数恒 4，长汇报需分次生成。

## 节点映射

- 实现文件：aggregator/vibe_studio.py
- 分支/函数：TEMPLATES["PPT设计"] → _build_design_adapter("PPT设计") → modes_design.py :: _build_ppt_prompt()（modes_design.py:90）
- 数据来源：modes_design 内置 PPT 设计原则文案
