# -*- coding: utf-8 -*-
"""
aggregator/eco/node.py — ComfyUI 节点: DirectorMasterEcoManager
(批次5 WaveC builder-p4, 生态预案 · 第 20 个注册节点)
================================================================================
生态预案三合一面 — 下拉选段, 全部走 aggregator.eco 聚合门面 (不绕过):
  pack_audit        dm_pack 包注册审计 (字段/版本/依赖三查, 负样本 fail loud);
  refflow_register  参考素材登记 (授权声明+来源描述必填, 缺任一 fail loud 不落盘)
                    + 素材解构三列表 (手法/参考实现/取舍, 确定性无 LLM)
                    + 可选契约 refs[] 注入 (只加 refs 键零漂移);
  decision_attach   决策审计轨追加 (append-only JSONL, sha256 哈希链 prev_hash
                    接龙) + 全链 verify。

范本: aggregator/episode_pipeline/node.py DirectorMasterNovelIntake (批次7) —
同款 DirectorNodeBase / CATEGORY / 输出目录非空校验 (LOW-5: None/空串诚实报错,
严禁字面 'None' 目录) / try-except 诚实上报。

纪律:
  · run 方法内惰性导入 (模块顶层不 import aggregator.eco/ComfyUI), 裸 python
    导入本包不崩; 门面经 importlib.import_module 按 sys.modules 解析
    (缺段/unavailable 场景可注入可观测, AttributeError 诚实降级);
  · 失败路径诚实上报 (ok=False + errors 非空 + 不抛异常), 绝不伪造生态结果;
  · 确定性: 报告 JSON 零 LLM 零随机零时间戳 (ensure_ascii=False);
  · options_considered 切分钉死: 英文分号 ";" split (去空白去空项, 保序);
    空输入 → None (门面按空链处理)。
零第三方依赖 (仅 stdlib)。
"""
import json as _json
import os as _os
import tempfile as _tempfile

from aggregator.node_base import DirectorNodeBase

# mode 三选一 (组合框枚举, 顺序即下拉顺序)
ECO_MODES = ("pack_audit", "refflow_register", "decision_attach")


class DirectorMasterEcoManager(DirectorNodeBase):
    """生态预案节点 (批次5) — 三模式聚合: 包审计 / 参考素材登记 / 决策审计轨。

    输出: 状态报告 JSON 字符串 (ok/mode/summary/errors, ensure_ascii=False,
    零时间戳) + 数值计数 (pack_audit=注册包数 / refflow_register=台账素材数 /
    decision_attach=决策条目 seq 序号)。"""
    NODE_TYPE = "生态预案"

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "生态模式": (list(ECO_MODES), {"default": "pack_audit",
                "tooltip": "★ 三选一 — pack_audit: dm_pack 包注册审计 (字段/版本/依赖三查); "
                           "refflow_register: 参考素材登记 (授权声明+来源描述必填, 缺任一 fail loud 不落盘); "
                           "decision_attach: 决策审计轨追加 (append-only, sha256 哈希链防篡改)"}),
        }, "optional": {
            "输出目录": ("STRING", {"default": "",
                "tooltip": "必填 — None/空串/纯空白一律诚实报错不执行 (严禁字面 'None' 目录); "
                           "生态产物落 <输出目录>/eco/ (packs|ref_ledger|decision_log.jsonl)"}),
            "项目名": ("STRING", {"default": "",
                "tooltip": "refflow_register / decision_attach 必填 (台账文件名与登记字段); pack_audit 可空"}),
            "素材ID": ("STRING", {"default": "",
                "tooltip": "refflow_register — 参考素材批次 ref_id (同 id 重复登记幂等覆盖同一条目)"}),
            "来源描述": ("STRING", {"default": "", "multiline": True,
                "tooltip": "refflow_register 必填 — source 来源描述 (缺任一授权字段 fail loud 不落盘)"}),
            "授权声明": ("STRING", {"default": "", "multiline": True,
                "tooltip": "refflow_register 必填 — authorization 授权声明 (\"只学手法不复制表达\"边界字段落盘进台账, 非口头约定)"}),
            "备注笔记": ("STRING", {"default": "", "multiline": True,
                "tooltip": "refflow_register 可选 — 解构笔记逐行归类三列表 (含 手法/technique → 手法列; 含 实现/做法/how → 参考实现列; 其余 → 取舍列)"}),
            "契约JSON": ("STRING", {"default": "", "multiline": True,
                "tooltip": "refflow_register 可选 — 批次6 storyboard_contract JSON 对象, 注入 refs[] 槽位 (只加 refs 键, 既有键逐字节不动); 非法 JSON 诚实拦截"}),
            "决策类别": ("STRING", {"default": "",
                "tooltip": "decision_attach — category (同 类别+主题 再追加 → 新条目 revised=true 且旧决策移入备选方案)"}),
            "决策主题": ("STRING", {"default": "",
                "tooltip": "decision_attach — subject"}),
            "决策内容": ("STRING", {"default": "", "multiline": True,
                "tooltip": "decision_attach — decision 决策正文"}),
            "备选方案": ("STRING", {"default": "", "multiline": True,
                "tooltip": "decision_attach 可选 — options_considered, 切分规则钉死为英文分号 \";\" split (去空白去空项保序); 留空按空链处理"}),
        }}

    RETURN_TYPES = ("STRING", "INT")
    RETURN_NAMES = ("生态报告", "计数")
    FUNCTION = "eco_manage"
    CATEGORY = "PromptLibrary/聚合/生态预案"

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
        return _os.path.join(_tempfile.gettempdir(), "DirectorMasterEco")

    # ---------- 报告构建 (确定性: 无时间戳/无随机, ensure_ascii=False) ----------
    @staticmethod
    def _emit(mode, out_dir, ok, errors, summary, count, engine_error=None):
        """统一输出: (状态报告 JSON 字符串, 数值计数 INT)。成功/失败共用键序。"""
        meta = {"ok": bool(ok), "mode": mode, "node": "DirectorMasterEcoManager",
                "out_dir": out_dir, "count": int(count or 0),
                "errors": [str(e)[:300] for e in (errors or [])]}
        if engine_error:
            meta["engine_error"] = str(engine_error)[:300]
        meta["summary"] = summary if isinstance(summary, dict) else {}
        return (_json.dumps(meta, ensure_ascii=False, indent=2), int(count or 0))

    @staticmethod
    def _fail(mode, out_dir, errors, engine_error=None, summary=None):
        """诚实失败: ok=False + errors 非空 + count=0, 不抛异常。

        summary 可选传入 mode 专属摘要 (如 pack_audit 部分包被拒时已注册包
        与审计错误仍如实展示, 不静默丢弃)。"""
        return DirectorMasterEcoManager._emit(
            mode, out_dir, False, errors or ["未知失败"],
            summary if isinstance(summary, dict) else {}, 0, engine_error)

    @staticmethod
    def _split_options(raw):
        """options_considered 确定性切分 (钉死英文分号 ";"): split(";") →
        strip → 去空项, 保序。空输入 → None (门面按空链处理)。"""
        text = "" if raw is None else str(raw)
        if not text.strip():
            return None
        opts = [p.strip() for p in text.split(";")]
        opts = [p for p in opts if p]
        return opts or None

    @staticmethod
    def _ledger_count(ledger_path):
        """refflow 计数: 台账 JSON 顶层素材条目数; 读取失败 → 1 (本次登记已
        原子写成功的最小真值, 不虚报)。"""
        try:
            with open(ledger_path, "r", encoding="utf-8") as f:
                data = _json.load(f)
            if isinstance(data, dict):
                return len(data)
        except Exception:
            pass
        return 1

    @staticmethod
    def _summary_pack(result):
        """pack_audit 摘要: 注册包六字段回读 + 注册表错误显式透传。"""
        packs = []
        for p in (result.get("packs") or []):
            if isinstance(p, dict):
                packs.append({k: p.get(k) for k in
                              ("pack_id", "version", "min_dm_version",
                               "dependencies", "tags", "entry", "pack_dir")})
        return {"pack_count": len(packs), "packs": packs,
                "audit_errors": [str(e)[:300] for e in (result.get("errors") or [])]}

    @staticmethod
    def _summary_refflow(result):
        """refflow_register 摘要: 登记 entry (含法务边界字段) + 三列表 + 注入与否。"""
        entry = result.get("entry") if isinstance(result.get("entry"), dict) else {}
        decon = result.get("deconstruct") if isinstance(result.get("deconstruct"), dict) else {}
        return {"ref_id": result.get("ref_id", entry.get("ref_id")),
                "ledger_path": result.get("ledger_path"),
                "entry": entry,
                "deconstruct": {k: list(decon.get(k) or [])
                                for k in ("手法", "参考实现", "取舍")},
                "contract_injected": "contract" in result}

    @staticmethod
    def _summary_decision(result):
        """decision_attach 摘要: 新条目 8 键 + log 路径 + verify 结论。"""
        entry = result.get("entry") if isinstance(result.get("entry"), dict) else {}
        keys = ("seq", "prev_hash", "hash", "category", "subject", "decision",
                "options_considered", "revised")
        return {"entry": {k: entry.get(k) for k in keys},
                "log_path": result.get("log_path"),
                "verify_ok": bool(result.get("ok")),
                "verify_errors": [str(e)[:300] for e in (result.get("errors") or [])]}

    # ---------- 主入口 ----------
    def eco_manage(self, **kwargs):
        mode = (kwargs.get("生态模式") or "").strip()
        # LOW-5: out_dir 非空校验 (EXECUTE 入口) — None/空串/纯空白一律诚实报错,
        # 严禁兜底/透传造成字面 "None" 目录。_resolve_out_dir 兜底仅用于合法显式值。
        raw_out = kwargs.get("输出目录")
        out_text = ("" if raw_out is None else str(raw_out)).strip()
        project = (kwargs.get("项目名") or "").strip()

        # 本地前置校验 (诚实失败, 不炸不落盘)
        errors = []
        if mode not in ECO_MODES:
            errors.append("生态模式 (mode) 非法: %r — 仅支持 %s (空/None 同样拦截)"
                          % (mode, " / ".join(ECO_MODES)))
        if not out_text:
            errors.append("输出目录 (out_dir) 必填: None/空串/纯空白 — 已拒绝执行, "
                          "严禁落到字面 'None' 目录, 请显式指定输出目录")
        if mode in ("refflow_register", "decision_attach") and not project:
            errors.append("项目名 (project) 必填: mode=%s 时缺失/空串 — 未落盘" % mode)

        contract = None
        raw_contract = (kwargs.get("契约JSON") or "").strip()
        if mode == "refflow_register" and raw_contract:
            try:
                parsed = _json.loads(raw_contract)
            except ValueError as e:
                errors.append("契约JSON 非合法 JSON: %s" % str(e)[:200])
            else:
                if not isinstance(parsed, dict):
                    errors.append("契约JSON 顶层须为 JSON 对象 (dict), 实际 %s"
                                  % type(parsed).__name__)
                else:
                    contract = parsed

        if errors:
            return self._fail(mode, out_text, errors)
        out_dir = self._resolve_out_dir(out_text)

        # 方法内惰性导入 — 顶层不 import aggregator.eco, 裸 python 导入本包不崩。
        # 用 importlib.import_module (非 `import a.b as c`, 后者优先从父包 getattr
        # 绑定会绕过 sys.modules 注入): 直接按 sys.modules 解析, 门面缺段/不可用
        # 时 AttributeError 走下方 except 诚实降级。
        try:
            import importlib as _importlib
            eco = _importlib.import_module("aggregator.eco")
        except Exception as e:
            return self._fail(mode, out_dir,
                              ["aggregator.eco 门面不可用: %s: %s"
                               % (type(e).__name__, str(e)[:200])],
                              engine_error="aggregator.eco 导入失败: %s: %s"
                                           % (type(e).__name__, str(e)[:300]))

        try:
            if mode == "pack_audit":
                result = eco.pack_audit(out_dir)
                summary = self._summary_pack(result)
                count = len(result.get("packs") or [])
            elif mode == "refflow_register":
                ref_id = kwargs.get("素材ID") or ""
                source = kwargs.get("来源描述") or ""
                authorization = kwargs.get("授权声明") or ""
                notes = (kwargs.get("备注笔记") or "").strip() or None
                result = eco.refflow_register(
                    out_dir, ref_id, source, authorization, project,
                    notes=notes, contract=contract)
                summary = self._summary_refflow(result)
                ledger_path = result.get("ledger_path")
                count = (self._ledger_count(ledger_path)
                         if result.get("ok") and ledger_path else 0)
            else:  # decision_attach
                options = self._split_options(kwargs.get("备选方案"))
                result = eco.decision_attach(
                    out_dir,
                    kwargs.get("决策类别") or "",
                    kwargs.get("决策主题") or "",
                    kwargs.get("决策内容") or "",
                    options_considered=options)
                summary = self._summary_decision(result)
                entry = result.get("entry") if isinstance(result.get("entry"), dict) else {}
                seq = entry.get("seq")
                count = seq if isinstance(seq, int) and seq > 0 else 0
        except Exception as e:
            return self._fail(mode, out_dir,
                              ["%s: %s" % (type(e).__name__, str(e)[:200])],
                              engine_error="eco 门面调用异常 (诚实上报, 不伪造结果): %s: %s"
                                           % (type(e).__name__, str(e)[:300]))

        ok = bool(result.get("ok")) if isinstance(result, dict) else False
        if not ok:
            # 门面 fail loud (负样本/段缺失/verify 失败等) — 诚实上报不伪造
            return self._fail(mode, out_dir,
                              (result.get("errors") or ["门面返回 ok=False (未知原因)"])
                              if isinstance(result, dict) else ["门面返回非 dict 结果"],
                              engine_error="eco 门面 ok=False: mode=%s" % mode,
                              summary=summary)
        return self._emit(mode, out_dir, True, [], summary, count)
