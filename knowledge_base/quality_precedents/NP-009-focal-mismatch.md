---
id: NP-009
rule: 焦段必须按景别电影学匹配 (特写 85-135mm、近景 70-100mm、中景 35-50mm、全景 24-35mm、远景 20-28mm、大远景 14-18mm), 消灭"中近景 12mm"式失配; 用户显式焦段偏好优先, 否则按 focal_for_size 修失配; 匹配率≥90%。
precedent: V16.5 落地判例: _FOCAL_BY_SIZE 九档景别→焦段池映射 (scene_entity.py), CHANGELOG 记录动机"消灭'中近景 12mm'"; 矩阵质量项"焦段-景别匹配≥90%"以 check_focal_match 逐镜核查, 是 71 用例 rubric 的常驻项。
self_check: 每镜焦段是否落在其景别的合理焦段池内? 全片匹配率是否≥90%? 用户显式焦段偏好是否被尊重 (偏好优先于自动匹配)?
evidence_ref: aggregator/scene_entity.py:240-258 (_FOCAL_BY_SIZE + focal_for_size); tests/test_matrix_full.py:60,146-147 (check_focal_match + 匹配≥90%); docs/CHANGELOG.md:38 ("消灭'中近景 12mm'")
---

# NP-009 景别焦段错配 (focal-size mismatch)

## 规则
焦段是空间语言: 长焦压缩=亲密/压迫, 广角展开=疏离/尺度。"中近景 12mm"这类错配会让模型画出畸变人脸或错误透视, 是提示词层的物理穿帮。规则:
1. 匹配表: 按电影学常识映射 景别→焦段池 (大远景 14-18mm / 远景 20-28mm / 全景 24-35mm / 中全景 28-35mm / 中景 35-50mm / 中近景 50-70mm / 近景 70-100mm / 特写 85-135mm / 大特写 100-150mm 微距);
2. 优先级: 用户显式焦段偏好 > 实体引擎自动匹配 (只修失配, 不覆盖偏好);
3. 逐镜核查: 匹配率 ≥90% 为质量项下限, 失配镜逐镜列出;
4. 未知景别: 回退通用组 (35/50/85mm), 不猜。

## 判例
V16.5 场景实体引擎提交把 focal_for_size 列为七件套之一, CHANGELOG 新增节原文: "focal_for_size 焦段-景别电影学匹配 (特写 85-135mm / 全景 24-35mm, 消灭'中近景 12mm')"——判例原型即矩阵实测中反复出现的"中近景 12mm"式荒诞组合。实现以 _FOCAL_BY_SIZE 九档池 + 镜号 md5 确定性取值 (同输入同输出, 不同镜位有分布); Cinematic 接线处注释明确 "6.1 焦段-景别匹配 (用户显式焦段偏好已在上方生效, 此处只修失配)"。矩阵 rubric 的 check_focal_match 从此把匹配率≥90% 变成回归红线。

## 自检
- 逐镜: 景别→焦段是否落在映射池内? (特写配 14mm = 直接打回)
- 匹配率是否≥90%?
- 用户焦段偏好是否存在? 存在则自动匹配不得覆盖它。

## 证据指针
- aggregator/scene_entity.py:240-251 — _FOCAL_BY_SIZE 九档映射表
- aggregator/scene_entity.py:254-258 — focal_for_size (确定性取值, 未知景别回退通用组)
- tests/test_matrix_full.py:60 — check_focal_match 定义; :146-147 — "焦段-景别匹配≥90%" 质量项
- docs/CHANGELOG.md:38 — "消灭'中近景 12mm'" 动机记录
