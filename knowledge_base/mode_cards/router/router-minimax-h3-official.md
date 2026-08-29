---
mode_id: router-minimax-h3-official
node: DirectorMasterRouter
name: MiniMax H3 (官方)
one_liner: 调真实 H3 引擎做 5 模式 IR 转换, 输出官方三字段加自检报告
applicable: [视频生成, 图生视频, 参考生视频]
intensity: high
style_tags: [官方格式, 上下文IR, 模式自动检测, 字段自检]
aliases: [H3, MiniMax H3]
---

## 意图

下游直接投 MiniMax H3 官方 API 时选它。与同节点其余 6 个目标只做单行格式化不同, 本模式是唯一走深度 IR 转换的目标: 按首尾帧/参考布尔组合自动判定 T2VA/I2VA/FL2VA/L2VA/Ref2VA, 输出官方三字段完整 prompt 并附字段自检。

## 核心手法

1. 5 模式自动检测: `_h3_deep_convert()` 把 有首帧/有尾帧/有参考素材 三个布尔交给 `select_h3_mode()` — 优先级 Ref2VA > FL2VA > L2VA > I2VA > T2VA; 判 Ref2VA 时 full_prompt 改走 6 段格式 (subject_definitions / summary / retention_analysis / detailed_description / overall_soundscape / non_diegetic_music), 其余模式走 Part One keyframe 对齐句 + 三字段。
2. 官方三字段组装: integrated_multimodal_description 以 [Shot N] At MM:SS.mmm 时间戳切镜 (时长 >4s 在中点追加 Shot 2), overall_soundscape 按场景关键词 (雨/夜/海/办公室等) 映射环境音, non_diegetic_music 按情绪映射配器 (孤独→Sparse piano, 悬疑→Low electronic pulse)。
3. 导演 8 维注入: 导演命中 35 导演库时注入镜头/光/节奏/色彩/表演/构图/声音/情绪 8 维加代表作/标志物件/年代; 未命中回退内置 5 导演档案, 再退默认推镜短语。
4. 字段自检: `_validate()` 输出 Part One 指令长度、Shot 数、camera motion 三维 (motion/amplitude/speed)、对白 `<d>` 标签检查, 附在输出块尾部。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 时长秒 | 8 | H3 路径强制钳制 max(4, min(15, dur)): 填 3 按 4s 转换、填 20 按 15s, 是 7 目标中唯一裁剪时长的分支 |
| 有参考素材 + 参考素材描述 | false / 空 | true 且描述非空才判 Ref2VA 并生成 Subject 2 段 (引用描述前 80 字符); 描述留空时按"无具体 reference"处理, 退回首尾帧判定链 |
| 视觉风格 | 电影感 | 经 _H3_VISUAL_MAP 映射英文 (黏土动画/定格动画→claymation, 纸艺/拼贴画→watercolor), 未映射值回退 Cinematic |
| 对白语言 | 英语 | 经 _H3_LANG_MAP 转 English/Chinese 等, 对白以 `<d>[Language]` 格式渲染进 multimodal; 其余 6 目标不消费该映射 |
| 有首帧/有尾帧 | false | 全 false 判 T2VA 且 Part One 为空; 置 true 生成 0.00 秒/尾秒 keyframe 对齐句, 是 I2VA/FL2VA/L2VA 的唯一判定依据 |

## 已知坑

- h3_context_ir_node.py 文件头已标 DEPRECATED (逻辑并入 UniversalDirectorPromptNode), 但 Router 仍 import 它做深度转换; knowledge_base/h3_prompt_framework 加载失败时 `convert_to_h3` 返回 fallback 元组而不抛异常, 输出块头仍写"深度 IR 转换", 需靠内嵌 "[H3 framework unavailable]" 与 "H3 Summary (Fallback)" 标记识别; 只有 convert_to_h3 真抛异常才走 "[DEGRADED]…降级为浅格式" 诚实降级分支。
- 时长 >4s 才有 Shot 2; 填 4s 整输出单镜 IR。
- tests/test_all_modes.py 断言 Router 三路输出非空, 本模式的模型提示词/视频生成请求/EDL 三槽都在覆盖内。

## 节点映射

- 实现文件：aggregator/router.py
- 分支/函数：convert_universal() 中 target == "MiniMax H3 (官方)" → `_h3_deep_convert()` → h3_context_ir_node.py :: H3ContextIRNode.convert_to_h3() (select_h3_mode / _build_instruction / _build_multimodal_description / _build_ref2va_prompt / _validate)
- 数据来源：director_data_unified.DIRECTOR_PROFILES_35 + SCENE_DATABASE_100、h3_prompt_framework.H3_MODES; 数据缺失时 H3_DIRECTOR_PROFILES_FALLBACK 内置 5 导演兜底。
