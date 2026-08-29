---
mode_id: characters-vehicle-design
node: DirectorMasterCharacters
name: 交通工具设计
one_liner: 生成交通工具卡：内饰磨损/声音先行/涂装地域年代三条设计指令
applicable: [公路题材, 都市短剧]
intensity: medium
style_tags: [服化道卡, 载具, 声音特征]
aliases: []
---

## 意图

做载具专项时选它。与服化道设定的差别收敛为 `_PROP_DESIGN["交通工具设计"]` 三条指令（内饰磨损匹配车龄 / 声音特征先行：引擎/铃铛 / 涂装有地域与年代依据）；分支与继承机制共用。

## 核心手法

- 走 `else:` 服化道分支，卡落「服化道圣经」路。
- 设计指令块注入载具三条；车龄/涂装地域无字段，落进服化道描述（如「1998 面包车, 车门锈穿, 挂本地货运牌」）。
- 服化道描述清空时继承 _关键道具 + 场景物件前 4；场景解析很少提载具，继承常错位。
- 角色绑定行取场景解析人物前 3 个；生成提示词固定追加「具体材质纹理」段。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 节点模式 | 交通工具设计 | 非法值回退 角色设定 |
| 服化道描述 | （手写载具规格） | 清空后继承普通物件，载具卡里出现信件/钢笔 |
| 核心数据包 | 含 _场景描述 的 JSON 包 | 场景文本含载具词时才可能被解析进物件 |
| 视觉风格 | 写实 | 逐字进提示词 |

## 已知坑

- 「声音特征先行」无音频能力支撑，纯文案指令。
- 涂装年代/地域代码无从校验，防穿帮靠手写描述的准确性。
- 与参考视频「运动母版」槽（锁运镜）无联动：载具动态参考要走参考图/视频输入而非本模式。
- tests/test_all_modes.py 断言本模式执行非空；三视图锚定路输出占位句。

## 节点映射

- 实现文件：aggregator/characters_master.py :: DirectorMasterCharacters.build()（ASSET_MODES 委托 + costume 路由）
- 分支/函数：aggregator/asset_master.py :: DirectorMasterAsset.build() `else:` 分支；设计指令 `_PROP_DESIGN["交通工具设计"]`
- 数据来源：核心数据包 _关键道具 + aggregator/scene_engine.parse_scene
