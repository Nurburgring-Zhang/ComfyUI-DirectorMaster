---
mode_id: vibe-ecommerce-set
node: DirectorMasterVibe
name: 电商套图
one_liner: 生成主图→细节→场景→对比→信任五段电商套图设计指令(count=4)
applicable: [电商详情页, 产品推广, 直播物料]
intensity: medium
style_tags: [电商套图, 主图铁律, 购买决策链]
aliases: [商品套图]
---

## 意图

给一个产品出一整套"能下单"的图组设计指令时选它：按主图(点击)→细节图(品质)→场景图(代入)→对比图(差异)→信任图(口碑)的购买决策链输出设计要求。与"海报设计"的本质差别：多图组链路逻辑，不是单张视觉冲击。

## 核心手法

1. 适配器 _build_design_adapter("电商套图") 调 modes_design._build_ecommerce_prompt：主图铁律"主体占画面60%+ 白底或纯色, 标题大且醒目"。
2. 五段链每段有独立验收点（细节=微距材质纹理、场景=人物与产品互动、信任=认证/口碑）。
3. 适配器参数装配：topic=场景前 80 字（空则"未命名产品"）、subject=首个角色或物件、style=商业摄影、color_tone=_视觉调性（空则"高对比"）、count 恒为 4。
4. 产品材质/颜色/拍摄角度/布光/背景五槽恒传空串 → 提示词内落内置默认建议（多角度组图/柔光箱主光+补光+轮廓光/纯色背景）。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 核心数据包 | 含 _视觉调性/_场景描述 的 JSON | 空包时色彩基调落"高对比"、主体落"产品待定" |
| 产品材质/产品颜色 | 实现签名存在但 Vibe 适配器恒传 "" | 提示词显示"待定"，材质颜色要求全部落默认口径 |
| 拍摄角度/布光方案/背景类型 | 同上恒传 "" | 落内置默认（多角度/电商标准三点布光/纯色+实景），无法自定义 |
| 启用反AI规则 | True | False 时输出不做套话清洗 |

## 已知坑

出图数量恒 4 张（适配器硬编码 count=4，非用户参数）且与五段链 5 图位不一一对应——需要 5 张以上要改代码或 AI 轨补；modes_design 导入失败时 stderr 写"[DirectorMaster] 设计模式降级"并返回"设计模式生成降级"占位文本。tests/test_all_modes.py 断言输出含"电商套图"。

## 节点映射

- 实现文件：aggregator/vibe_studio.py
- 分支/函数：TEMPLATES["电商套图"] → _build_design_adapter("电商套图") → modes_design.py :: _build_ecommerce_prompt()（modes_design.py:25）
- 数据来源：modes_design 内置电商设计原则文案，无外部库
