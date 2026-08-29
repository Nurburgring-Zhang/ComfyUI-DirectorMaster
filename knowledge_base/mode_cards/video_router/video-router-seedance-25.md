---
mode_id: video-router-seedance-25
node: DirectorMasterVideoRouter
name: Seedance 2.5
one_liner: 中文物理一致优化块加能力边界元数据, 火山方舟 body 带参考图
applicable: [视频生成, 3D 动画, 多参考生成]
intensity: medium
style_tags: [中文prompt, 物理一致, 参考库]
aliases: [Seedance, 豆包]
---

## 意图

单选 Seedance 出中文友好、物理一致 prompt 并直连火山方舟请求体时选它。与"全部生成"的差别: 其余 4 路输出为 "(未生成 — 目标为 Seedance 2.5)" 占位串, 7 路槽位结构不变。

## 核心手法

1. `_optimize_for_model("Seedance 2.5")` 分支输出四段块: 优化要点 (中文 prompt 友好避免英文从句 / 强项 3D CG 物理一致多角度 / 描述运镜光影物理材质不强调长对白) + 主 Prompt (content 截 800 字) + 技术规格 + 【EDL 决策】6 镜平均 duration//6 s/镜、转场硬切加偶尔叠化。
2. 能力边界注入元数据: master_director_data.SEEDANCE_25_CAPABILITIES 提取 版本/单镜最大秒/延展最大秒/最大参考资产数/图参考上限/视频参考上限 写进第 6 路元数据 (tests/test_all_modes.py "VideoRouter·Seedance能力边界" 断言元数据含 "单镜最大秒")。
3. 参考库块追加: 参考图/参考视频逐行 "tag: path" 追加到 prompt 尾部; 综合JSON 的 body.reference_images 收全部参考图值 — 5 模型中唯一带 reference_images 数组的 body。
4. body 组装: endpoint ark.cn-beijing.volces.com/api/v3/contents/generations/tasks, model doubao-seedance-2-5, ratio 取画幅按空格切分前段 ("16:9"), negative_prompt 是 5 模型中唯一消费 负向提示词 输入的 body 字段。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 目标视频模型 | Seedance 2.5 | 选本值只生成本路; 其余 4 路 prompt 槽与综合JSON 内 results 均为占位串, 下游需按槽位取用 |
| 视频时长_秒 | 8 | 3-30; 【EDL 决策】文本用整除 duration//6 (8s 显示 1s/镜), 与实际 6 镜均分 1.3s 有口径差 |
| 负向提示词 | 模糊, 变形, 多余手指, 文字水印, 低质量 | 仅进本模型 body 与元数据; prompt 块内【负向】行是硬编码 4 项, 改输入不影响 prompt 文本 |
| 参考库JSON | Asset.参考库JSON | 非法 JSON 静默吞掉 (except: pass), 参考图计数 0 且无告警; 合法时独立 forceInput 槽按键覆盖同名字段 |

## 已知坑

- prompt 块技术规格"帧率: 24fps"为硬编码, 帧率 参数只进 body 不进 prompt 文本。
- 元数据"场景"截 100 字、主 Prompt 截 800 字, 长分镜尾部丢失无提示。
- AIGC 生产模式判别失败时降级为 ("文生视频", "降级") 并写 stderr "[DirectorMaster] AIGC生产模式判别降级", 可查元数据 AIGC判别依据 字段核实。

## 节点映射

- 实现文件：aggregator/video_router_master.py
- 分支/函数：build() targets 分支 (target in VIDEO_ROUTER_MODES → 单路) + _optimize_for_model("Seedance 2.5") + _build_api_requests_json()["Seedance 2.5"]; 能力边界提取段 (SEEDANCE_25_CAPABILITIES)
- 数据来源：master_director_data.SEEDANCE_25_CAPABILITIES; 参考库解析 aggregator/ref_media.py :: resolve_ref()。
