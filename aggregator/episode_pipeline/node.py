# -*- coding: utf-8 -*-
"""
aggregator/episode_pipeline/node.py — ComfyUI 节点: DirectorMasterNovelIntake
(批次7 WaveB builder-e3, 长篇输入管线第 19 个注册节点)
================================================================================
长篇小说 → 分集产物: 章节感知切分 + 覆盖账本 Σ 校验 + 锚点回溯 + 三指标钩子
+ 断点续跑 (CheckpointStore) + dm_memory 记忆桥。

范本: aggregator/review_engine.py DirectorMasterReview (V16.7 批次3 D6) —
同款 INPUT_TYPES/RETURN_TYPES/FUNCTION/CATEGORY 结构与 try-except 诚实上报。

纪律:
  · run_intake 方法内惰性导入 (模块顶层不 import pipeline/ComfyUI), 裸 python
    导入本包不崩;
  · 输出目录运行时兜底: ComfyUI folder_paths.get_output_directory() 优先
    (函数内惰性 try/except), 裸环境落 tempfile.gettempdir()/DirectorMasterIntake;
  · 失败路径诚实上报 (ok=False + engine_error + errors), 绝不伪造分集结果;
  · AI 接口地址/密钥/模型名 经 resolve_ai_config 继承核心数据包, 传给
    run_intake 的 LLM 可选精拆轨 (api_url/api_key); 核心数据包可缺席。
零第三方依赖 (仅 stdlib)。
"""
import json as _json
import os as _os
import tempfile as _tempfile

from aggregator.node_base import DirectorNodeBase, parse_core_pack, resolve_ai_config


class DirectorMasterNovelIntake(DirectorNodeBase):
    """长篇分集接入节点 (批次7) — 小说原文 → 分集产物 + 接入报告。

    输出: 人读接入报告 (ok/集数/章节检出/覆盖账本/LLM轨/检查点/记忆桥/
    输出目录/分集清单) + 管线 JSON (run_intake 完整返回 dict)。"""
    NODE_TYPE = "长篇接入"

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "小说原文": ("STRING", {"default": "", "multiline": True, "forceInput": True,
                "tooltip": "★ 长篇小说全文 — 章节感知切分+覆盖账本Σ校验+锚点回溯+三指标钩子+断点续跑+记忆桥; 空输入将得到诚实的 fail 报告"}),
        }, "optional": {
            "核心数据包": ("STRING", {"default": "", "multiline": True, "forceInput": True,
                "tooltip": "接 Core.核心数据包 — 可继承 AI 接口配置 (_ai_api_url/_ai_api_key/_ai_api_model); 缺席时用本节点自身 AI 输入"}),
            "项目名": ("STRING", {"default": "小说项目",
                "tooltip": "产物落盘子目录名 (<输出目录>/episodes/<项目名>/); 重跑同项目名命中断点续跑"}),
            "每集目标字数": ("INT", {"default": 8000, "min": 200, "max": 10000000, "step": 100,
                "tooltip": "单集目标字数 (章节边界优先贪心聚合; 单章超长按段落边界二分)"}),
            "输出目录": ("STRING", {"default": "",
                "tooltip": "留空 = 运行时兜底: ComfyUI output 目录, 裸 Python 环境则系统临时目录 DirectorMasterIntake"}),
            "AI接口地址": ("STRING", {"default": "",
                "tooltip": "可选 — LLM 精拆轨 (OpenAI 兼容端点, 只加 logline 注释字段原文不可变); 留空走确定性轨"}),
            "AI密钥": ("STRING", {"default": ""}),
            "AI模型名": ("STRING", {"default": ""}),
        }}

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("接入报告", "管线JSON")
    FUNCTION = "novel_intake"
    CATEGORY = "PromptLibrary/聚合/长篇管线"

    @staticmethod
    def _resolve_out_dir(explicit):
        """输出目录兜底: 显式输入优先; 空 = ComfyUI output 目录 (惰性 try) →
        裸环境系统临时目录。不得在模块顶层 import folder_paths/ComfyUI。"""
        d = (explicit or "").strip()
        if d:
            return d
        try:
            import folder_paths
            out = folder_paths.get_output_directory()
            if out:
                return out
        except Exception:
            pass
        return _os.path.join(_tempfile.gettempdir(), "DirectorMasterIntake")

    def _render_report(self, result, out_dir, project_dir):
        """从 run_intake 返回 dict 构建人读报告 (成功/失败共用, 全部 .get 防缺键)。"""
        ledger = result.get("ledger_summary") or {}
        llm_track = result.get("llm_track") or {}
        ckpt = result.get("checkpoints") or {}
        memory = result.get("memory") or {}
        eps = result.get("episodes") or []
        lines = ["=" * 64,
                 "DirectorMaster 长篇接入报告 (小说 → 分集)",
                 "=" * 64,
                 "状态: %s | 集数: %d | 章节检出: %s | 总字数: %s"
                 % ("ok" if result.get("ok") else "fail", len(eps),
                    ledger.get("chapters", "?"), ledger.get("total_chars", "?")),
                 "覆盖账本: %s (Σ==len(text) 全量重算)"
                 % ("通过" if ledger.get("ok") else "未通过"),
                 "LLM 精拆轨: %s" % (llm_track.get("status", "unknown"),),
                 "检查点 (断点续跑): 命中跳过 %s 集 / 新算 %s 集"
                 % (ckpt.get("skipped", 0), ckpt.get("regenerated", 0)),
                 "记忆桥 (dm_memory): %s" % (memory.get("status", "unknown"),),
                 "输出目录: %s" % project_dir,
                 "项目: %s | pipeline_id: %s"
                 % (result.get("project", ""), result.get("pipeline_id", ""))]
        if result.get("errors"):
            lines.append("错误 (%d):" % len(result["errors"]))
            for e in result["errors"][:10]:
                lines.append("  - %s" % str(e)[:200])
        lines.append("分集清单:")
        for i, ep in enumerate(eps, start=1):
            lines.append("  %d. %s | %s | %d 字"
                         % (i, str(ep.get("ep_id", "?")),
                            str(ep.get("title", "")) or "(无题)",
                            len(ep.get("text") or "")))
        lines.append("=" * 64)
        return "\n".join(lines)

    def novel_intake(self, **kwargs):
        core = parse_core_pack(kwargs.get("核心数据包", ""))
        api_url, api_key, _api_model = resolve_ai_config(kwargs, core)
        novel_text = kwargs.get("小说原文", "") or ""
        project = (kwargs.get("项目名", "") or "").strip() or "小说项目"
        try:
            target_chars = int(kwargs.get("每集目标字数", 8000) or 8000)
        except Exception:
            target_chars = 8000
        out_dir = self._resolve_out_dir(kwargs.get("输出目录", ""))
        try:
            # 方法内惰性导入 — 顶层不 import pipeline, 裸 python 导入本包不崩
            from aggregator.episode_pipeline.pipeline import run_intake, safe_name
        except Exception as e:
            err_report = ("=" * 64 + "\n"
                          "DirectorMaster 长篇接入引擎异常 (诚实上报, 不伪造结果)\n"
                          + "=" * 64 + "\n%s: %s\n"
                          % (type(e).__name__, str(e)[:300])
                          + "接入未完成 — episode_pipeline 管线段不可用; 本节点不产生猜测性分集。\n"
                          + "=" * 64)
            err_meta = _json.dumps({"ok": False,
                                    "engine_error": "run_intake 不可用: %s: %s"
                                    % (type(e).__name__, str(e)[:300]),
                                    "errors": [str(e)[:300]], "episodes": []},
                                   ensure_ascii=False, indent=2)
            return (err_report, err_meta)
        try:
            result = run_intake(novel_text, out_dir, project, target_chars,
                                api_url=api_url, api_key=api_key)
        except Exception as e:
            err_report = ("=" * 64 + "\n"
                          "DirectorMaster 长篇接入引擎异常 (诚实上报, 不伪造结果)\n"
                          + "=" * 64 + "\n%s: %s\n"
                          % (type(e).__name__, str(e)[:300])
                          + "接入未完成 — 请检查输入; 本节点不产生猜测性分集。\n"
                          + "=" * 64)
            err_meta = _json.dumps({"ok": False,
                                    "engine_error": "%s: %s"
                                    % (type(e).__name__, str(e)[:300]),
                                    "errors": ["%s: %s" % (type(e).__name__, str(e)[:200])],
                                    "episodes": []},
                                   ensure_ascii=False, indent=2)
            return (err_report, err_meta)
        if not result.get("ok"):
            # run_intake fail loud (空输入/账本未过/逐集失败等) — 诚实上报不伪造
            errors = [str(e)[:200] for e in (result.get("errors") or [])]
            meta = dict(result) if isinstance(result, dict) else {}
            meta["ok"] = False
            meta.setdefault("errors", errors)
            meta["engine_error"] = "run_intake fail loud: %s" % ("; ".join(errors)[:300] or "未知原因")
            fail_report = ("=" * 64 + "\n"
                           "DirectorMaster 长篇接入未完成 (诚实上报, 不伪造结果)\n"
                           + "=" * 64 + "\n管线返回 ok=False:\n")
            for e in errors[:10]:
                fail_report += "  - %s\n" % e
            fail_report += ("小说原文为空或切分/覆盖账本校验未通过 — 本节点不产出猜测性分集。\n"
                            + "=" * 64)
            return (fail_report, _json.dumps(meta, ensure_ascii=False, indent=2))
        project_dir = _os.path.join(str(out_dir), "episodes",
                                    safe_name(project))
        return (self._render_report(result, out_dir, project_dir),
                _json.dumps(result, ensure_ascii=False, indent=2))
