---
mode_id: cinematic-miniapp-twist
node: DirectorMasterCinematic
name: 反转小程序分镜
one_liner: 反转钩子小程序剧分镜，反转拍自动配一秒三闪快闪语法
applicable: [反转小程序剧, 悬念投流素材, 神反转短剧]
intensity: high
style_tags: [反转, 小程序, 悬念, 一秒三闪, 快切]
aliases: []
---

## 意图

反转钩子驱动的小程序剧分镜：0.3 密度快切打底，反转拍（story_function 命中"反转/失去"）自动切一秒三闪——铺垫快切与反转快闪的结构对比就是投流钩子。

## 核心手法

- 体量推导：1min → 2 场 × 10 镜（density 0.3）；节拍生成器给两场功能（铺垫→反转类），反转场的 story_function 触发 STORY_FUNC_PACING["反转"]→一秒三闪。
- 双节奏结构：铺垫场走分支 D（密度快切 + "快切"运镜签名），反转场走分支 C 快闪组公式（1.9s/组、0.3s×3+1s 收束）——同一集内两种镜头结构并存。
- 悬念标注：反转镜的 purpose/note 携带节奏意图文案（"0.3s 情绪爆破点"），JSON 情感强度在反转镜跳变——卡点依据。
- 主导运镜：铺垫场 move="快切" 覆写 2/3 镜；反转场运镜由一秒三闪模板接管（快推/快摇/拉远）。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 目标时长(分钟) | 1（=60 秒/集） | 0.75min → int 截断 1 场——单场内仍可完成 铺垫→反转 功能切换 |
| 节奏风格 | 无(默认)=auto | 钉"一秒三闪"会把铺垫场也变成快闪——反转对比消失；保持 ND 才有双节奏结构 |
| 核心数据包 | Core 32 字段 JSON | 反转功能词需进剧本/场景（节拍表按输入生成）——纯画面描述无剧情词时两场功能雷同 |
| 剪辑节奏 | 无(默认) | 任何倍率档破坏 ±1% 覆盖；反转场的快闪组对倍率尤其敏感（0.3s 镜×0.5=0.15s） |

## 已知坑

- 反转拍位置由节拍表 story_function 决定（第二场概率最高但非固定）——"最后 15 秒反转"需剧本配合，引擎不保证位置。
- 三胞胎问题同 爽剧小程序：与另两个小程序模式区分度靠 mode_seed 变体与签名 note；双节奏结构（铺垫 D + 反转 C）是本模式独有的结构差异。
- 快闪组的 0.3s 镜在缩放下限保护下不变——反转场时长缺口全由收束镜吸收，反转"回神"镜可能被压扁。

## 节点映射

- 实现文件：aggregator/cinematic_studio.py；aggregator/pacing_engine.py；aggregator/feature_film_engine.py
- 分支/函数：MODE_PACING["反转小程序分镜"]（dur_scale 0.3, move "快切"）→ build_standard_shots(density_scale=0.3, pacing_mode="auto") → 铺垫场 分支 D / 反转场 get_pacing_for_scene("反转")→一秒三闪 → 分支 C（PACING_GROUP_FORMULAS["一秒三闪"]）
- 数据来源：pacing_engine.STORY_FUNC_PACING（反转/失去→一秒三闪）；PACING_STYLES["一秒三闪"]
