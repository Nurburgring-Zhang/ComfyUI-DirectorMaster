# -*- coding: utf-8 -*-
"""
⑦ DirectorMasterFinal — 终极汇总 (全链路终点)
================================================
直接使用上游Script.剧本和Cinematic.分镜的输出(不重建), 注入:
  - 导演锚定(1次) + Vibe主题前言
  - L1-L7七层结构化提示词(每镜7层)
  - 节拍表(Beat Table)
  - 张力曲线(Tension Curve)
  - 角色弧追踪(Arc Tracking)
  - 美术/声音/资产注入

slot0 剧本: 上游Script.剧本 + 导演锚定 + Vibe主题 + L1-L7 + 节拍表 + 张力曲线 + 角色弧
slot1 分镜脚本: 上游Cinematic.分镜 + 美术/声音注入 + L1-L7(每镜7层)
slot2 完整制作手册: 全能力汇总(去重复导演块)
slot3 JSON结构化数据: 干净结构化字段

AI双轨: 有AI→3个创意输出(剧本+分镜+手册)全走LLM原生; 无AI→模板输出零降级
"""
import os as _os, sys as _sys, json as _json
_HERE = _os.path.dirname(_os.path.abspath(__file__))
_PARENT = _os.path.dirname(_HERE)
if _PARENT not in _sys.path: _sys.path.insert(0, _PARENT)
if _HERE not in _sys.path: _sys.path.insert(0, _HERE)
from aggregator.node_base import DirectorNodeBase, parse_core_pack, resolve_ai_config, get_director_profile_text
from aggregator.pro_format import strip_decor, strip_director_block
from aggregator.scene_engine import parse_scene, generate_shots
from aggregator.prompt_layers import (build_all_layered_prompts, format_layered_prompts_text,
                                       build_beat_table, format_beat_table_text,
                                       build_tension_curve, format_tension_curve_text,
                                       build_arc_tracking, format_arc_tracking_text)


class DirectorMasterSummary(DirectorNodeBase):
    """V12.6 终极汇总节点 (V9.5 DirectorMasterFinal 重命名) — 直接使用上游输出, 注入L1-L7+节拍表+张力曲线+角色弧. 4 路输出: 剧本/分镜脚本/完整制作手册/JSON结构化数据."""
    NODE_TYPE = "终极汇总"
    OUTPUT_NODE = True

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "项目名": ("STRING", {"default": "我的电影项目"}),
        }, "optional": {
            "核心数据包": ("STRING", {"default": "", "multiline": True, "forceInput": True,
                "tooltip": "★ 必接 Core.核心数据包 — 灵魂/审美/风格/意图/AI配置 (AI自动从核心数据包继承, 无需重复填)"}),
            "剧本输出": ("STRING", {"default": "", "multiline": True, "forceInput": True,
                "tooltip": "★ 必接 Script.剧本 — 直接使用, 不重建"}),
            "创意输出": ("STRING", {"default": "", "multiline": True, "forceInput": True,
                "tooltip": "接 Vibe.创意 — 注入主题/概念"}),
            "美术输出": ("STRING", {"default": "", "multiline": True, "forceInput": True,
                "tooltip": "接 Art.美术 — 注入色彩/光影到分镜"}),
            "声音输出": ("STRING", {"default": "", "multiline": True, "forceInput": True,
                "tooltip": "接 Sound.声音 — 注入声轨到分镜"}),
            "分镜输出": ("STRING", {"default": "", "multiline": True, "forceInput": True,
                "tooltip": "接 Cinematic.分镜 — 直接使用, 不重建"}),
            "资产输出": ("STRING", {"default": "", "multiline": True, "forceInput": True,
                "tooltip": "接 Asset.资产设定 — 角色/环境/服化道卡"}),
            "角色输出": ("STRING", {"default": "", "multiline": True, "forceInput": True,
                "tooltip": "接 Characters.角色圣经 — 角色弧光追踪注入"}),
        }}

    RETURN_TYPES = ("STRING","STRING","STRING")
    RETURN_NAMES = ("完整制作手册","JSON交付包","项目索引")
    FUNCTION = "build"
    CATEGORY = "PromptLibrary/聚合/终点"

    def build(self, **kwargs):
        project = kwargs.get("项目名","我的电影项目")
        core = parse_core_pack(kwargs.get("核心数据包",""))
        script = kwargs.get("剧本输出","")  # 上游 Script.剧本(直接使用, 不重建)
        vibe = kwargs.get("创意输出","")
        art = kwargs.get("美术输出","")
        sound = kwargs.get("声音输出","")
        cine = kwargs.get("分镜输出","")  # 上游 Cinematic.分镜(直接使用, 不重建)
        asset = kwargs.get("资产输出","")
        chars_out = kwargs.get("角色输出","")

        # 从核心数据包读 32 字段
        director = core.get("_导演风格","王家卫") if core else "王家卫"
        scene = core.get("_场景描述","") if core else ""
        mood = core.get("_情绪基调","孤独") if core else "孤独"
        intent = core.get("_导演意图_观众应感到","心酸却温暖") if core else "心酸却温暖"
        project_core = core.get("_项目名", project) if core else project
        year = core.get("_时间年代","现代") if core else "现代"
        season = core.get("_季节","冬") if core else "冬"
        culture = core.get("_地区文化","中国都市") if core else "中国都市"
        platform = core.get("_平台媒介","院线长片") if core else "院线长片"
        audience = core.get("_目标受众","25-45岁都市") if core else "25-45岁都市"
        budget = core.get("_预算级别","中等制作") if core else "中等制作"
        runtime = core.get("_成片时长","90分钟") if core else "90分钟"
        aspect = core.get("_画幅比例","1.85:1 院线") if core else "1.85:1 院线"
        conflict = core.get("_核心冲突","家庭") if core else "家庭"
        theme = core.get("_主题词","孤独") if core else "孤独"
        visual = core.get("_视觉调性","梦幻") if core else "梦幻"
        subtext_strength = core.get("_潜文本强度","强") if core else "强"
        promise = core.get("_观众承诺","感动落泪") if core else "感动落泪"
        ref_films = core.get("_对标作品","") if core else ""
        props = core.get("_关键道具","") if core else ""

        # 导演锚定(只1次)
        director_anchor = ""
        dprof = get_director_profile_text(director)
        if dprof:
            director_anchor = f"【导演锚定】{director}\n{dprof}\n"

        # 生成 L1-L7 + 节拍表 + 张力曲线 + 角色弧
        parsed = parse_scene(scene)

        # V14.2 P0 修复: JSON 交付包的分镜表必须来自真实上游分镜 (此前用 generate_shots
        #        重建 30s 占位分镜, 与上游几百镜的真实分镜完全脱节 = 假数据)。
        upstream_shots = []
        shots_source = "(未连接上游分镜)"
        if cine:
            try:
                from aggregator.format_export import parse_shot_table as _parse_st
                upstream_shots = _parse_st(cine).get("shots", []) or []
                if upstream_shots:
                    shots_source = "上游 Cinematic.分镜 (真实交付)"
            except Exception:
                upstream_shots = []
        # L1-L7 层仍需 shot 对象列表 — 上游解析成功则用之, 否则用短片重建兜底 (仅层提示词用)
        rebuild_shots = generate_shots(parsed, director, mood)
        layered_shots = upstream_shots if upstream_shots else rebuild_shots
        layered = build_all_layered_prompts(layered_shots, director, scene, mood, intent, core)

        # V14.2: 节拍表/张力曲线用真实成片时长 (此前硬编码 30s)
        import re as _re_rt
        _rt_nums = _re_rt.findall(r"(\d+)", str(runtime))
        _rt_min = int(_rt_nums[0]) if _rt_nums else 90
        _total_sec = _rt_min * 60 if "秒" not in str(runtime) else int(_rt_nums[0])
        beat_table = build_beat_table(scene, director, mood, _total_sec)
        tension_curve = build_tension_curve(_total_sec, max(6, min(24, len(layered_shots) // 4 or 6)))
        character_names = parsed.get("characters", ["角色A","角色B"])
        arc_tracking = build_arc_tracking(character_names, mood)

        # === 唯一交付物: 完整制作手册 (制片人/客户/团队看的成片文档) ===
        manual = [
            f"═══════════════════════════════════════════════════════════",
            f"【完整制作手册】{project_core}",
            f"═══════════════════════════════════════════════════════════\n",
            f"【项目总览】",
            f"  导演: {director}",
            f"  场景: {scene}",
            f"  年代/季节/地区: {year} / {season} / {culture}",
            f"  平台/受众/预算: {platform} / {audience} / {budget}",
            f"  时长/画幅: {runtime} / {aspect}",
            f"  核心冲突/主题/视觉: {conflict} / {theme} / {visual}",
            f"  潜文本/观众承诺/观众应感到: {subtext_strength} / {promise} / {intent}",
            f"  对标作品: {ref_films}",
            f"  关键道具: {props}",
            f"\n" + "─"*40,
        ]

        # 一、导演总控
        manual.append(f"\n【一、导演总控·12 维风格档案】\n{director_anchor}")
        if core and core.get("统一电影提示词"):
            manual.append(f"\n【统一电影提示词】\n{strip_director_block(core['统一电影提示词'])}")

        # 二、创意/主题 (引用 Vibe)
        if vibe:
            manual.append(f"\n" + "─"*40 + f"\n【二、创意/主题/对标】\n{strip_director_block(vibe)}")

        # 三、剧本 (引用 Script 节点输出, 不重建)
        if script:
            manual.append(f"\n" + "─"*40 + f"\n【三、剧本】(引用 Script.剧本)\n{strip_director_block(script)}")
        else:
            manual.append(f"\n" + "─"*40 + f"\n【三、剧本】\n(未连接 Script.剧本 — 请连接剧本输出)")

        # 四、美术
        if art:
            manual.append(f"\n" + "─"*40 + f"\n【四、美术与视觉】\n{strip_director_block(art)}")

        # 五、声音
        if sound:
            manual.append(f"\n" + "─"*40 + f"\n【五、声音设计】\n{strip_director_block(sound)}")

        # 六、角色/资产
        if chars_out:
            manual.append(f"\n" + "─"*40 + f"\n【六、角色圣经】\n{strip_director_block(chars_out)}")
        if asset:
            manual.append(f"\n【六·补、角色/环境/服化道资产】\n{strip_director_block(asset)}")

        # 七、分镜 (引用 Cinematic 节点输出, 不重建)
        if cine:
            manual.append(f"\n" + "─"*40 + f"\n【七、画面/分镜】(引用 Cinematic.分镜)\n{strip_director_block(cine)}")
        else:
            manual.append(f"\n" + "─"*40 + f"\n【七、画面/分镜】\n(未连接 Cinematic.分镜)")

        # 八、节拍表
        manual.append(f"\n" + "─"*40 + f"\n【八、节拍表 (Beat Table)】\n{format_beat_table_text(beat_table)}")

        # 九、张力曲线
        manual.append(f"\n【九、张力曲线 (Tension Curve)】\n{format_tension_curve_text(tension_curve)}")

        # 十、角色弧追踪
        manual.append(f"\n【十、角色弧追踪 (Arc Tracking)】\n{format_arc_tracking_text(arc_tracking)}")

        # 十一、L1-L7 七层提示词 (每镜 7 层: 主体/动作/环境/光影/色彩/材质/声音)
        manual.append(f"\n" + "─"*40 + f"\n【十一、L1-L7 七层提示词 (每镜 7 层)】\n{format_layered_prompts_text(layered)}")

        # V14.3-MERGED: AIGC 影视全流程 42 环节 + 留白三定律 + 运镜三定律 (master_orchestrator 复活接线)
        try:
            from master_orchestrator import inject_42_stages, inject_3_whitespace, inject_3_camera_laws
            manual.append("\n" + inject_42_stages())
            manual.append("\n" + inject_3_whitespace())
            manual.append("\n" + inject_3_camera_laws())
        except Exception as _mo_e:
            import sys as _mo_s
            _mo_s.stderr.write(f"[DirectorMaster] 42环节/三定律注入降级: {type(_mo_e).__name__}\n")

        manual_text = "\n".join(manual)

        # === V12.6: Summary 节点纯汇总, 不做 AI 强化 ===
        # AI 强化已在 Script/Cinematic 节点完成 (整本剧本/分镜润色)
        # Summary 节点只引用上游已润色好的内容, 汇总成完整成片文档

        # === JSON 交付包 (程序解析用, 包含 32 字段项目信息 + 分镜 + 节拍 + 张力 + 弧) ===
        json_data = {
            "项目": {
                "项目名": project_core, "导演": director, "场景": scene,
                "年代/季节/地区": f"{year} / {season} / {culture}",
                "平台/受众/预算": f"{platform} / {audience} / {budget}",
                "时长/画幅": f"{runtime} / {aspect}",
                "核心冲突/主题/视觉": f"{conflict} / {theme} / {visual}",
                "潜文本强度/观众承诺": f"{subtext_strength} / {promise}",
                "对标作品": ref_films, "关键道具": props,
                "观众应感到": intent,
            },
            "分镜表来源": shots_source,
            "分镜表": (layered_shots if upstream_shots else
                       [{"镜号":s.get("n"),"阶段":s.get("stage"),"类型阶段":s.get("stage_name"),
                         "景别":s.get("size"),"角度":s.get("angle"),"运镜":s.get("move"),
                         "焦段":s.get("focal"),"时长":s.get("dur"),"画面焦点":s.get("focus"),
                         "声音":s.get("sound"),"色彩":s.get("stage_color",""),"光影":s.get("stage_light",""),
                         "材质":s.get("stage_material",""),"氛围":s.get("stage_atmosphere",""),
                         "情绪":s.get("stage_emotion",""),"转场":s.get("cut"),"叙事目的":s.get("purpose")} for s in layered_shots]),
            "节拍表": [{"拍":b["beat"],"入点":b["in_sec"],"出点":b["out_sec"],"阶段":b["stage"],
                        "情绪":b["emotion"],"强度":b["intensity"],"信息量":b["info_density"]} for b in beat_table],
            "张力曲线": [{"时间":c["time_sec"],"张力":c["tension"],"阶段":c["stage"]} for c in tension_curve],
            "角色弧": {name: [{"阶段":s["stage"],"状态":s["state"]} for s in stages] for name, stages in arc_tracking.items()},
            "L1L7分镜层": [{"镜号": i+1, "层": list(lp.keys()) if isinstance(lp, dict) else lp} for i, lp in enumerate(layered)],
            "上游摘要": {
                "剧本字数": len(script) if script else 0,
                "分镜字数": len(cine) if cine else 0,
                "创意字数": len(vibe) if vibe else 0,
                "美术字数": len(art) if art else 0,
                "声音字数": len(sound) if sound else 0,
                "角色字数": len(chars_out) if chars_out else 0,
                "资产字数": len(asset) if asset else 0,
            }
        }
        json_str = _json.dumps(json_data, ensure_ascii=False, indent=2)

        # === 项目索引 (头部摘要) ===
        index = (
            f"═══════════════════════════════════════════════════════════\n"
            f"【项目索引】{project_core}\n"
            f"═══════════════════════════════════════════════════════════\n"
            f"导演: {director} | 场景: {scene[:50]}{'...' if len(scene)>50 else ''}\n"
            f"年代: {year} | 季节: {season} | 地区: {culture}\n"
            f"平台: {platform} | 受众: {audience} | 预算: {budget}\n"
            f"时长: {runtime} | 画幅: {aspect}\n"
            f"核心冲突: {conflict} | 主题: {theme} | 视觉: {visual}\n"
            f"潜文本: {subtext_strength} | 观众承诺: {promise} | 观众应感到: {intent}\n"
            f"对标: {ref_films}\n"
            f"关键道具: {props}\n"
            f"═══════════════════════════════════════════════════════════\n"
            f"【成片指标】\n"
            f"分镜数: {len(layered_shots)} | 总时长: {sum(float(str((s.get('dur') or s.get('时长') or 0)).replace('s','') or 0) for s in layered_shots):.1f}s | 分镜来源: {shots_source}\n"
            f"剧本字数: {len(script) if script else 0} | 制作手册字数: {len(manual_text)}\n"
            f"═══════════════════════════════════════════════════════════"
        )

        return (manual_text, json_str, index)
