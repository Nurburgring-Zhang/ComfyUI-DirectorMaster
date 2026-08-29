---
mode_id: archive-save-video-request
node: DirectorMasterArchive
name: 保存视频请求
one_liner: 视频请求 JSON 校验后嵌入结构化副本写盘, 非法时退分节
applicable: [API 请求归档, 复现生成, 版本基线]
intensity: low
style_tags: [写盘归档, JSON校验, 版本提交]
aliases: [归档视频请求]
---

## 意图

把 Router/VideoRouter 的 视频生成请求 payload 固化为可复现文件时选它。与另三个保存模式的差别: 扩展名固定 .json, 且 to_json 对已是 JSON 的内容先校验再原样嵌入 payload.data, 保留可 POST 的原始结构。

## 核心手法

1. 资产装配: assets=[("视频请求", 视频请求 or 输入文本, "json")]; 默认保存格式 TXT,JSON → 写 原文 txt 副本 + 结构化 json 副本。
2. JSON 校验嵌入: format_export.to_json() 对以 { 或 [ 开头的内容先 json.loads 校验, 成功则 {"项目","资产类型","字符数","data":原始对象} 整体落盘; 校验失败不抛错, 转 split_sections 分节结构 (format 记 "sections")。
3. 自动版本提交: commit 的 files 登记第一成功格式文件名, 内容按原文一份进 blob 池 (sha256 去重 — 同一 payload 反复归档不重复占库)。
4. 元数据槽记录 模式/输出目录/已保存文件, 提交成功时 manifest["版本"] 带版本 id。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 视频请求 | Router.视频生成请求 (forceInput) | 空 → 回退 输入文本; 全空不写盘报"无可保存资产" |
| 输入文本 | 空 | 兜底资产源; 手填 JSON 字符串同样走校验嵌入 |
| 保存格式 | TXT,JSON | JSON 项校验失败退 sections 时仍写 .json 扩展名, 内容是分节对象而非原始 payload — 看 "format" 键辨别 |
| 项目名 | 我的电影项目 | 决定 blob 归属库; 消毒截 40 字符 |

## 已知坑

- 非法 JSON 静默转 sections 结构, 无错误码; 需要检查输出里 "data" 键存在性来确认嵌入成功。
- payload 内若已含 AI 密钥类字段不会被清洗 — 核心数据包的 _ai_api_key 剥离只作用于"核心数据"资产 (V13 修复 A-12 范围), 本模式原文照存。
- 版本内容单资产上限 2,000,000 字符, 超限截断并标 content_truncated, 版本库里只存前 200 万字符。

## 节点映射

- 实现文件：aggregator/archive_master.py
- 分支/函数：build() elif mode == "保存视频请求" + _save(); JSON 校验分支 aggregator/format_export.py :: to_json() 首段 (stripped.startswith("{") → json.loads → 失败转 sections)
- 数据来源：仅上游 payload 文本; 无内置数据库。
