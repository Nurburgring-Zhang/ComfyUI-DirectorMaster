---
mode_id: archive-version-rollback
node: DirectorMasterArchive
name: 版本回滚
one_liner: 还原版本文件并逐字节 sha256 校验, 回滚自动成新版本
applicable: [事故恢复, 方案回退, 版本管理]
intensity: medium
style_tags: [版本控制, 写盘还原, 不可变历史]
aliases: [回滚, rollback]
---

## 意图

把某个历史版本的资产恢复到磁盘时选它。与 版本对比 只读不同, 本模式真实写盘, 且回滚本身提交为新版本 — 历史不可变, 回滚是"新增一个还原版"而非抹掉后续版本。

## 核心手法

1. 目标必填: 目标版本 为空 → "版本回滚失败: 请填写 目标版本 (版本id/前缀/标签)", 不做任何写盘。
2. 逐字节还原: store.rollback(write=True) 每资产取 blob 内容 → 文件名取 basename 消毒 (V14.3 F4 防被篡改的版本库借回滚写任意路径) → 写入 out_dir → 回读文件算 sha256 与版本记录一致才计入还原清单。
3. 回滚即新版本: 还原后自动 commit "rollback→{原名}" (parent=当前 head, 携带 rollback_from 元数据), 回滚两次同一版本会产生两个递增的 rollback→ 版本。
4. 文件路径槽更新: 还原文件追加进第 3 路"文件路径"输出, 报告给出还原文件数。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 目标版本 | 版本id / 标签 / head | 缺失直接失败; 前缀多义解析失败报"找不到版本"; 支持标签 (如 gold) 间接定位 |
| 输出目录 | 空 | 还原落点是"本次运行的 out_dir", 不一定是当年保存目录 — 手动目录变了文件会出现在新位置 |
| 项目名 | 我的项目 | 决定从哪个库回滚; blob 缺失 (被裁剪回收) 的资产静默跳过不还原 |
| 自动版本记录 | true | 本模式不消费该参数 — 回滚必提交新版本, 无"只还原不提交"选项 |

## 已知坑

- 文件名消毒后为空或内容为空的条目跳过还原, 还原文件数可能小于版本登记资产数。
- sha256 回读校验失败的文件不计入还原清单但不报错 — 大体量资产还原后务必核对报告里的还原文件数。
- tests/ten_rounds.py T7 断言按标签回滚 (rollback("gold", write=True)) 后文件存在、还原数正确、sha256 与版本记录逐字节一致。

## 节点映射

- 实现文件：aggregator/archive_master.py
- 分支/函数：build() elif mode == "版本回滚" (目标必填校验 + restored 追加 file_paths); aggregator/version_store.py :: VersionStore.rollback() (basename 消毒 + sha256 回读校验 + "rollback→" commit)
- 数据来源：版本库 blob 池 (sha256 → 内容)。
