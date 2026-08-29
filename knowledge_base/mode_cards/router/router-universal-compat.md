---
mode_id: router-universal-compat
node: DirectorMasterRouter
name: 通用 (兼容所有模型)
one_liner: 中性单行格式加六类指令增强, 兜底分支与 CINEDANCE 骨架注入
applicable: [视频生成, 通用素材, 跨模型复用]
intensity: low
style_tags: [通用格式, 兜底分支, 指令增强]
aliases: [通用, 兼容模式]
---

## 意图

不确定下游模型或要先产通用素材时选它, 也是节点下拉默认值。与其他目标的差别: prompt 无模型专有前缀且同时携带画幅段, 元数据窗 3-20s 与 widget 边界一致, 是唯一无窗口矛盾的分支。

## 核心手法

1. 中性单行 prompt: "Universal: {scene}, {visual}风格, {emotion}情绪, {dur}s, {aspect}." — 无模型能力词。
2. 两级兜底: convert_universal() 对不在 TARGETS 的 target 先回退本模式的 else 分支生成 model_prompt, model_key 再回退 "seedance2.5" — 非法枚举永不报错。
3. CINEDANCE 15 块视觉骨架: style_prefix_data.render_style_prefix() 追加【CINEDANCE 15 块视觉骨架】块, 注入失败写 stderr "[DirectorMaster] CINEDANCE骨架注入降级" 不中断 (tests/test_all_modes.py "Router·CINEDANCE骨架" 与 tests/ten_rounds.py T4 断言该块存在)。
4. AI 双轨重写: 有 AI接口地址 时 _ensure_ai_output 以 LLM 重写 prompt, 生成结果 ≤200 字视为失败保留模板; 无 key 时模板原样输出。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 目标模型 | 通用 (兼容所有模型) | 下拉默认; 非法值静默落本模式; 选 🎲 随机 运行时改选 7 目标之一, 且 IS_CHANGED 只哈希原始 kwargs, 同参数重跑命中缓存不重掷 |
| 统一电影提示词 | 空 | 剧本输入缺位时截 2000 字前置【统一电影提示词(导演意图)】块; 两者都填时本参数被 elif 跳过 |
| 核心数据包 | 空 | 场景/情绪/导演/AI 配置继承源; 无包时导演"王家卫"、情绪"通用"写死 |
| 时长秒 | 8 | 本模式元数据 min 3/max 20 与 widget 边界一致, 无窗口矛盾 |

## 已知坑

- payload 的 negative_prompt 是硬编码英文质量词串 ("masterpiece,best quality,…,变形,多手,模糊"), 无输入口; 换负向需下游改写 payload。
- 指令增强六类 (对白/音乐/钩子/字幕/故事理论/首尾帧) 至少填一项才追加; 首帧/尾帧是纯布尔声明, 本节点无图片输入槽, "已提供"仅指下游有图。
- 属性下拉 (视觉风格/对白语言/画幅/故事理论/钩子) 选 🎲 随机 时均运行时改选, 受 IS_CHANGED 缓存影响可能不重掷。

## 节点映射

- 实现文件：aggregator/router.py
- 分支/函数：convert_universal() else 分支 (model_prompt) + target_to_key["通用 (兼容所有模型)"]→"seedance2.5" + CINEDANCE 骨架注入段; AI 轨 aggregator/node_base.py :: _ensure_ai_output()
- 数据来源：style_prefix_data.render_style_prefix() (CINEDANCE 15 块); 负向词串硬编码于 aggregator/cinema_craft.py :: build_video_api_payload()。
