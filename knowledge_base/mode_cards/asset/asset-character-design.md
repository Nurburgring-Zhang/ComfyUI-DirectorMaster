---
mode_id: asset-character-design
node: DirectorMasterAsset
name: 角色设定
one_liner: 把角色五要素输入变成带三视图锚定与生成提示词的角色卡
applicable: [AI漫剧, 竖屏微短剧, 短视频, 动画]
intensity: medium
style_tags: [角色设定, 角色一致性, IP-Adapter]
aliases: [人物设定, 角色卡]
---

## 意图

通用人设入口：手头已有角色名/性格/外貌/服装素材，要一张能直接喂生成模型的角色卡。与主角/反派等细分模式的本质差别：叙事定位取通用"主要人物 — 全片视点与情感锚点"，不携带专属弧光或专属性格池。

## 核心手法

1. 单角色卡装配：读角色名/年龄/性别/性格/外貌/服装六槽，叙事定位取 `_CHAR_ROLE_HINT["角色设定"]`，逐行拼姓名/年龄/性别/性格/外貌/服装。
2. 缺槽确定性补全：性格/外貌/服装留空时按 md5 种子（场景_导演_情绪_模式_项目名）从 `_PERSONA_TRAITS`/`_LOOK_TRAITS`/`_WARD_TRAITS` 各选一条，同输入同输出。
3. 三视图锚定块：输出正面/侧面/背面半身提示词 + 中性表情与微笑/凝重/惊讶 3 情绪变体，标注"IP-Adapter 用"，并统计已接参考图数写进一致性策略行。
4. 道具绑定：核心场景解析出物件或核心包带 `_关键道具` 时取首个，写"此物件是人物情感的外化, 出场必带"。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 核心数据包 | Core 节点输出的 JSON 包 | 非法 JSON 被 parse_core_pack 丢弃→导演回退"王家卫"、场景/情绪置空，补全池种子随之全变 |
| 角色性格 | "沉默寡言, 内敛, 用行动表达"（默认） | 留空→按种子从 _PERSONA_TRAITS 选一条；填值原样使用不做清洗 |
| 角色服装 | "深蓝色工作服(褪色), 灰色秋衣, 布鞋"（默认） | 留空→本模式无时代衣冠池，走 _WARD_TRAITS 种子补全（古风/科幻等 5 个时代模式才走 _ERA_WARD） |
| 视觉风格 | 写实 | 选"🎲 随机"→系统随机 8 选 1，两次运行结果可能不同（非种子确定性） |
| 参考图_角色正面 | LoadImage 的 IMAGE 或 STRING 路径 | 两槽都不接→一致性策略行计 0 张参考图；IMAGE 落盘失败才回退 STRING 路径 |

## 已知坑

- 角色名留默认"主角"且核心场景解析出角色时，姓名被静默替换为解析结果首位（parse_scene 返回 characters 截前 3 个）。
- 补全池种子含项目名：改"项目名"会连带改补全的性格/外貌/服装。
- tests/test_all_modes.py 全模式扫描对本模式断言执行非空；"Asset·6份项目记忆"断言输出含"Higgsfield 6 份文件"——六文档注入异常走 stderr 降级但节点不失败。

## 节点映射

- 实现文件：aggregator/asset_master.py
- 分支/函数：build() `mode in _CHARACTER_MODES` 单角色子分支；`_CHAR_ROLE_HINT["角色设定"]`；补全池 `_PERSONA_TRAITS/_LOOK_TRAITS/_WARD_TRAITS` + `_aseed_choice()`；道具绑定 prop_bind 分支；三视图锚定块
- 数据来源：核心数据包（_导演风格/_场景描述/_情绪基调/_关键道具）→ aggregator/scene_engine.py :: parse_scene；全模式注入 asset_registry_data.get_six_documents_summary()；导演档案 aggregator/node_base.py :: _director_block
