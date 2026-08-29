---
mode_id: archive-version-commit
node: DirectorMasterArchive
name: 版本提交
one_liner: 全资产写盘并无条件提交版本, blob 去重加 gzip 加 20 版裁剪
applicable: [里程碑固化, 交付快照, 协作同步]
intensity: medium
style_tags: [版本控制, 增量存储, 全量资产]
aliases: [提交, commit]
---

## 意图

把 剧本/分镜/视频请求/制作手册/核心数据 五资产做成可回滚快照时选它。与 自动保存全部资产 同资产集, 差别: 无视 自动版本记录 开关恒提交版本, 语义是"这次必须进版本库"。

## 核心手法

1. 全量资产装配: assets=[(剧本,txt),(分镜,txt),(视频请求,json),(制作手册,txt),(核心数据,json)], 输入文本 非空时追加"附加文本"; 核心数据 写盘前剥离 _ai_api_key/_ai_api_url 明文键 (V13 修复 A-12)。
2. 无条件提交: commit 条件为 kind_to_file 非空 and (auto_commit or mode=="版本提交") — 本模式恒走右支; 版本名=版本名称 or 自动 v{order+1}, parent=当前 head。
3. 增量存储: version_store schema-2 按内容 sha256 入共享 blob 池, 版本间相同内容只存一份; 库文件 gzip 压缩 (.versions.json.gz), tmp+os.replace 原子替换, Windows PermissionError 重试 5 次。
4. 评分与裁剪: compute_archive_scores() 完整度=资产数/5、体量=字符/40000、total=0.6 完整度+0.4 体量; 超 MAX_VERSIONS=20 删最旧版本并回收其独占 blob, 指向被删版本的 tags 同步清除。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 版本名称 | 空 | 留空自动 vN; 撞名不报错 (id 由 时间戳+order长度盐 生成, 同毫秒并发不碰撞) |
| 版本标签 | final | 非空即 store.tag(vid, 标签); 同名标签指向最新提交, 旧指向被覆盖 |
| 核心数据包 | Core.核心数据包 | 非法 JSON 时按原文入库 (剥离逻辑只对可解析 dict 生效), 含密钥且解析失败时密钥照写盘 |
| 自动版本记录 | true | 对本模式无效 (恒提交); 关它只影响四个保存模式 |

## 已知坑

- 单资产 >2,000,000 字符截断存前 200 万并标 content_truncated — 回滚还原的是截断版, 超长部分不在版本库里。
- 版本库超 20 版本时最旧版本被删: 依赖旧版本回滚的流程要在 20 版内完成, 或先给关键版本打标签再继续提交。
- 库解压上限 200MB (防 zipbomb 类 OOM): 超限视为损坏重建空库, stderr 有提示但节点输出照常 — 大体量项目建议按项目名分库。
- tests/ten_rounds.py T7 断言: commit/tag/diff 可用、回滚逐字节 sha256 一致、单项目版本库 <2MB、8 线程×2 并发提交零丢失。

## 节点映射

- 实现文件：aggregator/archive_master.py
- 分支/函数：build() if mode in ("自动保存全部资产","版本提交") 资产装配段 + 密钥剥离段 + 版本控制段 commit 条件; aggregator/version_store.py :: VersionStore.commit()/_trim()/_mutate()/_save() + compute_archive_scores()
- 数据来源：上游五输入 + 版本库磁盘文件 <out_dir>/_versions/<项目>.versions.json.gz。
