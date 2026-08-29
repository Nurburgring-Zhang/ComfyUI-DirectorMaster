---
mode_id: characters-reference-image
node: DirectorMasterCharacters
name: 参考图
one_liner: IP-Adapter参考引导卡：IMAGE落盘或路径直填，无参考则占位提示
applicable: [IP-Adapter 工作流, 跨镜头一致性]
intensity: adaptive
style_tags: [参考图引导, IP-Adapter, 视觉锚点]
aliases: [参考图引导, IP-Adapter参考]
---

## 意图

已有角色参考图/视频、要生成 IP-Adapter 引导卡时选它。与 41 个 ASSET 模式的本质差别：不走 asset_master 模板，由 characters_master 直接处理——IMAGE 张量优先落盘成 PNG 文件名，路径槽兜底；无任何参考输入时输出占位提示而非报错。

## 核心手法

- `resolve_ref(kwargs, "参考图_IMAGE", "参考图路径", "角色参考")`：IMAGE 张量存在则经 image_to_ref_path 落盘（文件名 dm_角色参考_<时间戳>.png，存 ComfyUI input 目录），失败/无 torch 环境返回空再取路径槽。
- 参考视频：参考视频_IMAGE 张量经 image_batch_to_ref_paths 抽帧落盘（最多 8 帧，等步采样）；落盘失败回退参考视频路径槽。
- 组装引导卡四段：视觉锚点（参考图/视频清单，全无则「(未提供参考图/视频 — 可接 LoadImage/LoadVideo…)」）、IP-Adapter 提示词模板（主体=角色名+外貌+服装；风格+导演+情绪；场景）、使用建议 4 条（首镜锁定/每镜复用/FaceID 联合/视频锁运镜）。
- 六路输出特殊分配：角色圣经=一行「参考图锚定: {角色名} = {引用}」；环境圣经/服化道圣经=空串；三视图锚定/MIP资产卡/完整资产=同一份引导卡（probe 实证 480 字符 ×3）。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 参考图_IMAGE | LoadImage 的 IMAGE 输出 | 优先于路径槽；非 ComfyUI 环境（无 torch/PIL）落盘失败静默回退路径槽 |
| 参考图路径 | ref_face.png | IMAGE 槽无值时生效；两者皆空 → 视觉锚点段输出占位提示 |
| 参考视频_IMAGE | LoadVideo/VHS 的 IMAGE 批次 | 非张量或维度≠4 → 返回空列表，回退路径槽 |
| 角色名 | 主角 | 逐字进 IP-Adapter 模板主体段与角色圣经锚定行 |
| 角色外貌/角色服装 | 短发, 瘦削…/深蓝色工作服… | 拼进模板主体段；清空则对应字段空缺，不触发任何补全池 |

## 已知坑

- 本模式不经过 asset_master：无种子池、无核心场景继承、无导演档案块、无 6 份记忆摘要、不做 strip_decor——卡内 ═ 装饰线原样保留（probe 实证）。
- 三个输出（三视图锚定/MIP资产卡/完整资产）内容完全相同，MIP 卡名不副实。
- 角色外貌/服装留默认值会原样进模板主体段；本模式无「清空→补全」机制。
- tests/test_all_modes.py 断言本模式执行非空（无参考输入时靠占位提示文本通过）。

## 节点映射

- 实现文件：aggregator/characters_master.py :: DirectorMasterCharacters.build() 模式4 段（`ref_img = resolve_ref(...)` 起至 return）
- 分支/函数：aggregator/ref_media.py :: resolve_ref() / image_to_ref_path() / image_batch_to_ref_paths()
- 数据来源：仅节点输入（IMAGE 张量/路径/角色名/外貌/服装/视觉风格）+ 核心数据包（导演/场景/情绪）
