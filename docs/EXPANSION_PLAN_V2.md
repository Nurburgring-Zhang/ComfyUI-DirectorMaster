# 作品库二期补全详细计划 V2.0

> **执行者**: Mavis (MiniMax Code)
> **执行时间**: 2026-08-08
> **目标**: 100 部最新 IMDB 高分电影 + 1000 个短视频导演思维 5 层拆解
> **方法论**: 分阶段实施 + 模板化 + AI 辅助 + 质量抽检

---

## 0. 任务量级评估

| 维度 | 数量 | 字段数 | 总分析维度 |
|---|---|---|---|
| 电影 (最新 IMDB) | 100 部 | 14 维 | 1,400 维 |
| 短视频 (1000) | 1,000 部 | 14 维 | 14,000 维 |
| **合计** | **1,100 部** | **14 维** | **15,400 维** |

> 这是大型工程化任务,**必须分阶段、有标准、有验证、有质量控制**。

---

## 1. Phase A: 100 部最新 IMDB 高分电影

### 1.1 选片标准 (满足 4 项中至少 3 项)
1. **IMDB Top 250 排名** OR
2. **2020-2026 年发布** OR
3. **奥斯卡/BAFTA/金球奖/戛纳/威尼斯/柏林 提名或获奖** OR
4. **Metacritic 80+ / 烂番茄 90%+ / 豆瓣 8.0+**

### 1.2 候选清单 (150 部候选,最终选 100 部)
**已确认入选的 100 部**(按主题分组):

#### A1. 奥斯卡最佳影片/导演/摄影 (2020-2026)
- Nomadland (2020) 赵婷
- CODA (2021) Sian Heder
- The Power of the Dog (2021) Jane Campion
- Everything Everywhere All at Once (2022) Daniel Kwan/Daniel Scheinert
- Oppenheimer (2023) Christopher Nolan
- Poor Things (2023) Yorgos Lanthimos
- Anora (2024) Sean Baker
- The Brutalist (2024) Brady Corbet

#### A2. 奥斯卡提名最佳影片
- 1917 (2019) Sam Mendes
- Joker (2019) Todd Phillips
- The Irishman (2019) Martin Scorsese
- Once Upon a Time in Hollywood (2019) Quentin Tarantino
- Parasite (2019) Bong Joon-ho
- Jojo Rabbit (2019) Taika Waititi
- Little Women (2019) Greta Gerwig
- Ford v Ferrari (2019) James Mangold
- The Trial of the Chicago 7 (2020) Aaron Sorkin
- Mank (2020) David Fincher
- The Father (2020) Florian Zeller
- Judas and the Black Messiah (2021) Shaka King
- Don't Look Up (2021) Adam McKay
- Belfast (2021) Kenneth Branagh
- Drive My Car (2021) 滨口�的亮
- Licorice Pizza (2021) Paul Thomas Anderson
- The Banshees of Inisherin (2022) Martin McDonagh
- Women Talking (2022) Sarah Polley
- Tár (2022) Todd Field
- The Fabelmans (2022) Steven Spielberg
- All Quiet on the Western Front (2022) Edward Berger
- Triangle of Sadness (2022) Ruben Östlund
- Elvis (2022) Baz Luhrmann
- Top Gun: Maverick (2022) Joseph Kosinski
- Avatar: The Way of Water (2022) James Cameron
- The Whale (2022) Darren Aronofsky
- The Holdovers (2023) Alexander Payne
- Past Lives (2023) Celine Song
- Killers of the Flower Moon (2023) Martin Scorsese
- Anatomy of a Fall (2023) Justine Triet
- The Zone of Interest (2023) Jonathan Glazer
- May December (2023) Todd Haynes
- Dune: Part Two (2024) Denis Villeneuve
- The Substance (2024) Coralie Fargeat
- A Real Pain (2024) Jesse Eisenberg
- Conclave (2024) Edward Berger
- The Wild Robot (2024) Chris Sanders
- Flow (2024) Gints Zilbalodis
- September 5 (2024) Tim Fehlbaum
- Nickel Boys (2024) RaMell Ross

#### A3. 戛纳金棕榈/评审团大奖
- Parasite (2019) Bong Joon-ho [已列]
- Titane (2021) Julia Ducournau
- Triangle of Sadness (2022) [已列]
- Anatomy of a Fall (2023) [已列]
- Anora (2024) [已列]
- It Was Just an Accident (2025) Jafar Panahi
- The Last One for the Road (2025)

#### A4. 威尼斯金狮
- Joker (2019) [已列]
- Nomadland (2020) [已列]
- Happening (2021) Audrey Diwan
- All the Beauty and the Bloodshed (2022) Laura Poitras
- Poor Things (2023) [已列]
- The Room Next Door (2024) Pedro Almodóvar
- Father Mother Sister Brother (2025) Jim Jarmusch

#### A5. 柏林金熊
- Synonyms (2019) Nadav Lapid
- There Is No Evil (2020) Mohammad Rasoulof
- Bad Luck Banging or Loony Porn (2021) Radu Jude
- Alcarràs (2022) Carla Simón
- On the Adamant (2023) Nicolas Philibert
- Dahomey (2024) Mati Diop
- Living the Land (2025)

#### A6. 大片 (票房+口碑)
- Dune: Part One (2021) Denis Villeneuve [已列相关]
- No Time to Die (2021) Cary Joji Fukunaga
- Spider-Man: No Way Home (2021) Jon Watts
- The Batman (2022) Matt Reeves
- Black Panther: Wakanda Forever (2022) Ryan Coogler
- Nope (2022) Jordan Peele
- Glass Onion (2022) Rian Johnson
- Bullet Train (2022) David Leitch
- The Menu (2022) Mark Mylod
- Decision to Leave (2022) 朴赞郁
- Broker (2022) 是枝裕和
- Saint Omer (2022) Alice Diop
- Tar (2022) [已列]
- Showing Up (2022) Kelly Reichardt
- Aftersun (2022) Charlotte Wells
- Saint Omer (2022) [已列]
- Tár (2022) [已列]
- Pinocchio (2022) Guillermo del Toro
- The Banshees of Inisherin (2022) [已列]
- The Woman King (2022) Gina Prince-Bythewood
- Babylon (2022) Damien Chazelle
- Creed III (2023) Michael B. Jordan
- John Wick: Chapter 4 (2023) Chad Stahelski
- Spider-Man: Across the Spider-Verse (2023) Joaquim Dos Santos
- Oppenheimer [已列]
- Barbie (2023) Greta Gerwig
- Saltburn (2023) Emerald Fennell
- The Boy and the Heron (2023) 宫崎骏
- Perfect Days (2023) Wim Wenders
- Fallen Leaves (2023) Aki Kaurismäki
- The Taste of Mango (2023)
- La Chimera (2023) Alice Rohrwacher
- Priscilla (2023) Sofia Coppola
- Ferrari (2023) Michael Mann
- Napoleon (2023) Ridley Scott
- Wish (2023) Chris Buck/Fawn Veerasunthorn
- Society of the Snow (2023) J.A. Bayona
- The Teachers' Lounge (2023) İlker Çatak
- 20 Days in Mariupol (2023) Mstyslav Chernov
- Hit Man (2024) Richard Linklater
- Love Lies Bleeding (2024) Rose Glass
- Civil War (2024) Alex Garland
- Monkey Man (2024) Dev Patel
- Challengers (2024) Luca Guadagnino
- Furiosa (2024) George Miller
- Kingdom of the Planet of the Apes (2024) Wes Ball
- Alien: Romulus (2024) Fede Alvarez
- The Bikeriders (2024) Jeff Nichols
- Longlegs (2024) Oz Perkins
- MaXXXine (2024) Ti West
- It Ends with Us (2024) Justin Baldoni
- Beetlejuice Beetlejuice (2024) Tim Burton
- Joker: Folie à Deux (2024) Todd Phillips
- Megalopolis (2024) Francis Ford Coppola
- Anora (2024) [已列]
- The Brutalist (2024) [已列]
- September 5 (2024) [已列]

#### A7. 韩国/日本/中国/亚洲佳作
- Parasite (2019) [已列]
- The Handmaiden (2016) 朴赞郁 (虽然不是最新,但影史级)
- Burning (2018) 李沧东
- Shoplifters (2018) 是枝裕和
- Decision to Leave (2022) 朴赞郁 [已列]
- Broker (2022) 是枝裕和 [已列]
- 驾驶我的车 (Drive My Car, 2021) 滨口�的亮 [已列]
- The Boy and the Heron (2023) 宫崎骏 [已列]
- Perfect Days (2023) Wim Wenders [已列]
- Fallen Leaves (2023) Aki Kaurismäki [已列]
- Parasite (2019) [已列]
- 流浪地球 2 (2023) 郭帆
- 满江红 (2023) 张艺谋
- 长安三万里 (2023) 追光动画
- 消失的她 (2023) 崔睿/刘翔
- 封神第一部 (2023) 乌尔善
- 孤注一掷 (2023) 申奥
- 深海 (2023) 田晓鹏
- 长空之王 (2023) 刘晓世
- 第二十条 (2024) 张艺谋
- 志愿军 (2023) 陈凯歌
- 周处除三害 (2023) 黄精甫
- 默杀 (2024) 柯汶利
- 749 局 (2024) 陆川
- 抓娃娃 (2024) 闫非/彭大魔
- 逆行人生 (2024) 徐峥
- 749 局 (2024) 陆川
- 热辣滚烫 (2024) 贾玲
- 飞驰人生 2 (2024) 韩寒

#### A8. 经典电影补全 (2020 前)
为了保持 100 部质量,部分 2020 前顶级作品也补:
- The Father (2020) [已列]
- Mad Max: Fury Road (2015) George Miller
- 1917 (2019) [已列]
- 罗马 Roma (2018) Alfonso Cuarón
- 冷战 Cold War (2018) Paweł Pawlikowski

### 1.3 阶段拆分
- **A1**: 35 部奥斯卡提名获奖(已列 35-40 部)
- **A2**: 25 部三大电影节
- **A3**: 25 部大片/票房+口碑
- **A4**: 10 部亚洲+5 部补全
- **总计**: 95-105 部,根据质量筛选 100 部

### 1.4 数据格式
沿用现有 schema,每个电影包含:
```python
{
    "id": "dune_part_two",
    "title_cn": "沙丘:第二部",
    "title_en": "Dune: Part Two",
    "year": 2024,
    "director": "Denis Villeneuve",
    "director_key": "villeneuve",
    "genre": ["科幻", "史诗"],
    "rating_imdb": 8.6,
    "style_tags": [...],
    "visual_signature": "...",
    "key_scenes": [...],
    "narrative_structure": "...",
    "cultural_impact": "...",
    "prompt_seed": "...",
    "director_view": {  # 新增 14 维
        "logline": "...",
        "theme": "...",
        ...
    }
}
```

### 1.5 实施方式
- **方法 A (推荐)**: 我(Mavis)分批手动生成高质量 14 维 director_view
- **方法 B (辅助)**: 让 AI 协助生成草稿,我审核调整
- **质量标准**:
  - logline 必须 30-80 字,一句话核心冲突
  - theme 必须 3-5 个关键词
  - visual_palette 必须具体色名/材质
  - 14 维全部有内容,无 placeholder
- **分批**: 每次 20-25 部,跑测试,确认 OK 再下批

---

## 2. Phase B: 1000 个短视频

### 2.1 "短视频" vs "短剧" 区分
**短剧**(已有 16 部):60-90s 剧情化,1 集 1 反转,长剧集数
**短视频**(新 1000 部):15s-3min,**包括剧情/搞笑/知识/美食/萌宠/情感/带货/vlog/旅行/颜值/才艺/影视切片**等

### 2.2 1000 部品类分布 (按抖音/TikTok 实际生态)
| 品类 | 数量 | 说明 |
|---|---|---|
| **剧情号** (短剧+剧情切片) | 200 | 霸总/家庭/穿越/校园/职场 |
| **搞笑/整活** | 150 | 段子/反转/挑战/配音 |
| **知识科普** | 100 | 历史/科学/法律/财经/育儿 |
| **情感/励志** | 100 | 治愈/激励/情感故事/演讲 |
| **美食** | 80 | 教程/探店/家常/小吃 |
| **萌宠/动物** | 70 | 猫狗/搞笑动物/动物园 |
| **带货/直播切片** | 80 | 抖音带货/直播话术/产品 |
| **颜值/达人/模特** | 60 | 颜值号/达人/coser/换装 |
| **vlog/生活记录** | 50 | 日常/vlog/生活技巧 |
| **旅行/风景** | 50 | 旅行博主人设/风景号 |
| **影视/解说** | 50 | 电影解说/电视剧解说/解说号 |
| **才艺/二次元** | 30 | 唱歌/舞蹈/cos/手绘 |
| **TikTok 海外爆款** | 30 | 海外短视频 |
| **合计** | **1050** | 留 buffer |

### 2.3 实施方式 (关键!)
**1000 部 × 14 维手动写不现实**,必须分层:

#### B1. 模板化 (按品类 14 维)
每个品类写 1 个"模板 director_view",同一品类下:
- logline / theme / protagonist_arc / conflict_structure: **每部略不同** (代表作品)
- visual_palette / lighting_approach / pacing_signature: **基本相同** (品类特征)
- performance_direction: **基本相同** (品类表演)
- thematic_layers / philosophical_core: **基本相同** (品类主题)
- shot_sequence_analysis / why_it_works: **基本相同** (品类结构)
- direct_lessons / replication_template: **相同** (可复制)

#### B2. 代表作深写 (每品类 10-20 部)
每个品类挑 10-20 部真实爆款账号,手写完整 14 维 director_view。
例:
- 剧情号:家里家外/陈翔六点半/十八岁太奶奶/歪嘴龙王系列/重生之我是霸总/真假千金
- 搞笑号:papi 酱/朱一旦/陈翔六点半/多余和毛毛姐/疯产姐妹
- 知识号:无穷小亮/罗翔/混知/老番茄(知识区)/妈咪说
- 美食号:滇西小哥/绵羊料理/麻辣德子/食贫路
- 萌宠号:会说话的刘二豆/金毛蛋黄/沙雕动物
- 颜值号:刀小刀/summer/小蓝和他的朋友
- 旅行号:房琪/小小莎老师/谷岳
- 影视号:毒舌电影/谷阿莫/木鱼水心/刘哔电影
- TikTok:Khaby Lame / Charli D'Amelio / Addison Rae

#### B3. 模板批量 (每品类 50-150 部)
基于代表作的 director_view 模板,填入代表作品的不同:
- id (账号/作品 ID)
- title (账号/作品名)
- view_count / like_count (公开数据)
- 略不同的代表场景/具体内容

#### B4. 标签驱动 (1000 部快速归类)
每部都有 3-5 个 genre 标签,build_rich_reference 可以按 tag 聚合。

### 2.4 数据存储
**新建文件** `knowledge_base/works_viral_shorts.py`:
- 1000 部短视频
- 按品类分字典(便于查找)
- 同样 14 维 director_view
- 防重复注入逻辑

### 2.5 实施分批
- **B1 模板** (1-2 批):14 个品类 × 1 模板 = 14 套模板
- **B2 代表作** (3-4 批):每批 50 部深写 = 200 部
- **B3 批量** (5-8 批):基于模板批量生成,每批 100-150 部
- **总计 8-10 批**

---

## 3. 验证与质量控制

### 3.1 测试基线
- `test_full_audit.py`: 94/94 必须保持
- `test_e2e_full.py`: 115/115 必须扩展到 150+ 项
- `doctor.py`: 必须报告新作品库存在

### 3.2 质量抽检
- 随机抽 20 部(电影 5 + 短视频 15)人工校验
- 校验标准:
  - logline 准确概括故事
  - theme 不是空话,真有导演意图
  - visual_palette 具体到色彩/材质
  - philosophical_core 真的是哲学而非套话
  - 数据基于公开资料(评分/年份/导演)

### 3.3 数据真实性
- 电影:IMDB/豆瓣/MTC 数据可查
- 短视频:抖音/快手/B站/TikTok 公开榜单可查
- 不编造账号名,只用已知名账号 + 公开爆款

### 3.4 防止破坏
- 注入脚本必须有防重复逻辑
- 每次注入后跑测试
- 失败能回滚

---

## 4. 时间线 (估计)

| Phase | 任务 | 估计工作量 |
|---|---|---|
| A1 | 100 部电影 director_view 14 维 | 4-6 批 × 30 分钟 = 2-3 小时 |
| A2 | 注入 + 测试 | 30 分钟 |
| B1 | 短视频模板 (14 套) | 1 小时 |
| B2 | 代表作深写 (200 部) | 3-4 小时 |
| B3 | 批量生成 (800 部) | 2-3 小时 |
| B4 | 注入 + 测试 | 1 小时 |
| C1 | 质量抽检 + AUDIT 更新 | 1 小时 |
| **总计** | | **10-14 小时** |

> 这是大型工程化任务。考虑到 token 消耗,**分多次会话完成**,每次 2-3 小时。

---

## 5. 风险与缓解

| 风险 | 缓解 |
|---|---|
| 100 部电影 14 维数据量大 | 分批 20-25 部/批,跑测试 |
| 1000 短视频不可能手动写 | 模板化 + 批量生成 + 代表作深写 |
| 数据真实性 | 全部基于公开榜单/官方资料 |
| 测试不破 | 每批注入后跑测试,失败回滚 |
| 种子库兼容 | 复用 corpus_stats 聚合函数 |
| build_rich_reference 性能 | 1000+ 部聚合可能要优化 (目前 55 部已能秒级) |

---

## 6. 立即可执行项

按优先级排序:

1. **Phase A 立即开始**:100 部电影 director_view 14 维(高质量,慢工出细活)
2. **Phase B 模板先行**:先做 14 个品类的 14 维模板(质量高,可复用)
3. **Phase B 代表作**:每类 10-20 部深写
4. **Phase B 批量**:基于模板批量填充(质量中等)
5. **验证 + AUDIT 更新**

---

## 7. 结论

**这一期的核心目标**:
- 100 部电影:质量优先,每部都是真导演思维分析
- 1000 短视频:模板化保证基本盘 + 代表作深写保证质量上限
- **整体作品库从 55 部 → 1055 部**,AI 创作时的对标参考从 3-5 部扩到 30-50 部

**完成后,本项目将达到**:
- 电影对标:从 21 部扩到 121 部(覆盖近 100 年 IMDB Top)
- 电视剧对标:18 部(待二期扩展)
- 短剧对标:16 部 + 1000 短视频(覆盖抖音/TikTok 全生态)
- 短视频对标:从 0 → 1000(全品类覆盖)

**对标参考从"几个经典"变成"完整影视生态"**,这是 ComfyUI 节点能落地的关键。

---

**计划版本**: V2.0
**计划执行者**: Mavis
**下次评审**: 完成 Phase A 后
