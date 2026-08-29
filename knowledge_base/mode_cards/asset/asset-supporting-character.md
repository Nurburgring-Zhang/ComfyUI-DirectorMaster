---
mode_id: asset-supporting-character
node: DirectorMasterAsset
name: 配角角色
one_liner: 生成侧面烘托主角的配角卡，绑定核心场景首个物件作情感外化
applicable: [AI漫剧, 竖屏微短剧, 短视频]
intensity: low
style_tags: [配角, 情感对照, 道具绑定]
aliases: [配角, 副线人物]
---

## 意图

给副线人物（亲人/挚友/对照组）建卡时选它。与主角模式的差别：叙事定位锁定"副线人物 — 侧面烘托主角, 承担情感对照功能"，其余走同一单角色分支，不继承姓名首位特判之外的特殊池。

## 核心手法

1. 叙事定位取 `_CHAR_ROLE_HINT["配角角色"]`。
2. 姓名继承：默认名"主角"且核心场景有人物→取解析首位（配角与主角共用首位继承，不会自动错开）。
3. 缺槽确定性补全：性格/外貌/服装走通用池（_PERSONA_TRAITS/_LOOK_TRAITS/_WARD_TRAITS）。
4. 道具绑定：核心物件或 _关键道具 首项写"出场必带"；三视图锚定 + 表情变体齐全。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 角色名 | 主角 | 留默认→与主角模式继承同一个首位角色，配角卡变主角复制；应显式填配角名 |
| 角色性格 | 留空走通用池 | 填值原样使用；留空→md5 种子从 _PERSONA_TRAITS 选 1 |
| 核心数据包 | Core 输出 JSON 包 | 不接→无道具绑定行，出场场景退化为"未指定" |
| 角色服装 | 留空走 _WARD_TRAITS | 本模式无时代衣冠池；需要古装配角应改用古风角色模式 |

## 已知坑

- 与主角模式取同一姓名继承首位：不显式填名时两张卡是同一人——配角与主角区分靠用户显式命名。
- _关键道具 绑定取 `split(",")[0].split("(")[0]`：逗号后第二件道具和括号内说明被截掉。

## 节点映射

- 实现文件：aggregator/asset_master.py
- 分支/函数：build() `mode in _CHARACTER_MODES` 单角色子分支；prop_bind 分支（core_objects[0] 或 key_props_core 首段）；`_CHAR_ROLE_HINT["配角角色"]`
- 数据来源：核心数据包→aggregator/scene_engine.py :: parse_scene；_关键道具 字符串解析
