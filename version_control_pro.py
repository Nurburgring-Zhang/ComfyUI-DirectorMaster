# -*- coding: utf-8 -*-
"""
VersionControlPro - 版本控制节点 (环节 35)
================================================
Phase 28 P1 - AIGC 影视全流程解析 补全节点

AI 时代最关键的环节: 一次生成多候选, 需要版本管理
本节点模拟"项目版本管理"逻辑:
- 版本创建/标签/分支/回滚
- 候选快照管理
- 元数据追踪 (导演/类型/情感/评分)
- 与 ShotSelectionPro 联动 (选片决策)
- 与 AestheticJudgmentPro 联动 (审美判断)

5 要素架构 (AIGC 文档 1.2 节):
- 数据层: 版本 dict (id/name/timestamp/parent/children/metadata/scores/notes)
- 上下文缩略层: 当前版本概要
- Skill/Harness: 版本操作 API (commit/branch/tag/rollback/diff/log)
- 经验矩阵: 历史版本评分 (从 director_soul 灵魂注入)
- AI 深度处理: LLM 风格的版本评估
"""
from __future__ import annotations

import os
import sys
import json
import time
import hashlib



try:
    from anti_ai_vocab import clean_anti_ai_text, inject_anti_ai_rules
    _HAS_ANTI_AI = True
except Exception:
    _HAS_ANTI_AI = False

try:
    from director_soul import soul_inject_simple
    _HAS_SOUL = True
except Exception:
    _HAS_SOUL = False


# ============================================================
# 版本状态机
# ============================================================
VERSION_STATES = {
    "DRAFT": "草稿",
    "REVIEW": "评审中",
    "APPROVED": "已通过",
    "REJECTED": "已驳回",
    "ARCHIVED": "已归档",
    "PUBLISHED": "已发布",
}


# ============================================================
# 版本控制核心 - 内存中维护版本树
# ============================================================
class VersionTree:
    """版本树 - 内存维护,可序列化"""

    def __init__(self, project_name="default_project"):
        self.project_name = project_name
        self.versions = {}  # id -> version dict
        self.tags = {}  # tag_name -> version_id
        self.branches = {"main": None}  # branch_name -> version_id
        self.head = None  # 当前 head version id

    def commit(self, name, content="", metadata=None, parent=None, scores=None, notes=""):
        """提交新版本"""
        version_id = "v_{}_{}".format(int(time.time() * 1000), hashlib.md5(name.encode()).hexdigest()[:6])
        version = {
            "id": version_id,
            "name": name,
            "content": content,
            "metadata": metadata or {},
            "scores": scores or {},
            "notes": notes,
            "parent": parent or self.head,
            "children": [],
            "timestamp": time.time(),
            "state": "DRAFT",
            "branch": "main",
        }
        # 更新 children
        if version["parent"] and version["parent"] in self.versions:
            self.versions[version["parent"]]["children"].append(version_id)
        self.versions[version_id] = version
        self.branches["main"] = version_id
        self.head = version_id
        return version_id

    def tag(self, version_id, tag_name):
        """打标签"""
        if version_id in self.versions:
            self.tags[tag_name] = version_id
            self.versions[version_id]["tags"] = self.versions[version_id].get("tags", []) + [tag_name]
            return True
        return False

    def branch_from(self, name, source_version_id):
        """从某版本创建分支"""
        self.branches[name] = source_version_id
        if source_version_id in self.versions:
            self.versions[source_version_id]["branches"] = self.versions[source_version_id].get("branches", []) + [name]
        return source_version_id

    def checkout(self, version_id):
        """切换 head"""
        if version_id in self.versions:
            self.head = version_id
            return True
        return False

    def rollback(self, version_id):
        """回滚到某版本 (创建新 commit 引用旧内容)"""
        if version_id in self.versions:
            old = self.versions[version_id]
            return self.commit(
                name="rollback_{}".format(old["name"]),
                content=old["content"],
                metadata=old.get("metadata", {}),
                parent=self.head,
                notes="Rollback to {}".format(version_id),
            )
        return None

    def set_state(self, version_id, state):
        """设置版本状态"""
        if version_id in self.versions and state in VERSION_STATES:
            self.versions[version_id]["state"] = state
            return True
        return False

    def log(self, limit=20):
        """查看历史"""
        sorted_v = sorted(self.versions.values(), key=lambda v: v["timestamp"], reverse=True)
        return sorted_v[:limit]

    def diff(self, v1_id, v2_id):
        """对比两个版本"""
        if v1_id not in self.versions or v2_id not in self.versions:
            return None
        v1 = self.versions[v1_id]
        v2 = self.versions[v2_id]
        # 简单 diff (字符串长度变化 + metadata 差异)
        return {
            "v1": {"id": v1_id, "name": v1["name"], "state": v1["state"]},
            "v2": {"id": v2_id, "name": v2["name"], "state": v2["state"]},
            "content_length_diff": len(v2.get("content", "")) - len(v1.get("content", "")),
            "metadata_diff": {
                k: (v1.get("metadata", {}).get(k), v2.get("metadata", {}).get(k))
                for k in set(list(v1.get("metadata", {}).keys()) + list(v2.get("metadata", {}).keys()))
            },
            "score_diff": {
                k: (v1.get("scores", {}).get(k), v2.get("scores", {}).get(k))
                for k in set(list(v1.get("scores", {}).keys()) + list(v2.get("scores", {}).keys()))
            },
        }

    def get_best(self, score_key="total", top_n=5):
        """获取评分最高的 N 个版本"""
        scored = [(v.get("scores", {}).get(score_key, 0), v) for v in self.versions.values()]
        scored.sort(key=lambda x: -x[0])
        return scored[:top_n]

    def to_dict(self):
        """序列化"""
        return {
            "project_name": self.project_name,
            "versions": self.versions,
            "tags": self.tags,
            "branches": self.branches,
            "head": self.head,
        }


# 全局内存版本树 (单进程)
_TREE_REGISTRY = {}


def get_tree(project_name="default_project"):
    if project_name not in _TREE_REGISTRY:
        _TREE_REGISTRY[project_name] = VersionTree(project_name)
    return _TREE_REGISTRY[project_name]


# ============================================================
# 主入口
# ============================================================
def manage_version(project_name="default_project", action="log", version_name="",
                   content="", metadata_json="", scores_json="", notes="",
                   target_version="", tag_name="", branch_name="",
                   score_key="total", top_n=5):
    """
    版本控制 - 增删改查

    Args:
        project_name: 项目名
        action: 操作 - commit/branch/tag/rollback/checkout/diff/log/best/get/set_state
        version_name: 版本名 (commit 时用)
        content: 内容 (commit 时用)
        metadata_json: 元数据 JSON (commit 时用)
        scores_json: 评分 JSON (commit 时用)
        notes: 备注
        target_version: 目标版本 ID (rollback/checkout/diff/set_state 时用)
        tag_name: 标签名 (tag 时用)
        branch_name: 分支名 (branch 时用)
        score_key: 评分维度 (best 时用)
        top_n: 取前 N 个 (best 时用)
    """
    tree = get_tree(project_name)

    if action == "commit":
        try:
            md = json.loads(metadata_json) if metadata_json else {}
        except Exception:
            md = {}
        try:
            sc = json.loads(scores_json) if scores_json else {}
        except Exception:
            sc = {}
        if _HAS_ANTI_AI:
            content = clean_anti_ai_text(content)
            content = inject_anti_ai_rules(content)
        version_id = tree.commit(version_name, content, md, scores=sc, notes=notes)
        return {"action": "commit", "version_id": version_id, "tree": tree.to_dict()}

    if action == "tag":
        ok = tree.tag(target_version, tag_name)
        return {"action": "tag", "success": ok}

    if action == "branch":
        source = target_version or tree.head
        result = tree.branch_from(branch_name, source)
        return {"action": "branch", "branch_name": branch_name, "source": result}

    if action == "rollback":
        new_id = tree.rollback(target_version)
        return {"action": "rollback", "new_version_id": new_id}

    if action == "checkout":
        ok = tree.checkout(target_version)
        return {"action": "checkout", "success": ok, "head": tree.head}

    if action == "diff":
        v1, v2 = target_version.split("->") if "->" in target_version else (target_version, tree.head)
        d = tree.diff(v1, v2)
        return {"action": "diff", "diff": d}

    if action == "log":
        log = tree.log()
        return {"action": "log", "count": len(log), "versions": [{"id": v["id"], "name": v["name"], "state": v["state"], "timestamp": v["timestamp"], "scores": v.get("scores", {}), "notes": v.get("notes", "")} for v in log]}

    if action == "best":
        best = tree.get_best(score_key, top_n)
        return {"action": "best", "score_key": score_key, "results": [{"score": s, "id": v["id"], "name": v["name"]} for s, v in best]}

    if action == "get":
        v = tree.versions.get(target_version)
        return {"action": "get", "version": v}

    if action == "set_state":
        ok = tree.set_state(target_version, version_name)  # 复用 version_name 作为状态
        return {"action": "set_state", "success": ok}

    return {"action": "unknown", "error": "Unknown action: {}".format(action)}


# ============================================================
# ComfyUI 节点
# ============================================================
class VersionControlPro:
    """
    版本控制 Pro 节点 - Phase 28 P1
    环节 35 - AI 时代多次生成时的版本管理

    自动赋予: 默认 log 模式 (查看历史)
    专项调整: 用户指定 action (commit/branch/tag/rollback/diff/best 等)
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "项目名": ("STRING", {"default": "default_project"}),
                "操作": (["log", "commit", "best", "diff", "tag", "branch", "rollback", "checkout", "get", "set_state"], {"default": "log"}),
            },
            "optional": {
                "版本名": ("STRING", {"default": "v1.0"}),
                "版本内容": ("STRING", {"default": "", "multiline": True}),
                "元数据JSON": ("STRING", {"default": "", "multiline": True}),
                "评分JSON": ("STRING", {"default": "", "multiline": True}),
                "备注": ("STRING", {"default": "", "multiline": True}),
                "目标版本": ("STRING", {"default": ""}),
                "标签名": ("STRING", {"default": ""}),
                "分支名": ("STRING", {"default": ""}),
                "评分维度": ("STRING", {"default": "total"}),
                "TopN": ("INT", {"default": 5, "min": 1, "max": 50, "step": 1}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("操作结果", "版本历史", "项目状态")
    FUNCTION = "control"
    CATEGORY = "Director/VersionControl"

    def control(self, **kwargs):
        project_name = kwargs.get("项目名", "default_project")
        action = kwargs.get("操作", "log")
        result = manage_version(
            project_name=project_name,
            action=action,
            version_name=kwargs.get("版本名", "v1.0"),
            content=kwargs.get("版本内容", ""),
            metadata_json=kwargs.get("元数据JSON", ""),
            scores_json=kwargs.get("评分JSON", ""),
            notes=kwargs.get("备注", ""),
            target_version=kwargs.get("目标版本", ""),
            tag_name=kwargs.get("标签名", ""),
            branch_name=kwargs.get("分支名", ""),
            score_key=kwargs.get("评分维度", "total"),
            top_n=kwargs.get("TopN", 5),
        )

        # 格式化输出
        result_str = json.dumps(result, ensure_ascii=False, indent=2)
        if action == "log":
            history = "项目: {} | 共 {} 个版本\n".format(project_name, result.get("count", 0))
            for v in result.get("versions", []):
                history += "- [{}] {} ({}) - 评分: {}\n".format(
                    v["state"], v["name"], v["id"][:20], v.get("scores", {}).get("total", "N/A")
                )
        elif action == "best":
            history = "项目: {} | 最佳 {} 个版本 (按 {})\n".format(project_name, len(result.get("results", [])), result.get("score_key"))
            for r in result.get("results", []):
                history += "- 评分 {:.3f}: {} ({})\n".format(r["score"], r["name"], r["id"][:20])
        elif action == "commit":
            history = "提交成功: {}".format(result.get("version_id", ""))
        elif action == "diff":
            history = json.dumps(result.get("diff", {}), ensure_ascii=False, indent=2)
        else:
            history = json.dumps(result, ensure_ascii=False, indent=2)[:500]

        # 项目状态
        tree = get_tree(project_name)
        status = "项目: {} | head: {} | 分支: {} | 标签: {} | 总版本: {}".format(
            project_name,
            tree.head or "(空)",
            list(tree.branches.keys()),
            list(tree.tags.keys()),
            len(tree.versions),
        )

        return (result_str, history, status)


# NODE_CLASS_MAPPINGS (disabled - internal library only) = {
#     "VersionControlPro": VersionControlPro,
# }

# NODE_DISPLAY_NAME_MAPPINGS (disabled) = {
#     "VersionControlPro": "🔀 版本控制 Pro (环节35) — Phase 28 P1 / commit/branch/tag/rollback",
# }
