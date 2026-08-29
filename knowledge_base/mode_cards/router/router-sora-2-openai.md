---
mode_id: router-sora-2-openai
node: DirectorMasterRouter
name: Sora 2 (OpenAI)
one_liner: 长视频复杂调度英文 prompt, payload 走 sora2 秒数独立字段
applicable: [视频生成, 长镜头调度, 写实短片]
intensity: high
style_tags: [物理真实, 复杂调度, 英文prompt]
aliases: [Sora, OpenAI视频]
---

## 意图

多角色调度、物理真实、最长时序的视频选它。元数据窗口 5-20s（短剧平台时长上限另可达 30s）, prompt 是含画幅段的英文长句格式。

## 核心手法

1. 英文长视频前缀 prompt: "Long-form, complex staging, physics-realistic: {scene}, {visual}风格, {emotion}情绪, {dur}s, {aspect}." — 与 通用/短剧平台 同为含画幅段的三个分支之一。
2. EDL 固定六镜序列: 景别 全景/中景/中近景/特写/中景/全景, 运镜 Truck right slow/静态/Push in slow/静态(手持微晃)/慢推/静态, 转场 硬切/硬切/匹配剪辑/跳切/硬切/淡出 — 按 shot index i%6 循环, 与总时长无关。
3. payload 走 sora2 键: vendor OpenAI, endpoint api.openai.com/v1/videos, fields prompt/model/seconds/size; 时长与帧率由 payload 通用段 (duration_sec/fps) 承载。
4. 对白指令: 对白参数截 300 字进【生成指令增强】并标注 "(语言: {对白语言})", 语言默认英语但不强制改写对白文本。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 时长秒 | 8 | 元数据 min 5 不强制: 填 3 照常生成 3s prompt/payload, 仅 payload 通用段 max(3, dur) 兜底 |
| 画幅比例 | 16:9 横屏 | 进 prompt 尾段与 payload aspect_ratio; 选 "9:16 短剧竖屏" 时 prompt 出现中文画幅串 |
| 对白 | 空 | 截 300 字, 超长静默丢弃; 语言仅作标注不改写文本 |
| 核心数据包 | 空 | _情绪基调 缺失时情绪回退"通用"写进 prompt; _导演风格 缺失回退"王家卫"进 EDL 与 payload |

## 已知坑

- MODEL_OPTIMIZERS.langs 只有英语, 但链路不做翻译或校验 — 中文对白原样拼接进指令增强, 官方 API 对非英语输入的表现未在链路内验证。
- EDL/shot_list 恒 6 镜: 8s 时每镜 1.3s、20s 时 3.3s, 镜头节奏不随时长重新设计。
- tests/ten_rounds.py T4 断言 Router 输出含 CINEDANCE 骨架, 本分支同样在 prompt 尾部追加该块。

## 节点映射

- 实现文件：aggregator/router.py
- 分支/函数：convert_universal() elif target == "Sora 2 (OpenAI)" + MODEL_OPTIMIZERS["Sora 2 (OpenAI)"] + target_to_key["sora2"]
- 数据来源：aggregator/cinema_craft.py :: VIDEO_MODELS["sora2"] / build_edit_decision_list() shot_sizes/moves/cut_types 固定序列。
