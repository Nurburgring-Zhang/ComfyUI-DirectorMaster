---
mode_id: router-short-drama-platform
node: DirectorMasterRouter
name: 短剧平台 (抖音/快手/小红书)
one_liner: 3-7 秒钩子加字幕驱动单行格式, payload 映射可灵 API
applicable: [竖屏短剧, 投流素材, 短视频]
intensity: medium
style_tags: [钩子开场, 字幕驱动, 竖屏短剧]
aliases: [短剧, 投流]
---

## 意图

投抖音/快手/小红书的竖屏强情绪素材选它。与"通用"的差别: prompt 骨架是钩子/镜数/字幕三项投放要素, 场景描述退居冒号之后; payload 落点不是内容平台而是快手可灵视频 API。

## 核心手法

1. 投放格式前缀: "3-7s hook, 1-3 shots, strong emotion, subtitle-driven: {scene}, {emotion}, {dur}s, {aspect}." — 7 目标中唯一不含视觉风格段的 prompt (风格只经 CINEDANCE 骨架块间接携带)。
2. 钩子指令: 钩子风格下拉 (视觉冲击/悬念问题/情感冲击/动作冲击/反差冲击) 非"无"时进【生成指令增强】"钩子风格: X (前3秒抓人)"。
3. 字幕指令: 需要字幕=true 时输出 "需要字幕: 是 (台词驱动, 字幕清晰)"; 元数据窗口 3-30s 是唯一超过 widget 上限 20 的目标。
4. payload 走 kling 键: target_to_key 把本目标映射到 VIDEO_MODELS["kling"] (vendor 快手可灵, endpoint api.klingai.com/v1/videos/text2video, fields prompt/duration/aspect_ratio/cfg_scale)。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 钩子风格 | 无 | 保持"无"则不生成钩子指令行; 选五种钩子之一只影响指令增强, 不改写前缀里的镜数/时长 |
| 需要字幕 | false | true 时加字幕指令行; 该布尔不改变 payload 结构, 字幕渲染责任在下游 |
| 画幅比例 | 9:16 短剧竖屏 | payload aspect_ratio 原样携带 "9:16 短剧竖屏" 全串 (Router 不做 split 清洗, VideoRouter 才做), 直连可灵 API 前需自行截 "9:16" |
| 时长秒 | 8 | 元数据 max 30 但 widget 上限 20, 实际可填 3-20; 程序化调用超 20 不拦 |

## 已知坑

- 名为"短剧平台"但 payload endpoint 是可灵 API, 不是抖音/快手开放平台内容接口 — 平台投放对接需下游另接。
- 视觉风格下拉在本分支完全不进 prompt; 想要风格化需依赖 CINEDANCE 骨架块或 AI 轨重写。
- tests/test_all_modes.py "Router 三路输出非空" 覆盖本分支 payload/EDL 的有效性。

## 节点映射

- 实现文件：aggregator/router.py
- 分支/函数：convert_universal() elif target == "短剧平台 (抖音/快手/小红书)" + MODEL_OPTIMIZERS["短剧平台 (抖音/快手/小红书)"] + target_to_key → "kling"
- 数据来源：aggregator/cinema_craft.py :: VIDEO_MODELS["kling"]; 无外部数据库。
