---
mode_id: script-vlog
node: DirectorMasterScript
name: Vlog脚本
one_liner: 第一视角口播 5 槽：对镜头开场→体验主线→空镜呼吸→真实意外→感受收尾
applicable: [Vlog, 体验类视频, 生活记录]
intensity: medium
style_tags: [第一视角, 口播真实感, 手持, 计划外时刻]
aliases: [VLOG脚本]
---

## 意图

个人视角的体验记录：对镜头说话是结构核心（开场与收尾都是口播）。与课程教学的差别：不做知识点分段，主线是体验过程本身，计划外时刻被显式保留为真实感资产。

## 核心手法

- `FORMAT_SCENE_SKELETONS["Vlog脚本"]`（script_studio.py:1104）5 槽：第一视角口播开场→体验过程·主线→空镜插拍·节奏调节→小意外·真实时刻→感受收尾；6min 下 5 场。
- 执行层 Vlog 分支（:1244-1248）逐场标注口播形式：对镜头说感受 30s / 边走边说（手持）/ 画外音+现场声交替（seed 三选一）。
- 槽位 mission 硬约束："今天做什么/为什么值得看""保留真实的反应和对话""小意外不剪掉，真实感往往在这里""给观众一个情绪出口"。
- `FORMAT_MODE_FLAVOR`（:931）：手持真实感、穿插空镜/转场、个人化语气。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 目标时长(分钟) | 0（自动→6） | 显式 >24 → 退出 5 槽覆盖走阶梯；3-24min 恒 5 场 |
| 对白密度 | 无(默认)→标准对白 | 口播即对白；"零对白"档与 Vlog 形态根本冲突（只剩空镜结构） |
| 潜文本强度 | 无(默认)→中 | 建议零档——个人表达以直白为真实感来源 |
| 核心数据包 | Core.核心数据包 | 体验对象（探店/旅行/日常）须写进场景描述；"探店"等词不在 loc_keywords 时地点锚定回落语义兜底 |

## 已知坑

- 体验类场景词（探店/美食街）依赖 parse_scene 词表：输入过偏的体验对象时地点锚定退化，空镜槽会落通用池。
- "小意外不剪掉"是拍摄纪律，引擎只能预留结构位，无法编造真实意外——素材层面靠实拍。

## 节点映射

- 实现文件：aggregator/script_studio.py
- 分支/函数：`_build_full_screenplay()`（:1413）+ FORMAT_SCENE_SKELETONS["Vlog脚本"]（:1104）+ 执行层 Vlog 分支（:1244）
- 数据来源：FORMAT_SCENE_SKELETONS/FORMAT_MODE_FLAVOR 内置表 + aggregator/scene_engine.parse_scene
