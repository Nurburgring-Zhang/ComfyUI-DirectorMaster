---
mode_id: video-router-hailuo-23
node: DirectorMasterVideoRouter
name: Hailuo 2.3
one_liner: 钩子加主体加收尾三段式, body 直填首尾帧图字段
applicable: [竖屏短剧, 短视频, 抖音快手素材]
intensity: medium
style_tags: [钩子开场, 字幕驱动, 短剧向]
aliases: [海螺, Hailuo]
---

## 意图

抖音/快手竖屏、8 秒标准时长、强情绪转折的素材选它。是 5 路中唯一"前3秒钩子 + 主体 + 收尾落点"三段式 prompt 结构的分支, 也是唯一把首帧与尾帧都写进 API body 字段的路。

## 核心手法

1. 三段式 Prompt: 前3秒 (视觉冲击/悬念/反差抓眼球) + 主体 (content 截 800 字) + 收尾 (情绪落点 + 留白/反转) — 固定三段模板。
2. 字幕建议块: 关键对白加字幕、字号大居中或下方、钩子文案 1-2 行强情绪。
3. 技术规格标注 "9:16 竖屏 (默认) 或 {画幅}" — 5 路中唯一在 prompt 层建议竖屏默认值的分支。
4. body 组装: endpoint api.hailuoai.video/v1/video/generate, model MiniMax-hailuo-2.3, first_frame_image/last_frame_image 直取参考库"首帧"/"尾帧"键 — 与 Sora 路单首帧 input_reference 不同, 本路首尾帧都带。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 首帧图片 / 尾帧图片 | 空 | STRING 路径槽与 _IMAGE 张量槽二选一 (IMAGE 优先落盘); 首尾帧齐备时 AIGC 判别升级为"首尾帧生视频" |
| 参考库JSON | Asset.参考库JSON | 非法 JSON 静默吞掉; 首帧/尾帧键缺失时 body 对应字段为空串, 不报错 |
| 视频时长_秒 | 8 | 优化要点标 8s 标准时长但无钳制, 3-30 原样进 body.duration |
| 负向提示词 | 模糊, 变形, 多余手指, 文字水印, 低质量 | 本路 body 无负向字段, 输入不生效 |

## 已知坑

- 元数据"首帧/尾帧"布尔只检查 首帧图片/尾帧图片 STRING 槽是否非空 — 直接接 首帧_IMAGE 张量时元数据显示 false, 但 body 经参考库仍生效; AIGC 判别用参考库口径, 两处口径不一致需看元数据"参考图清单"核实。
- Hailuo body 无 fps/negative 字段, 帧率与负向输入对本路无效。
- tests/test_all_modes.py 与 tests/ten_rounds.py T5 以 VideoRouter 公共输出结构覆盖本分支 (元数据可解析、槽位齐全)。

## 节点映射

- 实现文件：aggregator/video_router_master.py
- 分支/函数：_optimize_for_model("Hailuo 2.3") 分支 + _build_api_requests_json()["Hailuo 2.3"] (first_frame_image/last_frame_image 取 参考图.首帧/尾帧)
- 数据来源：参考库合并段 (standalone_refs 按键覆盖) + aggregator/ref_media.py :: resolve_ref()。
