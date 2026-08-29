---
mode_id: vibe-picture-book
node: DirectorMasterVibe
name: 绘本
one_liner: 接线 picture_book_pro 引擎, 输出年龄适配+分页绘本方案
applicable: [儿童绘本, 亲子内容, 教育动画]
intensity: high
style_tags: [分页结构, 年龄适配, 画面描述]
aliases: [绘本创作]
---

## 意图

要把故事变成可出版的分页绘本方案时选它：由 picture_book_pro 引擎产出年龄适配、逐页画面描述的完整结构。与"漫剧分镜"的本质差别：面向阅读的分页翻页节奏，不是面向画面的分格构图。

## 核心手法

1. 调用 picture_book_pro.PictureBookPro().build_book(场景描述/导演风格/情绪基调/启用反AI规则=True)，并透传 关键道具/_潜文本_情感/_导演意图_观众应感到。
2. 引擎返回 tuple 时取首元素；正文长度 >200 字符才采纳。
3. 引擎异常或输出过短时静默回退 _generic_vibe_template 通用分支（无绘本分页结构）。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 核心数据包 | 含 _关键道具/_潜文本_情感 的 JSON | 空包时引擎三个透传槽为空串，靠引擎内部缺省，画面与主题绑定变弱 |
| 导演风格 | 继承核心包（缺省 王家卫） | 影响引擎与【导演风格锚定】块两处 |
| 启用反AI规则 | True（节点开关） | 引擎调用恒传 True；节点开关只做输出二次清洗 |
| 情绪基调 | 继承核心包 _情绪基调（缺省 孤独） | 儿童题材忘改核心包时按"孤独"适配语气 |

## 已知坑

引擎失败走 except: pass 静默回退，stderr 无提示——正文出现"输出要求: 五感细节"即为回退信号（与 MV导演 共用同一回退分支，回退后无任何绘本分页结构）；目标年龄不由用户指定，由引擎内部适配。

## 节点映射

- 实现文件：aggregator/vibe_studio.py
- 分支/函数：TEMPLATES["绘本"] → _build_book_engine() → picture_book_pro.py :: PictureBookPro.build_book()（picture_book_pro.py:548）
- 数据来源：picture_book_pro 引擎内置年龄分页库 + 核心数据包透传字段
