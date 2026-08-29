---
mode_id: vibe-mv-director
node: DirectorMasterVibe
name: MV导演
one_liner: 接线 mv_pro 引擎输出 BPM+七段音乐结构+节拍剪辑映射的 MV 方案
applicable: [音乐MV, 歌曲宣传视频, 短视频卡点]
intensity: high
style_tags: [BPM结构, 节拍剪辑, 七段式]
aliases: [音乐视频导演]
---

## 意图

给一首歌/一段音乐出 MV 拍摄方案时选它：由 mv_pro 引擎产出 BPM、七段音乐结构与节拍-剪辑映射的完整方案，而非单场导演提示。与"剪辑"的本质差别：以音乐节拍为时间轴骨架组织画面。

## 核心手法

1. 调用 mv_pro.MvPro().build_mv(场景描述/导演风格/情绪基调/启用反AI规则=True)，并透传核心包的 关键道具/_潜文本_情感/_导演意图_观众应感到 三个槽修复引擎空变量。
2. 引擎返回 tuple 时取首元素作为正文；正文长度 >200 字符才采纳。
3. 引擎抛异常或输出过短时静默回退 _generic_vibe_template 的通用分支（五感细节输出要求），无降级提示。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 核心数据包 | 含 _关键道具/_潜文本_情感/_导演意图_观众应感到 的 JSON | 空包时引擎收到三个空串，靠内部缺省填充，画面与歌词对位变弱 |
| 导演风格 | 继承核心包 _导演风格（缺省 王家卫） | 影响引擎与导演锚定块两处；库外导演无锚定块 |
| 启用反AI规则 | True（节点开关） | 引擎调用恒传 True；节点开关只控制输出文本的二次清洗 |
| 情绪基调 | 继承核心包 _情绪基调（缺省 孤独） | 传入引擎用于分段情绪走向，缺省值不改写 |

## 已知坑

引擎失败（import 失败/输出 <200 字符）走 except: pass 静默回退，stderr 无任何提示，用户看到的是通用五感模板却以为拿到了 MV 方案——正文出现"输出要求: 五感细节"字样即为回退信号。tests/test_all_modes.py 只断言非空，拦不住这种降级。

## 节点映射

- 实现文件：aggregator/vibe_studio.py
- 分支/函数：TEMPLATES["MV导演"] → _build_mv_engine() → mv_pro.py :: MvPro.build_mv()（mv_pro.py:513）；回退 _generic_vibe_template()
- 数据来源：mv_pro 引擎内置音乐结构库 + 核心数据包透传字段
