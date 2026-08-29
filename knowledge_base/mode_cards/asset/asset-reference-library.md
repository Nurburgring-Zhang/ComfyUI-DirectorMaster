---
mode_id: asset-reference-library
node: DirectorMasterAsset
name: 参考库生成
one_liner: 为每类资产生成3-5张参考图方案，标注用途与派生链
applicable: [AI漫剧, 电影, 短视频, 广告]
intensity: medium
style_tags: [参考图规划, 用途标注, 派生链]
aliases: [参考图库, 参考方案]
---

## 意图

规划"每类资产该准备哪些参考图、每张用来锁什么"时选它。设计指令给出参考图工程规范：每类资产 3-5 张、每张标注用途（正面锁定/材质参考）、母版→变体派生链。

## 核心手法

1. 走服化道分支装配：清单读服化道描述；留空→_关键道具+场景物件合并继承；角色绑定行取核心角色前 3。
2. 设计指令块输出 `_PROP_DESIGN["参考库生成"]` 三条（3-5 张/用途标注/母版派生链）。
3. 节点实际收集 7 个参考图槽（角色正/侧/背、环境母版、道具母版、首帧、尾帧）与 2 个视频槽（运动/风格母版），已接引用进 ref_block 与参考库 JSON——本模式的指令块告诉用户该怎么补齐这些槽。
4. ref_block 按槽标注用途：正面→IP-Adapter 面部锁定、首帧→图生视频 first_frame、运动母版→锁定运镜节奏等；第二输出参考库 JSON 供下游 VideoRouter 消费。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 参考图_角色正面 | LoadImage IMAGE | 不接→ref_block 与参考库 JSON 均无此项；IMAGE 落盘成功返回文件名，失败回退 STRING 路径 |
| 参考视频_运动母版 | VIDEO 帧批次 | 接 VIDEO IMAGE 批次→抽帧落盘最多 8 张；非张量/环境缺 torch→空串 |
| 参考图路径 | 旧字段路径 | 仅当 7 个新图槽全空时兜底进"角色正面"槽；混用新槽后旧字段被忽略 |
| 核心数据包 | Core 输出 JSON 包 | 不接→清单继承断，方案卡缺资产名 |

## 已知坑

- "每类 3-5 张"是方案指令，节点本身每槽只收 1 图（视频槽抽帧 8 张）——3-5 张需多次运行或外部拼装。
- 参考库 JSON 在所有模式下都会输出，本模式不额外增强 JSON；价值在指令块引导用户正确接槽。

## 节点映射

- 实现文件：aggregator/asset_master.py
- 分支/函数：build() else 服化道分支；`_PROP_DESIGN["参考库生成"]`；参考收集 resolve_ref/image_batch_to_ref_paths（aggregator/ref_media.py）；ref_block 按槽用途映射；ref_library JSON 组装
- 数据来源：参考图 7 槽 + 参考视频 2 槽 + 旧字段兜底分支
