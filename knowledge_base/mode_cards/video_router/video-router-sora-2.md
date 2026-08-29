---
mode_id: video-router-sora-2
node: DirectorMasterVideoRouter
name: Sora 2
one_liner: 全英文优化块加导演运镜指令, body 走 OpenAI videos 接口
applicable: [视频生成, 写实短片, 多角色调度]
intensity: high
style_tags: [英文prompt, 物理真实, 复杂调度]
aliases: [Sora, OpenAI]
---

## 意图

多角色、精确物理、长时序写实视频选它。是 5 路中唯一全英文输出块 (优化要点/主 Prompt 标签/Camera Direction 全英文) 的分支, 明确 "English prompts preferred"。

## 核心手法

1. 英文优化块: physical realism & complex staging / long-form, multiple characters, precise physics / English prompts preferred 三条要点固定输出。
2. Camera Direction 块: Movement 填导演署名运镜 ("{director}'s signature camera work")、Composition 60-30-10 色彩法则加三分法、Lighting 9D 光影 — 导演只以名字注入, 不展开 12 维档案。
3. body 组装: endpoint api.openai.com/v1/videos, model sora-2, size 取画幅按空格切分前段, seconds=str(视频时长_秒) (字符串型秒数是 OpenAI videos 接口口径), input_reference 单首帧 — 与 Hailuo 双帧不同只带首帧。
4. content 截 800 字进【Main Prompt (English)】, 中文分镜不翻译直接嵌入。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 视频时长_秒 | 8 | str(duration) 直转 body.seconds, 无 5-20s 窗口校验 (Router 同名目标的 min 5 元数据不在本节点生效) |
| 画幅比例 | 16:9 横屏 | size 取 "16:9"; 选 🎲 随机 改选 4 画幅之一 |
| 核心数据包 | 空 | 导演回退"王家卫"写入 Camera Direction 与元数据; 场景为空时 base_scene 场景段空串 |
| 首帧图片 | 空 | 经参考库进 body.input_reference; 只认"首帧"键, 尾帧在本路被忽略 |

## 已知坑

- prompt 块 Tech Specs "FPS: 24" 硬编码, 帧率 参数只影响 LTX 的 num_frames 与元数据回显, 不进本路文本。
- 中文 content 不翻译: 英文优化块下嵌中文主 prompt, 语言混排是否被接口接受未在链路内验证。
- 800 字截断无标注, 长英文分镜尾部丢失。

## 节点映射

- 实现文件：aggregator/video_router_master.py
- 分支/函数：_optimize_for_model() else 分支 (Sora 2) + _build_api_requests_json()["Sora 2"] (seconds=str(duration))
- 数据来源：无外部库; 导演来自 parse_core_pack()._导演风格。
