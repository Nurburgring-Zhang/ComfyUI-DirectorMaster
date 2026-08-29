---
mode_id: characters-hellgrind-asset-library
node: DirectorMasterCharacters
name: HellGrind资产库
one_liner: 接线真实引擎：descriptor/状态变体/签名/压测/锁定报告
applicable: [一致性优先项目, IP 资产运营]
intensity: high
style_tags: [HellGrind, descriptor锁定, 压力测试]
aliases: [HellGrind, 资产库]
---

## 意图

要 Higgsfield Hell Grind 生产体系那套硬一致性时选它——唯一走真实引擎（非模板拼接）的模式。产出 descriptor 锁定描述符、状态变体、5 维声音/行为签名、完整生成 Prompt 块、压力测试报告与可选锁定报告。注意：经本节点（Characters）调用时资产固定为 @roco。

## 核心手法

- `if mode == "HellGrind资产库":` 分支调 `_build_hellgrind_asset()`，直连根模块 asset_registry（非模板池）。
- Descriptor 段输出注册表锁定描述符与「一次只改一行」铁律；状态选「(默认)」时列出全部可用状态变体（@roco 有 blood/injured/wet/clothed_change/crystal 五态）。
- `kind=="character"` 资产追加 5 维 Voice Signature 与 Behavior Signature；随后输出 render_asset_prompt 完整生成块（face/body 去头/背面三类 ref 描述）。
- 压力测试默认开：pressure_test 报 10 轮同帧一致性结果与失败模式检查（probe 实证「轮数: 10 | 全部通过: True」）；HellGrind锁定=True 时追加 lock_asset 锁定报告（锁定后 descriptor 不可改）。
- 资产不存在时整卡降级为一行「HellGrind资产库: 未找到资产 {name} (可选: 全部注册名)」。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 节点模式 | HellGrind资产库 | 非法值回退 角色设定，脱离引擎走模板 |
| 核心数据包 | 含 _导演风格 的 JSON 包 | 影响卡头「导演:」与导演档案块；引擎内容本身不依赖它 |
| 参考图路径 | （可空） | 与引擎输出无关；只影响 ref_block 与一致性计数行 |
| 项目名 | 我的电影项目 | 逐字进卡头；不影响 registry 查询 |

## 已知坑

- 经 Characters 节点调用时，HellGrind资产名/状态版本/压力测试/锁定 四个输入未在本节点 INPUT_TYPES 声明——probe 实证恒为 @roco / (默认) / 压测开 / 锁定关；要换 @jax/@rein/@lulu/@kaine/@loc_*/@crystal_sword 必须直用 DirectorMasterAsset 节点。
- 注册表实际 8 资产（5 角色 + 2 场景 + 1 道具），与六文档摘要文案里的「3 地点 + 5 道具」不一致，以 registry 为准。
- 六路输出落「服化道圣经」路（非角色非环境），probe 实证 7499 字符；角色圣经/环境圣经两路为空串。
- 输出尾部追加 Higgsfield 6 份项目记忆摘要（tests/test_all_modes.py 断言「Higgsfield 6 份文件」存在）；注入失败仅写 stderr「6文档注入降级」，不失败节点。

## 节点映射

- 实现文件：aggregator/characters_master.py :: DirectorMasterCharacters.build()（ASSET_MODES 委托 + costume 路由）
- 分支/函数：aggregator/asset_master.py :: DirectorMasterAsset.build() `if mode == "HellGrind资产库":` → `_build_hellgrind_asset(kwargs, project, director)`
- 数据来源：asset_registry（ASSET_REGISTRY/get_descriptor/get_state_descriptor/get_voice_signature/get_behavior_signature/render_asset_prompt/pressure_test/lock_asset）；asset_registry_data.get_six_documents_summary
