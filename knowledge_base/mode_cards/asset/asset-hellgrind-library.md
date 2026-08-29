---
mode_id: asset-hellgrind-library
node: DirectorMasterAsset
name: HellGrind资产库
one_liner: 调用asset_registry引擎输出身份合同、状态、签名、压测、锁定
applicable: [电影, AI漫剧, 短视频]
intensity: high
style_tags: [Higgsfield复刻, 资产锁定, 压力测试]
aliases: [资产注册表, 资产库, Hell Grind]
---

## 意图

要用内置 8 资产（@roco/@jax/@rein/@lulu/@kaine 五角色 + @loc_* 两场景 + @crystal_sword 一道具）的工业级锁定工作流时选它。与 40 个模板模式的本质差别：本模式不走模板拼装，直接调用 asset_registry 真实引擎输出身份合同。

## 核心手法

1. 引擎取数：`_build_hellgrind_asset()` 按 HellGrind资产名 取 AssetRecord，输出 descriptor（身份合同 + ≥3 身份锚点 + 参考图清单 + 状态索引 + 锁定状态）。
2. 状态变体：HellGrind状态版本 非"(默认)"时输出状态块（descriptor_delta + 声音/行为 delta + 状态专属参考图）；"(默认)"时改为列出该资产可用状态。
3. 角色 kind 附加声音签名（5 维英文 one-liner）与行为签名（pace/hand_habit/eye_movement/pressure_response/pre_break_action）；场景/道具无此两块。
4. 压力测试（默认开）输出 10 轮姿势/光线轮换报告 + 同框检查 + 4 类失败模式检查；锁定（默认关）走 lock_asset，输出逐字粘贴 descriptor。资产名/状态支持下拉"🎲 随机"。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| HellGrind资产名 | @roco（默认） | 填不存在名字→输出"HellGrind资产库: 未找到资产 …(可选: …)"错误行，节点仍返回非空不抛异常 |
| HellGrind状态版本 | (默认) | 填不存在状态→get_state_descriptor 回退输出"状态不存在+可用列表+基础描述"，不报错 |
| HellGrind压力测试 | True | 关掉→输出缺压测报告块；对场景/道具 kind 跳过测试，报告显示"全部通过: False"但无未通过项（见坑） |
| HellGrind锁定 | False | 对角色开→输出锁定报告（先自动补跑压测）；对场景/道具开→永远 locked False"压力测试未通过, 不能锁定" |
| 视觉风格 | 写实 | 本模式卡面不含视觉风格行（引擎输出为主），该参数只进参考库 JSON |

## 已知坑

- _build_hellgrind_asset 内 `import asset_registry` 无 try 保护：模块缺失时本模式直接抛异常，而下拉兜底函数 _hellgrind_names() 却会静默回退 ["@roco"]——输入框有值、执行崩溃的组合状态。
- pressure_test 对非 character 资产早退返回 dict 不含 all_pass 键，_build_hellgrind_asset 取 `pt.get('all_pass', False)` 显示"全部通过: False"；lock_asset 同因判 False——@loc_*/@crystal_sword 永远不可锁定（mock 边界，非真失败）。
- 资产名/状态版本选"🎲 随机"走系统随机（random.choice），非 _aseed_choice 种子确定性——同输入两次运行结果不同。
- tests/ten_rounds.py T3 断言资产输出含 "Higgsfield" 或 "ASSET_REGISTRY"——引擎输出天然满足。

## 节点映射

- 实现文件：aggregator/asset_master.py
- 分支/函数：build() `mode == "HellGrind资产库"` 分支 → `_build_hellgrind_asset()`；🎲 随机处理（资产名/状态版本）；引擎 asset_registry.py :: get_descriptor/get_state_descriptor/get_voice_signature/get_behavior_signature/render_asset_prompt/pressure_test/lock_asset/_get_asset
- 数据来源：asset_registry.ASSET_REGISTRY（5 角色 2 场景 1 道具，_build_roco/_build_jax/_build_rein/_build_lulu/_build_kaine/_build_loc_training_room/_build_loc_museum/_build_crystal_sword 注册）；ref_block 与六文档注入照常追加
