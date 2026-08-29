---
mode_id: archive-version-diff
node: DirectorMasterArchive
name: 版本对比
one_liner: 按标签或 id 前缀解析两版本, 输出字符差与文件级差异
applicable: [版本评审, 修改核对, 交付验收]
intensity: low
style_tags: [版本控制, 差异分析, 只读]
aliases: [diff, 对比]
---

## 意图

评审两版剧本/分镜改了什么时选它。与 版本历史 的差别: 输出是两版本间的结构化差异 (总字符差±/评分对比/文件级无变化-修改-新增-删除), 而非线性清单。

## 核心手法

1. 引用解析: 目标版本 默认 head; store.resolve_ref() 支持 标签名/完整 id/id 前缀 — 前缀命中多个版本时解析失败 (返回 None), 只有唯一命中才解析。
2. 基线回退: 对比基线 留空时取目标版本的 parent (提交时的上一 head), 即默认"和上一版比"。
3. 差异计算: store.diff() 按资产 kind 并集逐项比对 sha256 — 相同→无变化, 不同→已修改 (±字符差), 单侧存在→v2 中新增/已删除; 另给 总字符差 与 完整度/体量/total 评分对比。
4. 失败不抛错: 目标找不到 → "版本对比失败: 找不到目标版本 'X'"; 基线不存在 → 指明基线与目标 id。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 目标版本 | head | 空/填 head 都解析为当前 head; 前缀多义 (同毫秒双提交共享毫秒段前缀) → 报"找不到目标版本" |
| 对比基线 | 空 | 填不存在引用 → "版本对比失败: 基线版本 … 不存在 (目标 …)"; 填 head 时比较 head 与其 parent |
| 版本标签 | final | 与目标同填时 diff 先出报告, 随后对 目标版本(默认 head) 打标 — 报告尾部追加"已打标签"行, 对比与打标同次发生 |
| 项目名 | 我的项目 | 切库即切历史, 对比的是"这个项目名"的库 |

## 已知坑

- diff 只比 sha256 与字符数, 不做文本级行差异 — "已修改"只有 ±字符差, 想看逐行 diff 需回滚到临时目录自行比对。
- 引用解析顺序是 标签 → 完整 id → 前缀: 标签与版本 id 同名时标签优先。
- tests/ten_rounds.py T7 断言 commit/state/tag/diff 链路可用 (diff 非 None)。

## 节点映射

- 实现文件：aggregator/archive_master.py
- 分支/函数：build() elif mode == "版本对比" (resolve_ref/失败消息/diff 渲染) + 非保存模式打标段; aggregator/version_store.py :: VersionStore.resolve_ref()/diff()/tag()
- 数据来源：版本库 blobs (sha256) + 版本元数据 (scores/total_chars/parent)。
