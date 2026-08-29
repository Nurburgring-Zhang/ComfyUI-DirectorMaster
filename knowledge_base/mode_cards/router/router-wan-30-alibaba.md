---
mode_id: router-wan-30-alibaba
node: DirectorMasterRouter
name: Wan 3.0 (阿里)
one_liner: 中文简洁强美学前缀 prompt, 画幅只进 payload 不进 prompt
applicable: [视频生成, 氛围短片, 国风动画]
intensity: medium
style_tags: [中文prompt, 强美学, 简洁动作]
aliases: [通义万相, Wan]
---

## 意图

中文提示词驱动、重美学氛围、动作简洁的镜头选它。是 7 目标中唯一全中文前缀格式 ("中文提示词, 简洁动作, 强美学:") 的分支, 且模型 prompt 不含画幅段 — 画幅信息只落 payload。

## 核心手法

1. 中文前缀单行 prompt: "中文提示词, 简洁动作, 强美学: {scene}, {visual}, {emotion}, {dur}s." — 与 Seedance 分支同为无画幅格式, 且视觉风格不带"风格"后缀。
2. EDL 场景驱动音频: build_edit_decision_list() 经 aggregator.scene_engine.parse_scene 提取物件/天气/地点, 生成六条音频 cue (如 "{天气}声+{地点}底噪"、"{物件}被触碰的轻响") 注入 payload 的 audio_cues 轨。
3. payload 走 wan3.0 键: vendor 阿里通义万相, endpoint dashscope.aliyuncs.com/wan/v1/video, fields prompt/duration/size/seed。
4. 导演继承: 核心数据包._导演风格 缺失时回退"王家卫", 进 EDL 元信息与 payload 的 project 元数据。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 画幅比例 | 16:9 横屏 | 不进模型 prompt, 仅原样写入 payload aspect_ratio (含"横屏"中文后缀, 直连第三方 API 前需自行清洗) |
| 非画内音乐 | 空 | 填写后截 200 字进【生成指令增强】; Wan 分支无独立音频字段位, 音乐意图只能经指令增强表达 |
| 核心数据包 | 空 | 无包时导演固定"王家卫"、场景回退 用户意图、情绪"通用", 三者全部写死不报错 |
| 时长秒 | 8 | 元数据窗口 3-15 不强制, 仅 max(3, dur) 兜底; 填 20 原样透传 |

## 已知坑

- 目标模型传非法值时回退"通用 (兼容所有模型)"再走 seedance2.5 payload — 确认真实落点需看第 2 路输出 payload 的 target_model 字段而非输入回显。
- 对白语言参数在本分支不进 prompt (语言映射只有 H3 分支消费), 中文对白写进 对白 参数后经【生成指令增强】原样透传。
- 未发现针对本分支的独立测试断言; 依赖 test_all_modes.py "Router 三路输出非空" 的公共覆盖。

## 节点映射

- 实现文件：aggregator/router.py
- 分支/函数：convert_universal() elif target == "Wan 3.0 (阿里)" + MODEL_OPTIMIZERS["Wan 3.0 (阿里)"] + target_to_key["wan3.0"]
- 数据来源：aggregator/cinema_craft.py :: VIDEO_MODELS["wan3.0"] / build_edit_decision_list() 音频 cue 场景驱动段; 场景解析 aggregator.scene_engine.parse_scene。
