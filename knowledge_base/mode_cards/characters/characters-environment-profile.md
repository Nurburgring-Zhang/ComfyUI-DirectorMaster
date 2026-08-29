---
mode_id: characters-environment-profile
node: DirectorMasterCharacters
name: 环境设定
one_liner: 生成环境卡：三层空间设计指令+场景母版锚定，环境描述可继承场景文本
applicable: [竖屏微短剧, 短视频, 长片]
intensity: medium
style_tags: [环境卡, 场景母版, 空间锁定]
aliases: []
---

## 意图

立跨镜头复用的空间锚点时选它，环境类 16 模式的基座。与角色类的本质差别：输出落「环境圣经」路（角色圣经/服化道圣经为空串），三视图锚定路输出占位句而非三视图。本模式的设计指令是通用三层空间法，子模式（室内/太空等）各有专属三条。

## 核心手法

- 委托 DirectorMasterAsset 进入 `elif mode in _ENV_MODES:` 分支，产出「环境卡」落六路的环境圣经。
- 环境描述被手动清空时继承核心场景文本（scene，再退 core_loc）；场景内道具行取 parse_scene 物件前 4 个或 _关键道具 首段，都无则「无」。
- 注入 `_ENV_DESIGN["环境设定"]` 三条通用设计指令：空间三层（前景遮挡/中景动作区/后景信息层）、光源单一可解释、留一处人物生活痕迹。
- 环境锚定块固定三行：主色调按导演风格定、光影按情绪定、关键道具位置按场景描述定；生成提示词拼「环境类型场景, 描述, 风格, 导演, 情绪」。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 节点模式 | 环境设定 | 非法值回退 角色设定（角色分支），产出角色卡而非环境卡 |
| 环境描述 | 厨房8平米, 灶台+砧板+碗柜+餐桌+窗 | 默认值非空会盖住场景继承；手动清空后才继承核心场景文本 |
| 环境类型 | 室内 | 下拉仅室内/室外/太空/水下/虚拟五项，不随子模式联动——太空环境模式配默认值会生成「室内场景」提示词 |
| 核心数据包 | 含 _场景描述 的 JSON 包 | 场景与地点全空且描述被清空 → 环境描述行输出空文本 |

## 已知坑

- 「环境类型」下拉与 16 个环境子模式不同步：子模式名不参与提示词，进提示词的是下拉值（probe 实证：太空环境+默认下拉 → 「室内场景, 厨房8平米…」）。
- 默认环境描述「厨房8平米…」是历史示例文本，不清理就随卡输出。
- 本模式三视图锚定输出为固定占位句「(非角色模式 — 三视图锚定仅在角色类模式下生成)」（25 字，probe 实证），不是空白也不是真三视图。
- tests/test_all_modes.py 断言本模式执行非空；经 Characters 节点拿不到 Asset 的参考库 JSON 第二输出（包装层丢弃）。

## 节点映射

- 实现文件：aggregator/characters_master.py :: DirectorMasterCharacters.build()（ASSET_MODES 委托 + V13.1 六路三元路由的 env 路）
- 分支/函数：aggregator/asset_master.py :: DirectorMasterAsset.build() `elif mode in _ENV_MODES:` 分支；设计指令 `_ENV_DESIGN["环境设定"]`
- 数据来源：aggregator/scene_engine.parse_scene（物件/地点）；导演块来自 director_data_unified 档案
