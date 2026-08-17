# -*- coding: utf-8 -*-
"""
ProjectArchivePro - 项目归档节点 (P2 工程化)
================================================
Phase 28 P2 - 序列化整个项目状态

归档内容:
- 节点输出汇总
- 元数据 (导演/类型/情感/场景/审美)
- 版本控制快照
- 工作流配置
- 测试结果
- README + CHANGELOG
"""
from __future__ import annotations

import json
import time
import hashlib


# ============================================================
# 归档数据结构
# ============================================================
def create_archive(project_name="default", contents=None, metadata=None, format="json"):
    """
    创建项目归档

    Returns:
        dict: 归档数据
    """
    archive = {
        "project_name": project_name,
        "archive_id": "arc_{}_{}".format(int(time.time() * 1000), hashlib.md5(project_name.encode()).hexdigest()[:6]),
        "created_at": time.time(),
        "created_at_str": time.strftime("%Y-%m-%d %H:%M:%S"),
        "contents": contents or {},
        "metadata": metadata or {},
        "format": format,
        "version": "3.1",
        "schema": "comfyui-promptlibrary-archive-v1",
    }

    # 计算哈希
    content_str = json.dumps(archive["contents"], ensure_ascii=False, sort_keys=True)
    archive["content_hash"] = hashlib.md5(content_str.encode()).hexdigest()
    archive["size_bytes"] = len(content_str.encode("utf-8"))

    return archive


def archive_to_markdown(archive):
    """归档转 Markdown"""
    md = "# 项目归档: {}\n\n".format(archive["project_name"])
    md += "- 归档 ID: `{}`\n".format(archive["archive_id"])
    md += "- 创建时间: {}\n".format(archive["created_at_str"])
    md += "- 版本: {}\n".format(archive["version"])
    md += "- Schema: {}\n".format(archive["schema"])
    md += "- 大小: {} 字节\n".format(archive["size_bytes"])
    md += "- 哈希: `{}`\n\n".format(archive["content_hash"])

    md += "## 元数据\n\n"
    md += "```json\n"
    md += json.dumps(archive["metadata"], ensure_ascii=False, indent=2)
    md += "\n```\n\n"

    md += "## 内容\n\n"
    for k, v in archive["contents"].items():
        md += "### {}\n\n".format(k)
        if isinstance(v, str):
            md += v + "\n\n"
        else:
            md += "```json\n"
            md += json.dumps(v, ensure_ascii=False, indent=2)
            md += "\n```\n\n"

    return md


def archive_to_json(archive, pretty=True):
    return json.dumps(archive, ensure_ascii=False, indent=2 if pretty else None)


# ============================================================
# ComfyUI 节点
# ============================================================
class ProjectArchivePro:
    """
    项目归档 Pro 节点 - Phase 28 P2
    工程化: 序列化整个项目状态

    自动赋予: 默认 json 格式
    专项调整: 3 格式 + 元数据 + 内容
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "项目名": ("STRING", {"default": "default_project"}),
                "格式": (["json", "markdown", "raw"], {"default": "json"}),
            },
            "optional": {
                "内容1": ("STRING", {"default": "", "multiline": True}),
                "内容2": ("STRING", {"default": "", "multiline": True}),
                "内容3": ("STRING", {"default": "", "multiline": True}),
                "元数据JSON": ("STRING", {"default": "", "multiline": True}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("归档内容", "归档ID", "元信息")
    FUNCTION = "archive"
    CATEGORY = "Director/Engineering"

    def archive(self, **kwargs):
        project_name = kwargs.get("项目名", "default_project")
        fmt = kwargs.get("格式", "json")

        contents = {}
        for i in [1, 2, 3]:
            c = kwargs.get("内容{}".format(i), "")
            if c:
                contents["item_{}".format(i)] = c

        metadata_str = kwargs.get("元数据JSON", "")
        try:
            metadata = json.loads(metadata_str) if metadata_str else {}
        except Exception:
            metadata = {}

        arc = create_archive(
            project_name=project_name,
            contents=contents,
            metadata=metadata,
            format=fmt,
        )

        if fmt == "markdown":
            output = archive_to_markdown(arc)
        elif fmt == "json":
            output = archive_to_json(arc)
        else:
            output = json.dumps(arc, ensure_ascii=False)

        meta = json.dumps({
            "archive_id": arc["archive_id"],
            "size_bytes": arc["size_bytes"],
            "content_hash": arc["content_hash"],
            "format": fmt,
            "items_count": len(contents),
        }, ensure_ascii=False, indent=2)

        return (output, arc["archive_id"], meta)


# NODE_CLASS_MAPPINGS (disabled - internal library only) = {
#     "ProjectArchivePro": ProjectArchivePro,
# }

# NODE_DISPLAY_NAME_MAPPINGS (disabled) = {
#     "ProjectArchivePro": "📦 项目归档 Pro (P2) — Phase 28 P2 / 序列化+哈希+多格式",
# }
