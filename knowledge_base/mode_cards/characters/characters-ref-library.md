---
mode_id: characters-ref-library
node: DirectorMasterCharacters
name: 参考库生成
one_liner: 参考库派生指令的服化道分支卡：给出参考图规划文案，真实登记靠参考输入
applicable: [多资产项目, IP-Adapter 工作流]
intensity: adaptive
style_tags: [服化道卡, 参考库, 派生链]
aliases: [参考库]
---

## 意图

规划跨镜头参考图体系时选它。实现口径：本模式落服化道分支，产出的是「每类资产 3-5 张参考图 + 用途标注 + 母版→变体派生链」的设计指令文案；真实的参考图登记发生在输入侧（IMAGE 槽/路径槽），经 Asset 生成 ref_block 与参考库 JSON。

## 核心手法

- 走 `else:` 服化道分支，设计指令块注入 `_PROP_DESIGN["参考库生成"]` 三条：每类资产 3-5 张参考图、参考图标注用途（正面锁定/材质参考）、母版→变体派生链。
- 输入侧真实登记：接了参考图（IMAGE 槽落盘或路径槽直填）时，资产文本尾部追加「多图参考库」块，逐槽标注用途（正面→IP-Adapter 面部锁定 / 环境母版→空间光影色调锁定 / 首帧→图生视频 first_frame 等）。
- 参考计数进「一致性策略」行（「加载 N 张参考图」）；N 经 Characters 节点只统计单参考槽。
- 参考库 JSON（含全部槽位与统计）是 Asset 节点第二输出，经 Characters 包装层被丢弃。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 节点模式 | 参考库生成 | 非法值回退 角色设定 |
| 参考图路径 | ref_face.png | 填了就按「角色正面」槽登记并进 ref_block；IMAGE 槽有值时路径槽被优先级规则覆盖 |
| 参考视频路径 | motion_ref.mp4 | 登记为「运动母版 → 锁定运镜/节奏」；无任何参考输入时 ref_block 整块不出现 |
| 服化道描述 | （清空以继承） | 清单与参考库规划文案相互独立，清单空不影响参考块 |

## 已知坑

- 经 Characters 节点只有「参考图_IMAGE/参考图路径」两个图槽可用，Asset 的七槽体系（侧面/背面/首帧/尾帧等）不可达；要完整参考库必须直用 DirectorMasterAsset。
- 参考库 JSON 在 Characters 六路输出中不存在（包装层取 [0] 丢弃第二输出），下游 VideoRouter 拿不到结构化登记。
- IMAGE 槽在本模式映射到「角色正面」槽（_img_key_map 只认三个基础模式名），语义错位但计数照加。
- tests/test_all_modes.py 断言本模式执行非空。

## 节点映射

- 实现文件：aggregator/characters_master.py :: DirectorMasterCharacters.build()（ASSET_MODES 委托 + costume 路由；IMAGE 槽映射 `_img_key_map.get(mode, "参考图_IMAGE_角色正面")`）
- 分支/函数：aggregator/asset_master.py :: DirectorMasterAsset.build() `else:` 分支（指令 `_PROP_DESIGN["参考库生成"]`）+ ref_block 构建（resolve_ref / image_batch_to_ref_paths）
- 数据来源：参考输入槽 + 核心数据包 _关键道具 + aggregator/scene_engine.parse_scene
