---
mode_id: video-router-ltx-25
node: DirectorMasterVideoRouter
name: LTX-2.5
one_liner: 6 镜职能骨架拆镜输出, body 按时长乘帧率算 num_frames
applicable: [视频生成, 多机位剪辑, 蒙太奇]
intensity: medium
style_tags: [多角度拼接, 镜头一致性, 分镜骨架]
aliases: [LTX, Lightricks]
---

## 意图

同场景多机位、时间流逝、蒙太奇类视频选它。是 5 分支中唯一以"分镜 Prompt"职能骨架 (而非单一主 prompt) 组织内容的模型路。

## 核心手法

1. 6 镜职能骨架: 镜1 按导演/场景/情绪实时填充建立镜头, 镜2-5 固定职能句 (推进/切入/特写/视角转换, 要求色调光影连贯), 镜6 收束留白 — 建议拆 4-8s 短镜。
2. 负向定制: prompt 块【负向】行 "跳轴, 色调不连贯, 角色走形" — 与 Seedance 路的物理向负向不同, 针对拼接连贯性。
3. body 组装: endpoint api.ltx.video/v1/generate, model ltx-2.5, num_frames = 视频时长_秒 × 帧率 (8s×24fps=192), reference_videos 收参考库全部视频 — 5 模型中唯一参考视频进 body 的路。
4. 参考库块与 Seedance 路同构追加; content 基础按 分镜脚本 > 剧本输入 > 统一电影提示词 > 核心包场景 优先级取 800 字。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 帧率 | 24 (12-60) | 只参与 num_frames 计算, 不进 prompt 文本; 30s×60fps=1800 帧无上限校验, 超模型常规生成窗口需下游裁剪 |
| 视频时长_秒 | 8 | 线性放大 num_frames; 【技术规格】只写总时长, 无每镜时长字段 |
| 分镜脚本 | Cinematic.分镜 | content 最高优先级来源 (截 800 字); 为空时依次回退 剧本输入 → 统一电影提示词 → 核心包场景 → "(未提供内容)" |
| 运动母版视频 / 运动母版_IMAGE | 空 | IMAGE 张量经 ref_media.image_batch_to_ref_paths 落盘 (默认抽 8 帧) 并入参考视频; 无 torch/PIL 环境返回空串静默降级 |

## 已知坑

- 6 镜文案中镜 2-5 是固定职能句, 不随场景差异化; 场景具体性全靠镜 1 与 base_scene 行承载。
- content 截 800 字: 长剧本/长分镜尾部直接丢失, 无截断标注。
- 未选中本模型时本路输出 "(未生成 — 目标为 X)" 占位, 综合JSON 的 LTX body.prompt 同样是占位串, 直提交 API 会生成空语义请求。

## 节点映射

- 实现文件：aggregator/video_router_master.py
- 分支/函数：_optimize_for_model("LTX-2.5") 分支 + _build_api_requests_json()["LTX-2.5"] (num_frames = duration * fps)
- 数据来源：参考视频聚合 aggregator/ref_media.py :: image_batch_to_ref_paths() (max_frames=8); 无外部数据库。
