# -*- coding: utf-8 -*-
"""
V15.0-MERGED 多模态理解引擎 (Multimodal Engine)
================================================
修正版 — 否决原提案的 pass 空壳。只实现真实可算的分析, 不能实现的诚实降级。

真实能力:
  图像分析 (numpy/PIL): k-means 色板提取 / 亮度统计→光影判断 / 饱和度对比→情绪倾向 /
                        能量分布→构图倾向。全部确定性真实计算。
  音频分析 (wave 标准库): WAV 时长/RMS 能量 → 节奏倾向。仅 WAV, 其他格式诚实降级。
  视频分析: 本环境无解码器 — 诚实降级 (stderr 上报), 不假装支持。
"""
import os as _os
import sys as _sys

# 色相族分类 (H 区间 → 名称)
_HUE_FAMILIES = [
    (15, "红"), (45, "橙"), (70, "黄"), (160, "绿"), (200, "青"),
    (260, "蓝"), (300, "紫"), (345, "品红"), (360, "红"),
]


def _rgb_to_hsv(r, g, b):
    r, g, b = r / 255.0, g / 255.0, b / 255.0
    mx, mn = max(r, g, b), min(r, g, b)
    d = mx - mn
    if d == 0:
        h = 0
    elif mx == r:
        h = 60 * (((g - b) / d) % 6)
    elif mx == g:
        h = 60 * ((b - r) / d + 2)
    else:
        h = 60 * ((r - g) / d + 4)
    s = 0 if mx == 0 else d / mx
    return h, s, mx


def _hue_family(h):
    for limit, name in _HUE_FAMILIES:
        if h <= limit:
            return name
    return "红"


def _kmeans_palette(pixels, k=5, iters=8, seed=7):
    """numpy k-means 色板 (确定性初始化)."""
    import numpy as np
    rng = np.random.RandomState(seed)
    n = len(pixels)
    if n == 0:
        return []
    idx = rng.choice(n, size=min(k, n), replace=False)
    centers = pixels[idx].astype(np.float64)
    for _ in range(iters):
        d = ((pixels[:, None, :] - centers[None, :, :]) ** 2).sum(axis=2)
        labels = d.argmin(axis=1)
        new_centers = centers.copy()
        for j in range(len(centers)):
            mask = labels == j
            if mask.any():
                new_centers[j] = pixels[mask].mean(axis=0)
        if np.allclose(new_centers, centers):
            break
        centers = new_centers
    # 按簇大小排序
    labels = ((pixels[:, None, :] - centers[None, :, :]) ** 2).sum(axis=2).argmin(axis=1)
    counts = [(int((labels == j).sum()), centers[j]) for j in range(len(centers))]
    counts.sort(key=lambda x: -x[0])
    return [c for _, c in counts]


def analyze_image(image):
    """分析图像 → 风格向量文本.

    image: numpy array (H,W,3) 0-1 或 0-255, 或图像文件路径。
    返回 dict: {ok, palette, lighting, mood_hint, composition, text, error}
    """
    try:
        import numpy as np
    except ImportError:
        return {"ok": False, "text": "", "error": "numpy 不可用 — 图像分析降级"}

    arr = None
    try:
        if isinstance(image, str) and _os.path.isfile(image):
            from PIL import Image as _PILImg
            arr = np.asarray(_PILImg.open(image).convert("RGB"), dtype=np.float64)
        else:
            # ComfyUI IMAGE = torch 张量 (B,H,W,C) 0-1, 或 numpy 数组
            x = image
            if hasattr(x, "cpu") and hasattr(x, "numpy"):
                x = x.detach().cpu().numpy()
            x = np.asarray(x)
            src_is_float = np.issubdtype(x.dtype, np.floating)
            x = x.astype(np.float64)
            if x.ndim == 4:  # 批次维 → 取首帧
                x = x[0]
            if x.ndim == 3 and x.shape[-1] == 4:  # RGBA → RGB
                x = x[..., :3]
            if x.ndim != 3 or x.shape[-1] != 3:
                return {"ok": False, "text": "", "error": f"图像通道数无效 (shape={getattr(image, 'shape', '?')})"}
            # 0-1 vs 0-255 判定: 源为浮点且 max<=1.5 视为 0-1 (uint8 不缩放, 暗图不误判)
            if src_is_float and x.max() <= 1.5:
                x = x * 255.0
            arr = x
    except Exception as e:
        return {"ok": False, "text": "", "error": f"图像读取失败: {type(e).__name__}"}

    if arr is None or arr.size == 0:
        return {"ok": False, "text": "", "error": "无有效图像输入"}

    h, w = arr.shape[0], arr.shape[1]
    # 降采样加速 (最多 20000 像素)
    flat = arr.reshape(-1, 3)
    if len(flat) > 20000:
        step = len(flat) // 20000
        flat = flat[::step]

    # 色板
    palette = _kmeans_palette(flat, k=5)
    pal_desc = []
    for c in palette:
        hh, ss, vv = _rgb_to_hsv(*[float(x) for x in c])
        fam = _hue_family(hh) if ss > 0.15 else ("无彩" if vv < 0.6 else "白")
        pal_desc.append(f"{fam}({int(c[0])},{int(c[1])},{int(c[2])})")

    # 光影: 亮度统计
    lum = flat.mean(axis=1)
    mean_l, std_l = float(lum.mean()), float(lum.std())
    if mean_l < 85:
        lighting = "低调光影 (暗调主导, 适合孤独/悬疑/黑色)"
    elif mean_l > 170:
        lighting = "高调光影 (明亮主导, 适合纯真/希望/轻盈)"
    else:
        lighting = "自然光影 (中间调, 适合写实/日常)"
    if std_l > 70:
        lighting += "+高对比"

    # 饱和度 → 情绪倾向
    sat = []
    for c in flat[::max(1, len(flat) // 5000)]:
        _, ss, _ = _rgb_to_hsv(*[float(x) for x in c])
        sat.append(ss)
    mean_sat = float(sum(sat) / max(1, len(sat)))
    if mean_sat > 0.5:
        mood_hint = "高饱和 — 情绪外放/欲望/风格化"
    elif mean_sat < 0.18:
        mood_hint = "低饱和 — 克制/写实/疏离"
    else:
        mood_hint = "中饱和 — 平衡/自然"

    # 构图: 中心 vs 边缘能量
    gray = arr.mean(axis=2)
    ch, cw = h // 2, w // 2
    center = gray[max(0, ch - h // 4):ch + h // 4, max(0, cw - w // 4):cw + w // 4]
    gx = np.abs(np.diff(gray, axis=1)).mean()
    center_energy = float(np.abs(np.diff(center, axis=1)).mean()) if center.size else 0
    composition = "中心构图倾向 (主体集中)" if center_energy > gx * 1.1 else \
                  ("分散构图倾向 (视觉元素分布均匀)" if center_energy < gx * 0.9 else "均衡构图")

    text = (
        f"【多模态理解 · 图像分析】\n"
        f"主色板: {' / '.join(pal_desc)}\n"
        f"光影判断: {lighting}\n"
        f"情绪倾向: {mood_hint}\n"
        f"构图倾向: {composition}\n"
        f"应用建议: 以上维度应锚定到导演档案的色彩/光/构图维度, 与场景情绪一致时采纳, 冲突时以场景为准"
    )
    return {"ok": True, "palette": pal_desc, "lighting": lighting,
            "mood_hint": mood_hint, "composition": composition, "text": text, "error": ""}


def analyze_audio(path):
    """WAV 音频分析 (时长/RMS 能量 → 节奏倾向). 非 WAV 诚实降级."""
    import wave as _wave
    p = str(path or "")
    if not p or not _os.path.isfile(p):
        return {"ok": False, "text": "", "error": "音频文件不存在"}
    if not p.lower().endswith(".wav"):
        _sys.stderr.write(f"[DirectorMaster] 音频分析仅支持 WAV, 跳过: {_os.path.basename(p)}\n")
        return {"ok": False, "text": "", "error": "仅支持 WAV 格式 (诚实降级)"}
    try:
        with _wave.open(p, "rb") as wf:
            n = wf.getnframes()
            rate = wf.getframerate()
            width = wf.getsampwidth()
            dur = n / float(rate) if rate else 0
            frames = wf.readframes(min(n, rate * 30))
        import numpy as np
        dtype_map = {1: np.uint8, 2: np.int16, 4: np.int32}
        if width not in dtype_map:
            _sys.stderr.write(f"[DirectorMaster] WAV 采样宽度 {width} 字节不支持, 诚实降级\n")
            return {"ok": False, "text": "", "error": f"WAV 采样宽度 {width} 字节不支持"}
        sig = np.frombuffer(frames, dtype=dtype_map[width]).astype(np.float64)
        if width == 1:  # 8-bit 无符号, 中心化
            sig = sig - 128.0
        rms = float(np.sqrt((sig ** 2).mean())) if len(sig) else 0.0
        # 归一化到 16-bit 量级以便阈值统一
        rms_norm = rms / (2 ** (8 * width - 1)) * 32768.0
        energy = "高能量 (节奏强)" if rms_norm > 6000 else ("中能量" if rms_norm > 2000 else "低能量 (安静)")
        text = f"【多模态理解 · 音频分析】时长: {dur:.1f}s | RMS能量: {energy}\n应用建议: 能量水平映射到剪辑节奏 (高→快切, 低→长镜)"
        return {"ok": True, "duration": dur, "rms": rms_norm, "text": text, "error": ""}
    except Exception as e:
        return {"ok": False, "text": "", "error": f"音频解析失败: {type(e).__name__}"}


def analyze_video(path):
    """视频分析 — 本环境无解码器, 诚实降级 (不假装支持)."""
    p = str(path or "")
    if not p or not _os.path.isfile(p):
        return {"ok": False, "text": "", "error": "视频文件不存在"}
    _sys.stderr.write(f"[DirectorMaster] 视频分析需要解码器 (本环境无 cv2/ffmpeg 集成), 诚实降级: {_os.path.basename(p)}\n")
    return {"ok": False, "text": "",
            "error": "视频理解未启用 (需解码器) — 诚实降级, 不伪造分析结果"}
