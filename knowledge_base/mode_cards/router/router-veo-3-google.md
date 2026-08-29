---
mode_id: router-veo-3-google
node: DirectorMasterRouter
name: Veo 3 (Google)
one_liner: 4K 拟真英文 prompt, 元数据时长窗 4-8s 为 7 目标最短
applicable: [视频生成, 高保真短片, 创意广告]
intensity: medium
style_tags: [4K拟真, 高保真, 英文prompt]
aliases: [Veo, Google视频]
---

## 意图

高保真 4K、拟真材质、创意短镜头选它。元数据窗 4-8s 全节点最短, 明确面向 8 秒内单场景镜头而非叙事长片。

## 核心手法

1. 高保真前缀 prompt: "High-fidelity 4K, creative, physics-true: {scene}, {visual}风格, {emotion}情绪, {dur}s." — 无画幅段。
2. 声场声明位: MODEL_OPTIMIZERS 声明 ambient_sound 音频字段（H3 与短剧平台亦有各自音频字段声明）; 但 Router 未把任何输入映射到该字段, 环境声只能经 EDL audio_cues 与【生成指令增强】的非画内音乐间接表达。
3. EDL 音频留白规则: build_edit_decision_list() 音频轨 music 字段按镜号 i%3==0 写 "none(留白)", 其余写 "极简钢琴单音" — 留白节奏由 shot 循环位置决定而非情绪推导。
4. payload 走 veo3 键: vendor Google, endpoint aiplatform.googleapis.com/veo/v1/videos。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 时长秒 | 8 | 元数据 max 8 不强制: 填 20 原样进 prompt/payload, 超窗只有官方 API 侧才会拒绝; 链路内仅 max(3, dur) 兜底 |
| 视觉风格 | 电影感 | 进 "{visual}风格" 段; 与 H3 不同本分支不做英文风格映射, 中文风格词原样输出 |
| 非画内音乐 | 空 | 截 200 字进指令增强; audio_fields 声明的 ambient_sound 无输入口, 不会出现在 payload 专属字段 |
| 核心数据包 | 空 | _情绪基调 缺失回退"通用" — prompt 情绪段将输出"通用情绪"字面量 |

## 已知坑

- 元数据窗 4-8s 纯说明性, 链路内无钳制无警告 — 超窗 payload 照常产出, 需人工守窗。
- 视觉风格选 🎲 随机 时运行时改选且不可复现; IS_CHANGED 以原始 kwargs 哈希, 同参数重跑可能命中缓存不重掷。
- 未发现针对本分支的独立测试断言; 依赖 test_all_modes.py "Router 三路输出非空" 的公共覆盖。

## 节点映射

- 实现文件：aggregator/router.py
- 分支/函数：convert_universal() elif target == "Veo 3 (Google)" + MODEL_OPTIMIZERS["Veo 3 (Google)"] + target_to_key["veo3"]
- 数据来源：aggregator/cinema_craft.py :: VIDEO_MODELS["veo3"] / build_edit_decision_list() music 留白规则 (i%3)。
