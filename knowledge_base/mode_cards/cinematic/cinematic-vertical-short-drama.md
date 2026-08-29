---
mode_id: cinematic-vertical-short-drama
node: DirectorMasterCinematic
name: 竖屏微短剧分镜
one_liner: 竖屏短剧分镜，0.4密度钩子快切（镜数×2.5），3-5分钟单集体量
applicable: [竖屏微短剧, 短剧平台, 单集钩子剧]
intensity: high
style_tags: [微短剧, 竖屏, 快切钩子, 高密度]
aliases: []
---

## 意图

竖屏短剧的单集分镜：3-5 分钟/集、镜数是基线 2.5 倍的快切钩子节奏。与 横屏 的差别是更高密度与推近特写倾向；与 小程序剧三兄弟 的差别是场数体量（3 场 vs 2 场）与密度档（0.4 vs 0.3）。

## 核心手法

- 体量推导：3min → get_beat_map ≥3 梯 max(3, 2)=3 场；5min → 3 场（t/1.5=3）；density_scale=0.4 → 分支 D target_avg=4s → 每场镜数=max(12, 场秒/4)——3min 单集约 45 镜。
- 主导运镜：move="快切+推近" 覆写 2/3 镜——竖屏语法的"怼脸"倾向由推近承担；每 3 镜 1 镜原生。
- 钩子链：开场建立镜（establishing 池 opening=True）+ 反应/微距镜配额（//12、//20）提供高频情绪点；张力曲线把冲突推到集尾。
- 密度边界：0.4 在 clamp [0.3, 4.0] 内——镜数公式稳定。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 目标时长(分钟) | 3-5（单集） | 桶化 ≥20→30：设 10 实际按 30min 梯（8 场）出——单集感消失 |
| 节奏风格 | 无(默认)=auto | 钉"抖音超快"进一步提速（叠乘效应：pacing 组公式接管镜数，密度失效）；"🎲 随机" 不生效 |
| 核心数据包 | Core 32 字段 JSON | _平台媒介 进 JSON/上下文——短剧平台名供下游投放语义，不影响镜头生成 |
| 剧本输入 | Script 短剧剧本 | 前 6 块驱动 purpose；竖屏短剧台词密，建议每块对应一个钩子 |

## 已知坑

- 若同时显式设 节奏风格（pacing 钉死），density_scale 自动失效（pacing 模式不叠密度）——0.4 密度只在 auto 路径生效，混用会静默改变镜量。
- 模式主导运镜覆写发生在偏好覆写之后——运镜风格_多选 的弧值在非保留镜会被"快切+推近"盖掉。
- 竖屏构图（主体中上 60%、底部字幕位）是 format_templates 短视频模板的文案原则——Cinematic 分镜表不产出字幕位布局，字幕位仅叙事编排的 _arrange_plan 有"字幕位"字段（需编排下拉激活）。

## 节点映射

- 实现文件：aggregator/cinematic_studio.py；aggregator/feature_film_engine.py
- 分支/函数：MODE_PACING["竖屏微短剧分镜"]（dur_scale 0.4, move "快切+推近"）→ build_standard_shots(density_scale=0.4) → get_beat_map ≥3 梯 → generate_feature_shots 分支 D（establishing/反应/微距 配额）
- 数据来源：feature_film_engine.SHOT_POOL_BY_DENSITY；pacing_engine.STORY_FUNC_PACING；narrative_arrangement（字幕位字段）
