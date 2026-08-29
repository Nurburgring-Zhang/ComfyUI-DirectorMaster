---
mode_id: vibe-comic-storyboard
node: DirectorMasterVibe
name: 漫剧分镜
one_liner: 接线 comic_drama_pro 输出 8 页×5 格日漫分镜方案
applicable: [漫剧, 条漫, 日式动画分镜]
intensity: high
style_tags: [分格分镜, 拟声词, 视线引导]
aliases: [漫画分镜, 漫剧]
---

## 意图

把故事画成日漫式分格剧本时选它：由 comic_drama_pro 引擎产出 8 页×5 格、含格框/对话框/拟声词/视线引导的逐格分镜。与"绘本"的本质差别：按格组织画面语言，翻页节奏服从格子张力而非阅读段落。

## 核心手法

1. 调用 comic_drama_pro.ComicDramaPro().build_comic(场景/导演/情绪基调 + 硬编码参数：漫剧风格="日漫分镜"、页数=8、每页格数=5、对白密度=0.5、拟声词使用=True)，透传 关键道具/_潜文本_情感/_导演意图。
2. 阅读方向从右至左（日漫口径），格框规整矩形+少量破格，线条中细 1-2px。
3. 引擎异常或输出 <200 字符时回退 _build_comic_template——固定 8 页演示模板（雨夜厨房/父亲/女儿/信/凤梨罐头）。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 核心数据包 | 含 _关键道具/_潜文本_情感 的 JSON | 空包时引擎透传槽为空串，格内道具与潜台词由引擎缺省填充 |
| 导演风格 | 继承核心包（缺省 王家卫） | 影响引擎与【导演风格锚定】块 |
| 情绪基调 | 继承核心包（缺省 孤独） | 传入引擎决定分格情绪走向 |
| 漫剧风格/页数/格数/对白密度 | 日漫分镜 / 8 / 5 / 0.5（实现内硬编码） | 非用户参数——下拉与核心包均改不了，需要其它风格要改代码 |

## 已知坑

引擎回退模板 _build_comic_template 是与输入场景无关的固定演示文本（厨房/信/凤梨罐头），tests/test_all_modes.py 的非空断言拦不住——正文出现"第1页·格1(全景): 厨房外景, 雨夜"即为回退信号；页数/格数/对白密度硬编码不可调。

## 节点映射

- 实现文件：aggregator/vibe_studio.py
- 分支/函数：TEMPLATES["漫剧分镜"] → _build_comic_engine() → comic_drama_pro.py :: ComicDramaPro.build_comic()（comic_drama_pro.py:40）；回退 _build_comic_template()
- 数据来源：comic_drama_pro 引擎内置分格语法库 + 核心数据包透传字段
