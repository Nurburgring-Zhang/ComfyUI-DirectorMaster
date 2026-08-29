---
mode_id: vibe-poster-design
node: DirectorMasterVibe
name: 海报设计
one_liner: 生成海报视觉层级/构图/标题字/色彩方案的设计系统指令
applicable: [电影海报, 活动宣传, 社媒封面]
intensity: medium
style_tags: [视觉层级, 主视觉, 标题字体]
aliases: [海报]
---

## 意图

为项目出一张"3 秒读懂"的海报设计指令时选它：按视觉层级（主视觉→主标题→副标题→正文→logo）组织构图/标题/色彩要求。与"电商套图"的本质差别：单张层级表达，不做多图决策链。

## 核心手法

1. modes_design._build_poster_prompt：视觉层级五层逐级缩小，要求"一眼读懂"。
2. 构图给三分法/居中/对角线三选 + 留白呼吸 + 视觉重心明确。
3. 标题规则：大字体粗体高对比、6-12 字以内、一句记住。
4. 色彩规则：主色1+辅色1+点缀色1，情绪与品牌一致；适配器传 style=商业摄影、color_tone=_视觉调性（空则"高对比"）、count=4、主视觉/场景槽取场景解析结果（空则"主视觉待定"）。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 核心数据包 | 含 _视觉调性 的 JSON | 空包时色彩基调落"高对比" |
| 场景描述来源 | 核心包 _场景描述 | 空场景时主题=前80字截断或"未命名产品"，主视觉行显示"主视觉待定" |
| 数量 count | 4（适配器硬编码） | 非用户参数，改不了张数 |
| 启用反AI规则 | True | False 时输出保留套话 |

## 已知坑

与全部 8 个设计模式共用适配器：modes_design 导入失败→stderr 降级提示+占位文本；主题取场景前 80 字截断，长标题项目会被切尾。文案槽（character_desc/env_desc）只装场景解析的首个人物/物件，营销文案本身不在输入里。

## 节点映射

- 实现文件：aggregator/vibe_studio.py
- 分支/函数：TEMPLATES["海报设计"] → _build_design_adapter("海报设计") → modes_design.py :: _build_poster_prompt()（modes_design.py:48）
- 数据来源：modes_design 内置海报设计原则文案
