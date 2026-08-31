---
id: NP-001
rule: 连续近景/特写镜组的主体面部必须绑定同一参考锚点 (参考图/IP-Adapter/角色DNA锚点行); 画面内出现脸部漂移按生产问题单 face_drift 类目登记, 且返修优先级为"脸和手优先"。
precedent: 仓库内置 Higgsfield 后期问题单模板把"手脸"列为定剪后独立清理 pass 的第一类目 (face_drift 脸部漂移), 示例问题单给出实测形态与返修法 (rerun_with_modified_prompt); 资产注册表同步预设防线——正面全身参考图故意无头, 防小图取脸崩。本地暂无实测脸崩返工判例, 本条为生产分类学沉淀的预防性规则。
self_check: 每个连续近景/特写镜组是否绑定同一面部参考锚点? 出现脸部漂移时是否登记 face_drift 类问题单并按"脸和手优先"返修, 而不是当作可交付的偶然瑕疵?
evidence_ref: asset_registry_data.py:364 (categories 含 "face_drift" # 脸部漂移); asset_registry_data.py:377 (fix_priority=face_and_hands_first); asset_registry.py:302 (正面全身参考图"故意无头 (防小图取脸崩)")
---

# NP-001 脸部崩坏/漂移 (face_drift)

## 规则
面向连续镜组的主体一致性: 特写/近景是脸崩高发位——每换一次镜, 生成模型对面部 ID 的保持都没有保证。规则三层:
1. 同一角色的连续近景/特写镜组必须共享同一参考锚点 (参考图 / IP-Adapter 输入 / 角色 DNA 锚点行), 禁止每镜独立生成面部;
2. 生成画面中的脸部漂移 (五官偏移/换脸感/年龄跳变) 不是风格问题, 是缺陷——按后期问题单 `face_drift` 类目登记, 带 shot_id/时间点/描述;
3. 返修优先级固定"脸和手优先" (face_and_hands_first), 这是 Higgsfield 工作流沉淀的排序, 不是本仓库拍脑袋。

## 判例
来源为仓库内置生产问题单模板 (POST_ISSUE_LIST_TEMPLATE, 沉淀自 Higgsfield 定剪后清理 pass 方法论): 其 categories 列表第一项即 `face_drift  # 脸部漂移`, 与 `hand_extra_finger 多指`/`boil_texture 沸腾纹理` 等并列; example_issue 给出完整问题单形态 (shot_id=S02_T03_R01_05, category=hand_extra_finger, severity=high, fix_priority=face_and_hands_first, fix_method=rerun_with_modified_prompt, 带精确时间点 0:08.500 的描述)。资产注册表同样把脸崩视为预期失效: 正面全身参考图的用途注记明确写"模型取身体比例, 故意无头 (防小图取脸崩)"——即从素材源头规避小图取脸导致的崩脸。
诚实边界: 本仓库测试断言与历史版本记录中暂无本地实测的脸崩返工案例 (本仓库不产像素, 只产提示词与分镜); 本条判例为生产分类学证据, 规则定位为预防性——审查时仍按上述自检问题逐组核对。

## 自检
- 每个连续近景/特写镜组: 面部参考锚点是否同一? 有无"每镜各画各的脸"的裸生成?
- 成片若有脸部漂移: 是否已登记 face_drift 类问题单 (带 shot_id/时间点) 并按"脸和手优先"排返修?
- 角色参考素材: 是否存在小图取脸的隐患 (正面全身图是否按规范无头/低权重)?

## 证据指针
- asset_registry_data.py:364 — POST_ISSUE_LIST_TEMPLATE.categories 含 `"face_drift",  # 脸部漂移`
- asset_registry_data.py:362 — description "定剪后独立清理 pass: 手脸/文字/接缝/颜色/环境声/待补镜头"
- asset_registry_data.py:377 — `"fix_priority": "face_and_hands_first",  # Higgsfield: 优先级: 脸和手`
- asset_registry.py:302 — `purpose="正面全身 — 模型取身体比例, 故意无头 (防小图取脸崩)"`
