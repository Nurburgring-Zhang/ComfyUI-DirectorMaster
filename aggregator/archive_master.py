# -*- coding: utf-8 -*-
"""
⑨ DirectorMasterArchive — 归档终态 (真实存盘 + 版本控制)
================================================
真正保存各阶段产出资产到磁盘 (ComfyUI output 目录 / fallback 本地 output).
不再只格式化文本 — 接收 剧本/分镜/视频请求/制作手册/核心数据包, 写盘保存.

模式:
  - 自动保存全部资产 (默认): 把 剧本/分镜/视频请求/制作手册/JSON/EDL 全部写盘
  - 保存剧本 / 保存分镜 / 保存视频请求 / 保存制作手册
  - 资产清单: 列出已保存文件
  - V14.2 版本控制 (真实磁盘持久化, 修复能力降级 — 此前仅 legacy 内存版):
    版本提交 / 版本历史 / 版本对比 / 版本回滚 / 最优版本
    每次保存类归档自动提交版本 (可关), 版本库存于 <输出目录>/_versions/.
"""
import os as _os, sys as _sys, json as _json, time as _time
_HERE = _os.path.dirname(_os.path.abspath(__file__))
_PARENT = _os.path.dirname(_HERE)
if _PARENT not in _sys.path: _sys.path.insert(0, _PARENT)
if _HERE not in _sys.path: _sys.path.insert(0, _HERE)
from aggregator.node_base import DirectorNodeBase, parse_core_pack, resolve_ai_config

ARCHIVE_MODES = ["自动保存全部资产","保存剧本","保存分镜","保存视频请求","保存制作手册","资产清单",
                 "版本提交","版本历史","版本对比","版本回滚","最优版本"]
_SAVE_MODES = {"自动保存全部资产","保存剧本","保存分镜","保存视频请求","保存制作手册"}


def _get_output_dir():
    """获取 ComfyUI 输出目录 (folder_paths), fallback 到本地 output."""
    try:
        import folder_paths
        out = folder_paths.get_output_directory()
        if out and _os.path.isdir(_os.path.dirname(out) or out):
            _os.makedirs(out, exist_ok=True)
            return out
    except Exception:
        pass
    # fallback: 项目同级 output 目录
    out = _os.path.join(_PARENT, "output")
    _os.makedirs(out, exist_ok=True)
    return out


def _safe_name(s):
    import re as _re
    s = _re.sub(r'[\\/:*?"<>|]', "_", s or "项目")
    return s.strip()[:40] or "项目"


def _save(out_dir, project, kind, content, ext="txt"):
    """保存一个资产文件, 返回相对路径."""
    if not content:
        return None
    ts = _time.strftime("%Y%m%d_%H%M%S")
    fname = f"{_safe_name(project)}_{kind}_{ts}.{ext}"
    path = _os.path.join(out_dir, fname)
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return fname
    except Exception as e:
        return f"(保存失败: {e})"


class DirectorMasterArchive(DirectorNodeBase):
    """归档终态 — 真实保存各阶段产出资产."""
    OUTPUT_NODE = True

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "归档模式": (ARCHIVE_MODES, {"default": "自动保存全部资产"}),
            "项目名": ("STRING", {"default": "我的电影项目"}),
        }, "optional": {
            "核心数据包": ("STRING", {"default": "", "multiline": True, "forceInput": True,
                "tooltip": "接 Core.核心数据包 — 用于元数据/导演信息"}),
            "剧本": ("STRING", {"default": "", "multiline": True, "forceInput": True,
                "tooltip": "接 Final.剧本 — 保存为剧本文件"}),
            "分镜脚本": ("STRING", {"default": "", "multiline": True, "forceInput": True,
                "tooltip": "接 Final.分镜脚本 — 保存为分镜文件"}),
            "视频请求": ("STRING", {"default": "", "multiline": True, "forceInput": True,
                "tooltip": "接 Router.视频生成请求 — 保存为API payload JSON"}),
            "制作手册": ("STRING", {"default": "", "multiline": True, "forceInput": True,
                "tooltip": "接 Final.完整制作手册 — 保存为手册文件"}),
            "输入文本": ("STRING", {"default": "", "multiline": True, "tooltip": "可选: 额外文本"}),
            "输出目录": ("STRING", {"default": "", "multiline": False,
                "tooltip": "★ V13.2: 手动指定归档目录 (绝对/相对路径均可, 自动创建)。留空 = ComfyUI output 目录, 再 fallback 到插件目录/output"}),
            "保存格式": ("STRING", {"default": "TXT,JSON", "multiline": False,
                "tooltip": "★ V14.2: 保存格式多选 — TXT/JSON/MD/HTML (逗号分隔)。TXT=原文; JSON=结构化解析(剧本→场次对象/分镜→逐镜对象); MD=Markdown; HTML=完整样式文档"}),
            "自动版本记录": ("BOOLEAN", {"default": True,
                "tooltip": "V14.2: 每次保存类归档自动提交一个版本 (磁盘持久化, 可回滚/对比/选优)"}),
            "版本名称": ("STRING", {"default": "", "tooltip": "V14.2: 版本名 (留空自动编号 vN)"}),
            "目标版本": ("STRING", {"default": "",
                "tooltip": "V14.2: 版本对比/回滚/打标签的目标 — 版本id、id前缀、标签名 或 head"}),
            "对比基线": ("STRING", {"default": "",
                "tooltip": "V14.2: 版本对比的基线版本 (留空=目标版本的上一个版本)"}),
            "版本标签": ("STRING", {"default": "", "tooltip": "V14.2: 给目标版本打标签 (如 final/交付版)"}),
            "版本备注": ("STRING", {"default": "", "multiline": True, "tooltip": "V14.2: 版本备注"}),
            "AI接口地址": ("STRING", {"default": "", "tooltip": "留空=继承Core AI; 填写=覆盖"}),
            "AI密钥": ("STRING", {"default": ""}),
            "AI模型名": ("STRING", {"default": ""}),
        }}

    RETURN_TYPES = ("STRING","STRING","STRING","STRING","STRING")
    RETURN_NAMES = ("保存清单","元数据","文件路径","版本历史","报告")
    FUNCTION = "build"
    CATEGORY = "PromptLibrary/聚合/归档"

    def build(self, **kwargs):
        from aggregator.version_store import open_store, compute_archive_scores
        mode = kwargs.get("归档模式","自动保存全部资产")
        if mode not in ARCHIVE_MODES: mode = "自动保存全部资产"
        core = parse_core_pack(kwargs.get("核心数据包",""))
        project = kwargs.get("项目名","我的电影项目")
        director = core.get("_导演风格","") if core else ""
        scene = core.get("_场景描述","") if core else ""

        script = kwargs.get("剧本","")
        storyboard = kwargs.get("分镜脚本","")
        video_req = kwargs.get("视频请求","")
        manual = kwargs.get("制作手册","")
        extra = kwargs.get("输入文本","")

        # V13.2: 手动输出目录优先 — 填写则用之(自动创建), 留空走 ComfyUI output / fallback
        custom_dir = (kwargs.get("输出目录","") or "").strip()
        out_dir = ""
        dir_note = ""
        if custom_dir:
            try:
                cand = _os.path.expandvars(_os.path.expanduser(custom_dir))
                if not _os.path.isabs(cand):
                    cand = _os.path.abspath(cand)
                _os.makedirs(cand, exist_ok=True)
                if _os.path.isdir(cand):
                    out_dir = cand
                    dir_note = "手动指定"
            except Exception as e:
                dir_note = f"手动目录不可用({e}), 已回退默认"
        if not out_dir:
            out_dir = _get_output_dir()
            dir_note = dir_note or "默认"
        saved = []

        # V14.2: 版本库 (磁盘持久化)
        store = open_store(out_dir, project)
        v_notes = (kwargs.get("版本备注","") or "").strip()
        v_tag = (kwargs.get("版本标签","") or "").strip()

        # 各模式的保存动作
        assets = []  # (kind, content, ext)
        # V13 修复 (A-12): 写盘前剥离核心数据包中的明文 AI 密钥
        _core_pack_raw = kwargs.get("核心数据包", "")
        try:
            _cp = _json.loads(_core_pack_raw) if _core_pack_raw else {}
            if isinstance(_cp, dict):
                _cp.pop("_ai_api_key", None)
                _cp.pop("_ai_api_url", None)
                _core_pack_safe = _json.dumps(_cp, ensure_ascii=False, indent=2)
            else:
                _core_pack_safe = _core_pack_raw
        except Exception:
            _core_pack_safe = _core_pack_raw
        if mode in ("自动保存全部资产", "版本提交"):
            assets = [("剧本", script, "txt"), ("分镜", storyboard, "txt"),
                      ("视频请求", video_req, "json"), ("制作手册", manual, "txt"),
                      ("核心数据", _core_pack_safe, "json")]
            if extra: assets.append(("附加文本", extra, "txt"))
        elif mode == "保存剧本":
            assets = [("剧本", script or extra, "txt")]
        elif mode == "保存分镜":
            assets = [("分镜", storyboard or extra, "txt")]
        elif mode == "保存视频请求":
            assets = [("视频请求", video_req or extra, "json")]
        elif mode == "保存制作手册":
            assets = [("制作手册", manual or extra, "txt")]
        else:  # 资产清单 / 版本历史 / 版本对比 / 版本回滚 / 最优版本
            assets = []

        # V14.2: 保存格式多选 — 每个资产按所选格式逐一真实转换写盘
        from aggregator.format_export import parse_formats, convert
        fmts = parse_formats(kwargs.get("保存格式", "TXT,JSON"))

        kind_to_file = {}  # kind -> (filename, content) 供版本提交 (内容只存一份原文)
        for kind, content, _ext in assets:
            if not content:
                continue
            first_fname = None
            for fmt in fmts:
                converted, cext = convert(content, fmt, kind, project)
                fname = _save(out_dir, project, kind, converted, cext)
                if fname and not str(fname).startswith("(保存失败"):
                    saved.append(fname)
                    if first_fname is None:
                        first_fname = fname
            if first_fname:
                kind_to_file[kind] = (first_fname, content)

        file_paths = "\n".join(f"{out_dir}/{f}" for f in saved)
        manifest = {
            "项目": project, "导演": director, "场景": scene, "模式": mode,
            "时间": _time.strftime("%Y-%m-%d %H:%M:%S"), "输出目录": out_dir,
            "目录来源": dir_note, "保存格式": fmts,
            "已保存文件": saved,
            "资产数": len(saved),
        }

        # ============ V14.2 版本控制分支 ============
        version_report = ""
        if mode in _SAVE_MODES or mode == "版本提交":
            auto_commit = bool(kwargs.get("自动版本记录", True))
            if kind_to_file and (auto_commit or mode == "版本提交"):
                total_chars = sum(len(c) for _, c in kind_to_file.values())
                scores = compute_archive_scores(list(kind_to_file.keys()), total_chars)
                vname = (kwargs.get("版本名称","") or "").strip() or f"v{len(store.data['order']) + 1}"
                vid = store.commit(
                    name=vname,
                    files=kind_to_file,
                    metadata={"模式": mode, "导演": director, "目录来源": dir_note},
                    scores=scores,
                    notes=v_notes,
                )
                if v_tag:
                    store.tag(vid, v_tag)
                version_report = f"已提交版本 {vid} ({vname}) | 资产{len(kind_to_file)}项 {total_chars}字符 | total={scores['total']}"
                manifest["版本"] = vid
        elif mode == "版本历史":
            log = store.log(limit=20)
            lines = [f"【版本历史】{project} | 共 {len(store.data['order'])} 个版本 | 版本库: {store.path}"]
            if not log:
                lines.append("(暂无版本 — 请先执行 保存/版本提交)")
            for v in log:
                sc = v.get("scores", {})
                files_s = "/".join(v.get("files", {}).keys())
                lines.append(f"  · [{v['state']}] {v['name']} ({v['id']})")
                lines.append(f"      {v['timestamp']} | 资产: {files_s} | {v.get('total_chars',0)}字符 | total={sc.get('total','N/A')}")
                if v.get("notes"):
                    lines.append(f"      备注: {v['notes']}")
            version_report = "\n".join(lines)
        elif mode == "版本对比":
            target_ref = (kwargs.get("目标版本","") or "").strip() or "head"
            base_ref = (kwargs.get("对比基线","") or "").strip()
            t_vid = store.resolve_ref(target_ref)
            if not t_vid:
                version_report = f"版本对比失败: 找不到目标版本 '{target_ref}'"
            else:
                if not base_ref:
                    base_ref = (store.get(t_vid) or {}).get("parent") or ""
                d = store.diff(base_ref, t_vid) if base_ref else None
                if not d:
                    version_report = f"版本对比失败: 基线版本 '{base_ref or '(无)'}' 不存在 (目标 {t_vid})"
                else:
                    lines = [f"【版本对比】{project}",
                             f"  v1: {d['v1']['name']} ({d['v1']['id']}) {d['v1']['time']} [{d['v1']['state']}]",
                             f"  v2: {d['v2']['name']} ({d['v2']['id']}) {d['v2']['time']} [{d['v2']['state']}]",
                             f"  总字符差: {d['总字符差']:+d}"]
                    for k, (s1, s2) in d["评分对比"].items():
                        lines.append(f"  评分 {k}: {s1} → {s2}")
                    for fd in d["文件级差异"]:
                        lines.append(f"  文件 {fd['资产']}: {fd['变化']}" +
                                     (f" ({fd.get('字符差', 0):+d}字符)" if "字符差" in fd else ""))
                    version_report = "\n".join(lines)
        elif mode == "版本回滚":
            target_ref = (kwargs.get("目标版本","") or "").strip()
            if not target_ref:
                version_report = "版本回滚失败: 请填写 目标版本 (版本id/前缀/标签)"
            else:
                new_vid, restored = store.rollback(target_ref, write=True)
                if new_vid:
                    saved.extend(restored)
                    file_paths = "\n".join(f"{out_dir}/{f}" for f in saved)
                    version_report = f"已回滚 '{target_ref}' → 新版本 {new_vid} | 还原文件 {len(restored)} 个: {', '.join(restored) or '(无内容)'}"
                else:
                    version_report = f"版本回滚失败: 找不到版本 '{target_ref}'"
        elif mode == "最优版本":
            best = store.best(score_key="total", top_n=5)
            lines = [f"【最优版本】{project} | 按 total 评分排序 (评分=完整度60%+体量40%, 全部来自真实归档数据)"]
            if not best:
                lines.append("(暂无带评分版本 — 请先执行 保存/版本提交)")
            for rank, (s, v) in enumerate(best, 1):
                lines.append(f"  {rank}. {v['name']} ({v['id']}) total={s} | 资产{'/'.join(v.get('files', {}).keys())} | {v['timestamp']}")
            version_report = "\n".join(lines)

        # 打标签 (任何模式下提供 版本标签+目标版本 都可打标)
        if v_tag and mode not in _SAVE_MODES and mode != "版本提交":
            t_ref = (kwargs.get("目标版本","") or "").strip() or "head"
            t_vid = store.resolve_ref(t_ref)
            if t_vid:
                store.tag(t_vid, v_tag)
                version_report += f"\n已打标签: {v_tag} → {t_vid}"

        metadata = _json.dumps(manifest, ensure_ascii=False, indent=2)

        if mode == "资产清单":
            all_files = []
            try:
                all_files = sorted(f for f in _os.listdir(out_dir)
                                   if _os.path.isfile(_os.path.join(out_dir, f)) and not f.endswith(".tmp"))
            except Exception:
                pass
            main = f"【资产清单】{project}\n目录: {out_dir} ({dir_note})\n共 {len(all_files)} 个文件:\n" + \
                   ("\n".join(f"  · {f}" for f in all_files) if all_files else "(空)")
            report = f"归档报告: 资产清单 — {len(all_files)} 个文件"
        elif not saved and mode in _SAVE_MODES:
            main = f"【保存清单】{project}\n目录: {out_dir} ({dir_note})\n(无资产输入, 未保存)\n模式: {mode}"
            report = f"归档报告: {mode} — 无可保存资产\n提示: 请连接 剧本/分镜/视频请求/制作手册 输入"
        elif mode in _SAVE_MODES or mode == "版本提交":
            main = f"【保存清单】{project}\n模式: {mode}\n已保存 {len(saved)} 个资产:\n" + "\n".join(f"  · {f}" for f in saved)
            report = f"归档报告: {mode} — 成功保存 {len(saved)} 个资产到 {out_dir} ({dir_note})"
        else:
            main = version_report or f"【{mode}】{project}\n(无操作结果)"
            report = f"归档报告: {mode} 完成"

        # V14.2: 版本历史输出 — 真实持久化日志 (替代此前伪造的单行 v1.0)
        _last5 = store.log(limit=5)
        if _last5:
            history = f"版本库: {store.path}\nhead: {store.data.get('head')}\n最近 {len(_last5)} 个版本:\n" + \
                      "\n".join(f"  [{v['state']}] {v['name']} ({v['id']}) {v['timestamp']} total={v.get('scores',{}).get('total','N/A')}"
                                for v in _last5)
            if version_report and mode not in _SAVE_MODES:
                history = version_report + "\n\n" + history
        else:
            history = version_report or "(版本库为空 — 保存资产时自动记录版本)"
        if version_report and mode in _SAVE_MODES:
            main += f"\n\n【版本控制】{version_report}"

        # AI 增强 (可选: 整理报告)
        api_url, api_key, ai_model = resolve_ai_config(kwargs, core)
        if api_url and main:
            main = self._ensure_ai_output(main,
                {"node_type":"终极汇总","mode":mode,"director":director or "王家卫","scene":scene,"intent":core.get("_导演意图_观众应感到","") if core else ""},
                api_url, api_key, ai_model)

        return (main, metadata, file_paths, history, report)
