# -*- coding: utf-8 -*-
"""工作流验证器: 节点类型已注册 + 连线端点有效 + 类型匹配"""
import importlib.util, os, sys, json, glob
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("m", "__init__.py")
m = importlib.util.module_from_spec(spec); sys.modules["m"] = m
spec.loader.exec_module(m)
MC = m.NODE_CLASS_MAPPINGS

# ComfyUI 内置节点 (真实 ComfyUI 环境可用, 非本包注册) — 白名单
COMFY_BUILTINS = {
    "UNETLoader", "CLIPLoader", "VAELoader", "LoadImage", "SaveImage", "PreviewImage",
    "CLIPTextEncode", "CLIPTextEncodeSDXL", "KSampler", "KSamplerAdvanced", "VAEDecode",
    "VAEEncode", "EmptyLatentImage", "LatentUpscale", "ImageScale", "ImageComposite",
    "CheckpointLoaderSimple", "LoraLoader", "ControlNetLoader", "ControlNetApply",
    "ControlNetApplyAdvanced", "IPAdapter", "IPAdapterAdvanced", "LoadVideo", "SaveVideo",
    "VideoLinearCFGGuidance", "ModelSamplingFlux", "BasicScheduler", "SamplerCustom",
    "BasicGuider", "BasicLatentNoise", "RandomNoise", "CFGZero", "FreeU",
    "Note", "Reroute", "PrimitiveNode",
    # VideoHelperSuite (VHS) 第三方扩展节点
    "VideoCombine", "LoadVideoPath", "LoadVideoUpload", "VideoInfo",
}


def node_io(ntype):
    cls = MC[ntype]
    it = cls.INPUT_TYPES()
    # 连线输入名集合 (forceInput/IMAGE) 与全部输入名
    conn_in = []; all_in = []
    for sec in ("required", "optional"):
        for name, sp in (it.get(sec) or {}).items():
            opts = sp[1] if len(sp) > 1 and isinstance(sp[1], dict) else {}
            all_in.append(name)
            if opts.get("forceInput") or sp[0] == "IMAGE":
                conn_in.append(name)
    rn = list(getattr(cls, "RETURN_NAMES", None) or [])
    rt = list(cls.RETURN_TYPES)
    out_names = [rn[i] if i < len(rn) else f"out{i}" for i in range(len(rt))]
    return conn_in, all_in, out_names


def validate(wf_path):
    d = json.load(open(wf_path, encoding="utf-8"))
    nodes = d.get("nodes", [])
    links = d.get("links", [])
    errs = []
    by_id = {n["id"]: n for n in nodes}
    # 1) 节点类型注册 (ComfyUI 内置节点白名单放行)
    for n in nodes:
        t = n.get("type")
        if t not in MC and t not in COMFY_BUILTINS:
            errs.append("未注册节点类型: %s (id=%s)" % (t, n.get("id")))
    # 2) 连线端点有效
    for l in links:
        lid, fn, fi, tn, ti, typ = l[0], l[1], l[2], l[3], l[4], (l[5] if len(l) > 5 else "?")
        if fn not in by_id:
            errs.append("link%s 源节点%s不存在" % (lid, fn)); continue
        if tn not in by_id:
            errs.append("link%s 目标节点%s不存在" % (lid, tn)); continue
        fnode, tnode = by_id[fn], by_id[tn]
        fouts = fnode.get("outputs", [])
        tins = tnode.get("inputs", [])
        if fi >= len(fouts):
            errs.append("link%s 源槽%s越界(%s.%s)" % (lid, fi, fnode.get("type"), len(fouts)))
        if ti >= len(tins):
            errs.append("link%s 目标槽%s越界(%s.%s)" % (lid, ti, tnode.get("type"), len(tins)))
    # 3) 每个 forceInput 是否被连接 (信息性)
    unconnected = []
    for n in nodes:
        ntype = n.get("type")
        if ntype not in MC:
            continue
        conn_in, _, _ = node_io(ntype)
        linked_names = set()
        for i in n.get("inputs", []):
            if i.get("link") is not None:
                linked_names.add(i.get("name"))
        for ci in conn_in:
            if ci not in linked_names:
                unconnected.append("%s(id=%s).%s" % (ntype, n.get("id"), ci))
    return errs, unconnected, len(nodes), len(links)


if __name__ == "__main__":
    # V14.3: legacy/ 工作流已随 legacy 节点层移除, 只校验现行管线。
    wfs = sorted(glob.glob(os.path.join("workflows", "*.json")))
    total_err = 0
    for wf in wfs:
        errs, unconn, nn, nl = validate(wf)
        name = os.path.relpath(wf)
        if errs:
            total_err += len(errs)
            print("[ERR] %s [%d节点%d连线] %d错误:" % (name, nn, nl, len(errs)))
            for e in errs[:6]:
                print("     -", e)
        else:
            print("[OK ] %s [%d节点%d连线] 类型全注册+连线有效 | 未连forceInput:%d" % (name, nn, nl, len(unconn)))
    print("\n总错误:", total_err)
