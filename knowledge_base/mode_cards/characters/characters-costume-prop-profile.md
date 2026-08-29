---
mode_id: characters-costume-prop-profile
node: DirectorMasterCharacters
name: 服化道设定
one_liner: 生成服化道卡：道具情感功能+材质年代指令，继承关键道具与场景物件
applicable: [竖屏微短剧, 短视频, 长片]
intensity: medium
style_tags: [服化道卡, 道具母版, 叙事物件]
aliases: []
---

## 意图

立可跨镜头锁定的服化道锚点时选它，服化道类 14 模式的基座。与角色/环境类的本质差别：输出落「服化道圣经」路（角色圣经/环境圣经为空串）；清单可从核心数据包 `_关键道具` 与场景物件自动合并继承。

## 核心手法

- 委托后走 `else:` 分支（不在 _CHARACTER_MODES/_ENV_MODES 的兜底路径），产出「服化道卡」。
- 服化道描述清空时自动合并继承：_关键道具 打头 + 场景解析物件前 4 个（去重）顿号/逗号连接；全空则显示「未指定」。
- 注入 `_PROP_DESIGN["服化道设定"]` 三条通用指令：每件道具承载一个情感/叙事功能、材质/年代/磨损具体到可拍、服装色彩与场景主色形成关系。
- 角色绑定行取场景解析人物前 3 个；生成提示词拼「清单, 风格, 具体材质纹理, 情绪」，清单空则回退「核心道具」。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 节点模式 | 服化道设定 | 非法值回退 角色设定（角色分支），产出角色卡 |
| 服化道描述 | 旧信(泛黄), 凤梨罐头(过期), 钢笔(没墨水), 收音机 | 默认值非空会盖住 _关键道具 继承；清空后才走合并继承 |
| 核心数据包 | 含 _关键道具 的 JSON 包 | 不接 → 清单只剩默认文本或「未指定」，无角色绑定行 |
| 视觉风格 | 写实 | 逐字进生成提示词；「具体材质纹理」为固定段不可配 |

## 已知坑

- 默认服化道描述是示例文本（旧信/凤梨罐头…），不清理就永远看不到核心数据包继承效果。
- 角色绑定行来自 parse_scene 规则提取，可能含「主角/副线」占位名（probe 实证）。
- 清单空且无继承时生成提示词回退「核心道具」四字占位。
- tests/test_all_modes.py 断言本模式执行非空；经 Characters 节点拿不到 Asset 参考库 JSON 第二输出。

## 节点映射

- 实现文件：aggregator/characters_master.py :: DirectorMasterCharacters.build()（ASSET_MODES 委托 + costume 路由：非角色非环境即落服化道）
- 分支/函数：aggregator/asset_master.py :: DirectorMasterAsset.build() `else:` 分支；设计指令 `_PROP_DESIGN["服化道设定"]`
- 数据来源：核心数据包 _关键道具 + aggregator/scene_engine.parse_scene（物件/人物）
