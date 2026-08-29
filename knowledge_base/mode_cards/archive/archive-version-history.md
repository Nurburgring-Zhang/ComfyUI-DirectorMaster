---
mode_id: archive-version-history
node: DirectorMasterArchive
name: 版本历史
one_liner: 读版本库列最近 20 版状态与评分, 空库诚实提示先提交
applicable: [版本审计, 回滚前核对, 协作同步]
intensity: low
style_tags: [版本控制, 只读, 审计]
aliases: [历史, log]
---

## 意图

回滚/对比前先看库里有什么时选它。与 资产清单 的差别: 读的是版本库 (gzip JSON) 而非目录文件, 输出带 state/评分/备注的结构化版本行。

## 核心手法

1. 最近 20 版倒序: build() elif mode == "版本历史" → store.log(limit=20), 每版两行 — "[state] name (id)" 与 "timestamp | 资产kinds | 字符数 | total | 备注"; 头行带 共 N 版 与版本库绝对路径。
2. 空库诚实: log 空时输出 "(暂无版本 — 请先执行 保存/版本提交)", 不伪造历史。
3. 双槽输出: 第 1 槽 main 是完整 20 版清单; 第 4 槽"版本历史"恒输出 版本库路径/head/最近 5 版 (所有模式共有该槽)。
4. 兼容迁移: 打开库时自动把旧 schema-1 明文 .versions.json 升级为 schema-2 blob 去重格式, 内容逐字节保留。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 项目名 + 输出目录 | 我的项目 / 空 | 二者共同决定版本库路径 <输出目录>/_versions/<项目消毒>.versions.json.gz — 任何一处改动都会"查不到历史", 先核对元数据槽的版本库路径 |
| 版本备注 | 空 | 本模式不写库, 备注只在保存/提交时入库; 历史行的备注来自当时提交 |
| 核心数据包 | 空 | 仅影响元数据与 AI 轨; 版本库定位与其无关 |

## 已知坑

- 版本 state 提交时恒为 DRAFT, 本节点没有改 state 的模式 (set_state 只在库 API 层) — 历史里见到的 REVIEW/APPROVED 等状态是外部工具写入的。
- 旧 schema-1 库超过 200MB 跳过迁移按空库处理 (stderr 提示), 历史突然"清零"先查 stderr 而不是重新提交。
- gzip 解压上限 200MB, 超限视为损坏重建空库 — 与 版本提交 共享同一容量边界。

## 节点映射

- 实现文件：aggregator/archive_master.py
- 分支/函数：build() elif mode == "版本历史" (log limit=20 + 空库提示); aggregator/version_store.py :: VersionStore.log()/_load()/_migrate_v1()
- 数据来源：<out_dir>/_versions/<项目>.versions.json.gz (schema-2) 或 legacy .versions.json。
