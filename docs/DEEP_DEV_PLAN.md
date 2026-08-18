# 深度铺开开发计划 V2 (Expert-Level Completion)

## 目标
完成4个模块的7维决策树金标准铺开,零虚假实现,每条目含真实专家级决策字段。

## 阶段划分

### Phase 1: director_styles 剩余36位导演
DIRECTOR_DECISION 覆盖层,每位补 trigger/failure_modes/measurement/alternatives。
- 经典/艺术(13): chaplin, billy_wilder, orson_welles, john_ford, david_lean, bergman, fellini, tarkovsky, ozu, de_palma, michael_mann, polanski, sergio_leone
- 当代(11): coen_brothers, pt_anderson, darren_aronofsky, alejandro_inarritu, alfonso_cuaron, guillermo_del_toro, damien_chazelle, frank_darabont, robert_zemeckis, james_cameron, fernando_meirelles
- 亚洲(6): chen_kaige, hou_hsiao_hsien, johnnie_to, satoshi_kon, makoto_shinkai, lee_changdong
- 短剧/新媒体(6): duanmu_rong, jiang_shiqi, liu_xunzimo, sam_kolder, brandon_li, terrence_malick

### Phase 2: performance_system 剩余子模块
- basic 9微表情: PERFORMANCE_BASIC_DECISION 覆盖层(trigger/failure/measurement/alternatives/cross_refs)
- body_language/laban_efforts/character_interactions/world_interaction/character_archetypes/movement_phrases/group_choreography: PERFORMANCE_DECISION 覆盖层(按key)

### Phase 3: transition_grammar 剩余
- advanced_montage 4条 → 内联7维重写
- viral_transition_full 10条 → 从字符串转为7维dict
- transition_quickmap → 已有结构,补决策说明(可选)

### Phase 4: viral_video 剩余
- visual_storytelling 3 / engagement_triggers 3 / content_categories 5 / platform_optimization 3 / ai_video_specifics 3
→ VIRAL_VIDEO_DECISION 扩展(已11条,补17条)

### Phase 5: 双AI互审 (Workflow)
fan-out review agents 对每模块抽样验证: 7维完整/非虚假/跨引用一致/引擎注入路径

### Phase 6: 代码审核+落地测试+自审迭代
- py_compile 全文件
- import 全模块
- 节点加载(mock torch/numpy/PIL)
- 端到端深度注入完整性测试(20+章节)
- 多轮自审: grep语法错误/字典括号匹配/覆盖层合并函数

## 每阶段自我质疑
- 这条目是否真实专家级? (非占位/非重复)
- failure_modes是否是该技法的真实陷阱? (非泛泛)
- measurement是否可验收? (非模糊)
- 引擎是否真正使用? (注入路径打通, 非死数据)
