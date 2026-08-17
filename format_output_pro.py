# -*- coding: utf-8 -*-
"""
FormatOutputPro - 格式化输出节点 (P2 工程化)
================================================
Phase 28 P2 - 标准化输出格式

支持 8 种格式:
- text: 纯文本
- markdown: Markdown
- json: JSON
- yaml: YAML
- xml: XML
- html: HTML
- csv: CSV
- srt: 字幕
"""
from __future__ import annotations

import json
import re


# ============================================================
# 8 种格式转换
# ============================================================
def to_markdown(text, title="输出"):
    """转 Markdown"""
    if not text:
        return ""
    # 简单转换: 段落分隔
    lines = text.split("\n")
    result = "# {}\n\n".format(title)
    for line in lines:
        line = line.strip()
        if not line:
            result += "\n"
        elif line.startswith("- ") or line.startswith("* "):
            result += line + "\n"
        elif re.match(r"^\d+\.", line):
            result += line + "\n"
        else:
            result += line + "\n\n"
    return result.strip()


def to_json(text, indent=2, **kwargs):
    """尝试转 JSON, 失败则包装"""
    if not text:
        return "{}"
    # 简单检测
    text_strip = text.strip()
    if text_strip.startswith("{") and text_strip.endswith("}"):
        try:
            parsed = json.loads(text_strip)
            return json.dumps(parsed, ensure_ascii=False, indent=indent)
        except Exception:
            pass
    return json.dumps({"content": text}, ensure_ascii=False, indent=indent)


def to_yaml(text, **kwargs):
    """转 YAML (简单)"""
    if not text:
        return ""
    lines = text.split("\n")
    result = "content: |\n"
    for line in lines:
        result += "  " + line + "\n"
    return result


def to_xml(text, root="output", **kwargs):
    """转 XML"""
    if not text:
        return "<{}/>".format(root)
    # 转义
    escaped = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return "<{}>\n{}\n</{}>".format(root, escaped, root)


def to_html(text, title="输出"):
    """转 HTML"""
    if not text:
        return "<html></html>"
    escaped = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    body = escaped.replace("\n", "<br/>\n")
    return "<!DOCTYPE html>\n<html>\n<head><title>{}</title></head>\n<body>\n{}\n</body>\n</html>".format(title, body)


def to_csv(text, **kwargs):
    """转 CSV (按行)"""
    if not text:
        return ""
    lines = text.split("\n")
    return "\n".join(['"{}"'.format(line.replace('"', '""')) for line in lines])


def to_srt(text, **kwargs):
    """转 SRT 字幕 (按行)"""
    if not text:
        return ""
    lines = [l for l in text.split("\n") if l.strip()]
    srt = ""
    for i, line in enumerate(lines, 1):
        # 假设每行 3 秒
        start = (i - 1) * 3
        end = i * 3
        srt += "{}\n00:00:{:02d},000 --> 00:00:{:02d},000\n{}\n\n".format(
            i, start, end, line
        )
    return srt


FORMATTERS = {
    "text": lambda t, **kw: t,
    "markdown": to_markdown,
    "json": to_json,
    "yaml": to_yaml,
    "xml": to_xml,
    "html": to_html,
    "csv": to_csv,
    "srt": to_srt,
}


# ============================================================
# ComfyUI 节点
# ============================================================
class FormatOutputPro:
    """
    格式化输出 Pro 节点 - Phase 28 P2
    工程化: 8 种格式转换

    自动赋予: 默认 markdown
    专项调整: 8 格式 + 标题
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "输入文本": ("STRING", {"default": "", "multiline": True}),
                "格式": (list(FORMATTERS.keys()), {"default": "markdown"}),
            },
            "optional": {
                "标题": ("STRING", {"default": "输出"}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("格式化输出", "元信息")
    FUNCTION = "format"
    CATEGORY = "Director/Engineering"

    def format(self, **kwargs):
        text = kwargs.get("输入文本", "")
        fmt = kwargs.get("格式", "markdown")
        title = kwargs.get("标题", "输出")
        formatter = FORMATTERS.get(fmt, lambda t, **kw: t)
        try:
            output = formatter(text, title=title)
        except Exception as e:
            output = "[格式化错误: {}]\n\n{}".format(str(e), text)
        meta = json.dumps({
            "format": fmt,
            "input_length": len(text),
            "output_length": len(output),
            "title": title,
        }, ensure_ascii=False, indent=2)
        return (output, meta)


# NODE_CLASS_MAPPINGS (disabled - internal library only) = {
#     "FormatOutputPro": FormatOutputPro,
# }

# NODE_DISPLAY_NAME_MAPPINGS (disabled) = {
#     "FormatOutputPro": "📐 格式化输出 Pro (P2) — Phase 28 P2 / 8种格式",
# }
