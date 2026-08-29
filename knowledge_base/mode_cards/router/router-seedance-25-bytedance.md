---
mode_id: router-seedance-25-bytedance
node: DirectorMasterRouter
name: Seedance 2.5 (字节)
one_liner: 物理一致 3D CG 前缀 prompt, payload 固定字节键
applicable: [视频生成, 3D 动画, 产品展示]
intensity: medium
style_tags: [物理一致, 多角度, 单行格式]
aliases: [Seedance, 豆包视频]
---

## 意图

要 3D CG 质感、物理一致、多角度呈现时选它。与"通用"的差别: prompt 固定 "3D CG, physics-consistent, multi-angle:" 能力前缀锁物理特性, payload 静态绑定 seedance2.5 键 (火山引擎 endpoint)。

## 核心手法

1. 能力前缀单行 prompt: convert_universal() 分支拼 "3D CG, physics-consistent, multi-angle: {scene}, {visual}风格, {emotion}情绪, {dur}s." — 不含画幅段, 画幅只进 payload 的 aspect_ratio。
2. 上游内容三级注入: 分镜输入截 3000 字前置【分镜内容基础(来自管线)】块; 无分镜时 剧本输入截 3000 字前置【剧本内容基础(优先级最高)】, 再退 统一电影提示词截 2000 字。
3. EDL 6 镜 + payload: build_video_api_payload("seedance2.5", …) 产出 vendor 字节、endpoint api.volcengine.com/seedance/v1 的请求体, shot_list 与 audio_cues 取自 build_edit_decision_list() 音视频轨, 音频 cue 由 parse_scene 从场景物件/天气/地点实时生成。
4. 【生成指令增强】统一拼接对白/音乐/钩子/字幕/故事理论/首尾帧六类指令行。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 用户意图 | 父女厨房雨夜, 霓虹灯在雨水中反射 | scene 取 核心数据包._场景描述, 缺包时回退本参数; 两者全空则 prompt 场景段为空串, 只剩能力前缀与风格情绪 |
| 时长秒 | 8 | MODEL_OPTIMIZERS 标 min 4/max 12 但 build() 不按它钳制, 填 20 原样进 prompt 与 payload, 需自行守 4-12s |
| 剧本输入 | 空 | 填写即以 3000 字截断成为最高优先级内容基础, 同时挤掉 分镜输入与统一电影提示词 的前置块 (elif 链) |
| 视觉风格 | 电影感 | 进 prompt "{visual}风格" 段; 选 🎲 随机 时运行时改选 12 风格之一, 结果不可复现 |

## 已知坑

- 元数据窗口 4-12s 是说明性字段, 链路内唯一真实裁剪点是 payload 的 duration=max(3, dur) — 只有 3 以下才兜底。
- 非法目标值防御在目标层: target 不在 TARGETS 时静默回退"通用 (兼容所有模型)", 程序化传参拼错枚举名不报错不告警, 真实落点要看第 2 路 payload 的 target_model 字段。
- tests/test_all_modes.py "Router·CINEDANCE骨架" 与 tests/ten_rounds.py T4 断言输出含 CINEDANCE 15 块骨架, 本模式同样追加该块。

## 节点映射

- 实现文件：aggregator/router.py
- 分支/函数：convert_universal() elif target == "Seedance 2.5 (字节)" + MODEL_OPTIMIZERS["Seedance 2.5 (字节)"] + target_to_key 映射 "seedance2.5"
- 数据来源：aggregator/cinema_craft.py :: VIDEO_MODELS["seedance2.5"] / build_edit_decision_list() / build_video_api_payload(); 骨架来自 style_prefix_data.render_style_prefix()。
