---
mode_id: archive-save-script
node: DirectorMasterArchive
name: 保存剧本
one_liner: 剧本写盘 txt 加结构化 json, 场次对白按固定缩进真实解析
applicable: [剧本归档, 项目交付, 版本基线]
intensity: low
style_tags: [写盘归档, 结构化解析, 版本提交]
aliases: [归档剧本]
---

## 意图

只想把 Final.剧本 落盘留存时选它。与 自动保存全部资产 的差别: 只写剧本一个资产 (输入文本 可兜底), 版本评分完整度按 1/5 计, 版本库体积与增长最小。

## 核心手法

1. 资产装配: build() elif mode == "保存剧本" → assets=[("剧本", 剧本 or 输入文本, "txt")]; 剧本 为空时回退 输入文本, 两者皆空不写盘。
2. 多格式真实转换: 默认 保存格式 "TXT,JSON" 每资产写两份 — TXT 原文; JSON 走 format_export.parse_screenplay() 真实解析 (《标题》/导演: 元信息/INT.EXT.场景标题切场/对白三行式 12-10-8 空格缩进/〔潜文本/转场行), 产出 title/meta/scenes/场次数。
3. 文件命名: {项目名消毒}_{剧本}_{时间戳}.txt — _safe_name 把 \\/:*?"<>| 换下划线并截 40 字符, 空项目名回退"项目"。
4. 自动版本提交: 自动版本记录=true (默认) 时 commit 进 <输出目录>/_versions/<项目名>.versions.json.gz, 版本评分 完整度=1/5=0.2。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 剧本 | Final.剧本 (forceInput) | 空且 输入文本 也空 → 不写盘, 报告"(无资产输入, 未保存)"并提示连接输入 |
| 保存格式 | TXT,JSON | 非法项 (如 DOCX) 被 parse_formats 丢弃, 全非法回退 ["TXT"]; 改 "MD,HTML" 时剧本转 Markdown 场次标题加粗对白或内嵌 CSS 的 HTML |
| 项目名 | 我的电影项目 | 非法字符消毒截 40; 决定版本库文件名, 改名即切到另一版本库 |
| 自动版本记录 | true | false 且模式非"版本提交"时只写盘不 commit, 版本历史不增长 |

## 已知坑

- JSON 解析依赖 format_screenplay 固定缩进口径: 自由文本剧本解析出 scenes=[] (场次数 0), JSON 退化为只有元信息, 不报错。
- 写盘失败 (权限/路径) 时 _save 返回 "(保存失败: {e})" 字符串, 不计入已保存清单也不中断 — 报告里资产数可能为 0, 需看保存清单核实。
- tests/test_all_modes.py 以 tests/_archive_tmp 为输出目录真实执行本模式 (写盘回归)。

## 节点映射

- 实现文件：aggregator/archive_master.py
- 分支/函数：build() elif mode == "保存剧本" 资产装配段 + _save()/_safe_name() 写盘; 格式转换 aggregator/format_export.py :: parse_screenplay()/convert()/parse_formats()
- 数据来源：仅上游输入文本; 无内置数据库。
