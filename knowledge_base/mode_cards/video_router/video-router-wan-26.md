---
mode_id: video-router-wan-26
node: DirectorMasterVideoRouter
name: Wan 2.6
one_liner: 少对白重氛围美学锚点块, body 走 dashscope wan2.6-t2v
applicable: [视频生成, 氛围短片, 国风动画]
intensity: medium
style_tags: [中文prompt, 美学锚点, 慢节奏]
aliases: [通义万相, Wan]
---

## 意图

美学向、慢节奏、氛围电影的镜头选它。优化要点全中文且明确"少对白 多视觉 重氛围 强色调", 是 5 路中唯一给出运镜收敛建议 (慢推/慢移/固定为主) 的分支。

## 核心手法

1. 美学锚点块: 色温按情绪定 (暖/冷)、9D 光影设计、黄金分割与 9 宫格构图、慢推慢移固定运镜 — 四条锚点为固定模板文本。
2. 主 Prompt 中文 content 截 800 字; base_scene 行拼接 导演/情绪/画幅/时长 元信息, 随 core 缺项出现空段。
3. body 组装: endpoint dashscope.aliyuncs.com/api/v1/services/aigc/video-generation/video-synthesis, model wan2.6-t2v, 结构 input.prompt + parameters.{duration, ratio, fps} — 5 模型中唯一双层嵌套 body。
4. 导演继承: 核心数据包缺失或无 _导演风格 键时都回退"王家卫", 进锚定行与元数据。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 画幅比例 | 16:9 横屏 | 选 🎲 随机 时改选 4 画幅之一; parameters.ratio 取按空格切分前段, prompt 文本携带全串 |
| 负向提示词 | 模糊, 变形, 多余手指, 文字水印, 低质量 | 本路 body 无 negative_prompt 字段, 该输入对 Wan 路完全无效 (只有 Seedance body 消费) |
| 核心数据包 | 空 | 无包时 场景""/情绪""/导演"王家卫"; base_scene 行出现空情绪段, 元数据 场景 键为空串 |
| 视频时长_秒 | 8 | 3-30 原样进 parameters.duration, 无模型窗口钳制 |

## 已知坑

- 美学锚点是静态文案, 不随输入数据变化; 与情绪联动的只有"色温按情绪定"一句, 无实际色温推导。
- AIGC 生产模式判别 (参考视频>首尾帧>多参考图>首帧>文生) 结果只进元数据, 本路 prompt 不因生产模式改写。
- 未发现针对本分支的独立测试断言; 依赖 tests/ten_rounds.py T5 对 VideoRouter 元数据解析的公共覆盖。

## 节点映射

- 实现文件：aggregator/video_router_master.py
- 分支/函数：_optimize_for_model("Wan 2.6") 分支 + _build_api_requests_json()["Wan 2.6"]
- 数据来源：无外部库 (节点内置模板文本); 导演/场景/情绪来自 parse_core_pack()。
