---
mode_id: characters-dreamscape
node: DirectorMasterCharacters
name: 梦境场景
one_liner: 生成梦境场景卡：空间断裂/熟悉场景陌生化/光线无来源三条设计指令
applicable: [心理短片, 意识流]
intensity: medium
style_tags: [环境卡, 梦境, 陌生化]
aliases: []
---

## 意图

立梦境空间锚点时选它。专属差异是 `_ENV_DESIGN["梦境场景"]` 三条指令（空间连续性可断裂 / 熟悉场景的陌生化变形 / 光线无来源）；与记忆场景模式的差别在断裂方向——梦境变形、记忆褪色。

## 核心手法

- 进入 `elif mode in _ENV_MODES:` 分支，环境卡落「环境圣经」路。
- 设计指令块注入梦境三条；断裂/变形的具体设计无字段承载，落进环境描述。
- 环境描述清空时继承核心场景文本——梦境常以现实场景为底，「继承现实场景再陌生化」正是预期用法。
- 环境锚定块按导演定主色调、按情绪定光影；「光线无来源」指令与锚定行「光影按情绪定」并存，无仲裁。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 节点模式 | 梦境场景 | 非法值回退 角色设定 |
| 环境描述 | （清空以继承现实场景作底） | 手写时可直接写变形后场景；保留默认厨房文本则厨房成了梦境底版 |
| 环境类型 | 虚拟/室内 | 梦境无专属下拉项，语义最近的是虚拟；影响提示词前缀 |
| 核心数据包 | 含 _情绪基调 的 JSON 包 | 情绪为空 → 光影锚定行与提示词情绪段留空 |

## 已知坑

- 「光线无来源」与锚定行「光影: 按情绪({mood})定」两段并存卡内，mood 空时后者留空文本。
- 下拉与子模式不同步（全环境类共性）。
- 与记忆场景的指令差一条都不同，互审时按三条指令逐字区分，勿互换。
- tests/test_all_modes.py 断言本模式执行非空；三视图锚定路输出占位句。

## 节点映射

- 实现文件：aggregator/characters_master.py :: DirectorMasterCharacters.build()（ASSET_MODES 委托 + env 路由）
- 分支/函数：aggregator/asset_master.py :: DirectorMasterAsset.build() `elif mode in _ENV_MODES:` 分支；设计指令 `_ENV_DESIGN["梦境场景"]`
- 数据来源：aggregator/scene_engine.parse_scene
