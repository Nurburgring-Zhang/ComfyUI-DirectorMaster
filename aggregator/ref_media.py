# -*- coding: utf-8 -*-
"""
aggregator/ref_media.py — 参考图/参考视频 IMAGE 张量处理 (ComfyUI 标准)
========================================================================
ComfyUI 中参考图的正确传递格式是 IMAGE 类型 (torch.Tensor [B,H,W,C]),
LoadImage 节点输出的就是 IMAGE。本模块把 IMAGE 张量落盘为文件并返回可引用路径,
供下游视频 API (Seedance/Wan/Hailuo/Sora) 的 reference_images 字段使用。

格式规范 (回答"参考图参考视频传递应该是什么格式"):
  - 参考图: IMAGE 类型 (torch.Tensor, shape [B,H,W,C], 值域 0-1)。接 LoadImage 的 IMAGE 输出。
  - 参考视频: IMAGE 批次 (多帧, shape [N,H,W,C]) 或 VHS LoadVideo 的 IMAGE 输出。
  - 若需直接给外部 API 传 URL/路径, 用 STRING 路径槽 (与 IMAGE 槽二选一, IMAGE 优先)。

降级: 无 torch/PIL/folder_paths (非 ComfyUI 环境) 时返回空串, 不报错。
"""
import os as _os
import time as _time


def _comfy_input_dir():
    """获取 ComfyUI input 目录 (folder_paths), 失败返回 None."""
    try:
        import folder_paths
        d = folder_paths.get_input_directory()
        if d and _os.path.isdir(d):
            return d
    except Exception:
        pass
    return None


def image_to_ref_path(image, tag="ref"):
    """把 IMAGE 张量 (torch.Tensor [B,H,W,C]) 保存为 PNG, 返回文件名。

    Args:
        image: torch.Tensor, shape [B,H,W,C], 值域 0-1 (ComfyUI IMAGE 标准)。
        tag: 文件名前缀标签 (如 "角色正面")。
    Returns:
        保存的文件名 (str); 非张量/环境缺失时返回 ""。
    """
    if image is None:
        return ""
    try:
        import torch
        import numpy as np
        from PIL import Image
    except Exception:
        return ""
    try:
        if not torch.is_tensor(image):
            return ""
        t = image
        if t.dim() == 3:  # 单图 [H,W,C] → [1,H,W,C]
            t = t.unsqueeze(0)
        if t.dim() != 4:
            return ""
        t = t[0]  # 取首帧
        arr = (t.detach().cpu().float().clamp(0, 1).numpy() * 255).astype("uint8")
        img = Image.fromarray(arr)
        in_dir = _comfy_input_dir() or "."
        safe_tag = "".join(ch if ch.isalnum() else "_" for ch in str(tag))[:24] or "ref"
        fname = "dm_%s_%d.png" % (safe_tag, int(_time.time() * 1000))
        fpath = _os.path.join(in_dir, fname)
        img.save(fpath)
        return fname
    except Exception:
        return ""


def image_batch_to_ref_paths(image, tag="ref", max_frames=8):
    """把视频帧批次 IMAGE (torch.Tensor [N,H,W,C]) 保存为多张 PNG, 返回文件名列表。

    用于参考视频 (多帧)。抽帧保存 (默认最多 max_frames 帧)。
    """
    if image is None:
        return []
    try:
        import torch
        import numpy as np
        from PIL import Image
    except Exception:
        return []
    try:
        if not torch.is_tensor(image) or image.dim() != 4:
            return []
        n = min(image.shape[0], max_frames)
        in_dir = _comfy_input_dir() or "."
        safe_tag = "".join(ch if ch.isalnum() else "_" for ch in str(tag))[:24] or "ref"
        stamp = int(_time.time() * 1000)
        paths = []
        step = max(1, image.shape[0] // n)
        for i in range(0, image.shape[0], step):
            if len(paths) >= max_frames:
                break
            arr = (image[i].detach().cpu().float().clamp(0, 1).numpy() * 255).astype("uint8")
            img = Image.fromarray(arr)
            fname = "dm_%s_%d_%03d.png" % (safe_tag, stamp, len(paths))
            img.save(_os.path.join(in_dir, fname))
            paths.append(fname)
        return paths
    except Exception:
        return []


def resolve_ref(kwargs, img_key, path_key, tag):
    """统一解析参考输入: IMAGE 张量优先 (落盘返回文件名), 否则用 STRING 路径。

    Args:
        kwargs: 节点 kwargs。
        img_key: IMAGE 输入键名 (如 "参考图_IMAGE_角色正面")。
        path_key: STRING 路径输入键名 (如 "参考图_角色正面")。
        tag: 落盘文件名标签。
    Returns:
        参考引用 (str): 落盘文件名 或 用户填的路径/URL; 无则 ""。
    """
    img = kwargs.get(img_key)
    if img is not None:
        p = image_to_ref_path(img, tag)
        if p:
            return p
    return (kwargs.get(path_key) or "").strip()
