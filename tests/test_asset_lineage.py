# -*- coding: utf-8 -*-
"""
批次6 D5/D6 — 资产派生谱系 + slot 接线 测试 (tests/test_asset_lineage.py)
=========================================================================
覆盖矩阵:
  T0  video_router RETURN 7 路冻结 (类型/名称零改动)
  T1  参考库JSON 无 母版/派生声明 → 无 谱系 键, 旧消费方零影响 (v1 兼容)
  T2  母版→派生 谱系记录 + 完整锚定 (库引用=真实版本id, 稳定内容零重复入库)
  T3  版本库: 存母版→更新母版 → 派生报 母版已更新待同步; 派生媒体缺 → 派生缺失
  T4  首库首跑 → 母版条目 母版缺失态 (无先前存档可比对, 库引用=本次快照), 派生 母版缺失
  T5  派生在场母版缺 → 母版缺失 (母版参考未提供); 无库不落盘
  T6  HellGrind锁定=True → 首次母版 母版缺失态 (库引用=真实 asset_registry 描述符快照)
  T7  video_router: 参考槽位 → reference_images 槽位序排列 + 槽位映射 (含 prompt 标签对齐)
  T8  video_router: 缺槽(负数/越界) → 诚实跳过 + 槽位映射说明, 未伪造占位
  T9  video_router: 无 参考槽位 (v1 JSON / 纯文本) → 原路径零变化 (无 槽位映射 键)
  T10 archive: 角色DNA档 非空 → 独立文件落盘 + commit files 含 角色DNA + blob 逐字回读
  T11 archive: 角色DNA档 空 → 既有 commit 行为零变化 (files 无 角色DNA, 磁盘无该文件)
退出码: 0 = 全部通过, 1 = 有失败
运行: python -X utf8 tests/test_asset_lineage.py
"""
import json
import os
import sys
import tempfile

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from aggregator.asset_master import DirectorMasterAsset
from aggregator.archive_master import DirectorMasterArchive
from aggregator.video_router_master import DirectorMasterVideoRouter
from aggregator.version_store import open_store

PASS, FAIL = 0, 0


def check(label, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  [OK] {label}")
    else:
        FAIL += 1
        print(f"  [FAIL] {label} {detail}")


def asset_ref_json(kw):
    out = DirectorMasterAsset().build(**kw)
    return json.loads(out[1])


def seed_master(tmp, proj, contents):
    """预置母版存档 — 模拟先前的 资产母版快照 入库历史."""
    st = open_store(tmp, proj)
    for c in contents:
        st.commit(name="seed", files={"资产母版_角色正面": ("", c)}, notes="测试预置")
    return st


def router_api(refs, storyboard):
    kw = {"目标视频模型": "全部生成", "视频时长_秒": 8, "画幅比例": "16:9 横屏", "帧率": 24,
          "核心数据包": "", "参考库JSON": refs, "分镜脚本": storyboard}
    out = DirectorMasterVideoRouter().build(**kw)
    return out, json.loads(out[6])


REFS4 = json.dumps({"参考图": {"角色正面": "a.png", "角色侧面": "b.png", "环境母版": "c.png", "道具母版": "d.png"},
                    "参考视频": {}, "统计": {"参考图总数": 4, "参考视频总数": 0}}, ensure_ascii=False)


def main():
    print("=" * 60)
    print("  批次6 D5/D6 — 资产派生谱系 + slot 接线 测试")
    print("=" * 60)

    # ---------- T0 RETURN 7 路冻结 ----------
    print("\n--- T0 video_router RETURN 冻结 ---")
    check("T0 RETURN_TYPES 7 路", len(DirectorMasterVideoRouter.RETURN_TYPES) == 7)
    check("T0 RETURN_NAMES 末路=综合API请求JSON",
          DirectorMasterVideoRouter.RETURN_NAMES[-1] == "综合API请求JSON")

    # ---------- T1 无谱系键 → 旧消费方零影响 ----------
    print("\n--- T1 参考库JSON 无 谱系 键 (v1 兼容) ---")
    with tempfile.TemporaryDirectory() as tmp:
        lib = asset_ref_json({"资产模式": "角色设定", "项目名": "谱系T1", "核心数据包": ""})
        check("T1 参考库JSON 可解析 (旧消费方)", isinstance(lib, dict))
        check("T1 无 谱系 键", "谱系" not in lib, str(list(lib.keys())))
        check("T1 既有键集合零漂移",
              set(lib.keys()) == {"项目", "导演", "视觉风格", "参考图", "参考视频", "统计"},
              str(sorted(lib.keys())))
        check("T1 空参考库 (无母版无派生)", lib["统计"]["参考图总数"] == 0)

    # ---------- T2 母版→派生 完整锚定 ----------
    print("\n--- T2 母版→派生 谱系记录 + 完整锚定 ---")
    with tempfile.TemporaryDirectory() as tmp:
        proj = "谱系T2"
        st = seed_master(tmp, proj, ["faceA.png"])
        vid1 = st.data["order"][0]
        lib = asset_ref_json({"资产模式": "角色设定", "项目名": proj, "核心数据包": "", "输出目录": tmp,
                              "参考图_角色正面": "faceA.png", "参考图_角色侧面": "sideA.png"})
        lin = lib.get("谱系", {})
        side = lin.get("角色侧面", {})
        check("T2 谱系块存在且含派生条目", side.get("类型") == "派生" and side.get("母版") == "角色正面",
              str(side))
        check("T2 派生状态 完整锚定", side.get("状态") == "完整锚定", str(side.get("状态")))
        check("T2 库引用=真实版本id", side.get("库引用") == vid1, f"{side.get('库引用')} != {vid1}")
        front = lin.get("角色正面", {})
        check("T2 母版条目 完整锚定+库引用", front.get("状态") == "完整锚定" and front.get("库引用") == vid1,
              str(front))
        back = lin.get("角色背面", {})
        check("T2 背面未提供 → 派生缺失", back.get("状态") == "派生缺失", str(back))
        check("T2 稳定内容零重复入库 (台账仍 1 版)", len(st.data["order"]) == 1,
              f"order={len(st.data['order'])}")

    # ---------- T3 母版已更新待同步 ----------
    print("\n--- T3 存母版→更新母版 → 母版已更新待同步 ---")
    with tempfile.TemporaryDirectory() as tmp:
        proj = "谱系T3"
        st = seed_master(tmp, proj, ["faceA.png", "faceB.png"])
        lib = asset_ref_json({"资产模式": "角色设定", "项目名": proj, "核心数据包": "", "输出目录": tmp,
                              "参考图_角色正面": "faceB.png", "参考图_角色侧面": "sideB.png"})
        lin = lib.get("谱系", {})
        side = lin.get("角色侧面", {})
        check("T3 派生状态 母版已更新待同步", side.get("状态") == "母版已更新待同步", str(side))
        st = open_store(tmp, proj)  # 重开: 构建内的确认快照已落盘, 旧句柄不感知
        check("T3 库引用指向最新存档", side.get("库引用") == st.data["order"][-1], str(side.get("库引用")))
        check("T3 说明含变更语义", "变更" in (side.get("说明") or ""), str(side.get("说明")))
        back = lin.get("角色背面", {})
        check("T3 背面派生缺失", back.get("状态") == "派生缺失", str(back))
        check("T3 滞后确认快照不再重复入库 (台账 2 版, LOW-6)", len(st.data["order"]) == 2,
              f"order={len(st.data['order'])}")

    # ---------- T4 无库 → 母版缺失 诚实降级 ----------
    print("\n--- T4 无库场景 → 母版缺失 (不炸不伪造) ---")
    with tempfile.TemporaryDirectory() as tmp:
        proj = "谱系T4"
        lib = asset_ref_json({"资产模式": "角色设定", "项目名": proj, "核心数据包": "", "输出目录": tmp,
                              "参考图_角色正面": "faceA.png", "参考图_角色侧面": "sideA.png"})
        side = lib.get("谱系", {}).get("角色侧面", {})
        check("T4 派生状态 母版缺失", side.get("状态") == "母版缺失", str(side))
        check("T4 说明在场 (原因可读)", bool(side.get("说明")), str(side))
        check("T4 未伪造库引用", "库引用" not in side, str(side))
        st = open_store(tmp, proj)
        check("T4 首次锚定快照真实入库 (台账 1 版)", len(st.data["order"]) == 1,
              f"order={len(st.data['order'])}")
        front = lib.get("谱系", {}).get("角色正面", {})
        check("T4 首次母版 母版缺失态 (无先前存档可比对, 库引用=本次快照, 说明保留首次原因)",
              front.get("状态") == "母版缺失" and bool(front.get("库引用"))
              and "首次" in (front.get("说明") or ""), str(front))

    # ---------- T5 派生在场母版缺 → 母版缺失, 无库不落盘 ----------
    print("\n--- T5 派生在场母版缺 → 母版缺失 ---")
    with tempfile.TemporaryDirectory() as tmp:
        lib = asset_ref_json({"资产模式": "角色设定", "项目名": "谱系T5", "核心数据包": "", "输出目录": tmp,
                              "参考图_角色侧面": "sideA.png"})
        side = lib.get("谱系", {}).get("角色侧面", {})
        check("T5 状态 母版缺失", side.get("状态") == "母版缺失", str(side))
        check("T5 说明写明母版参考未提供", "母版参考 角色正面 未提供" in (side.get("说明") or ""),
              str(side.get("说明")))
        check("T5 无母版可入库 → 版本库不落盘", not os.path.isdir(os.path.join(tmp, "_versions")),
              "._versions 不应存在")

    # ---------- T6 HellGrind 锁定 → 首次母版 母版缺失态 ----------
    print("\n--- T6 HellGrind锁定 → 母版条目 ---")
    with tempfile.TemporaryDirectory() as tmp:
        lib = asset_ref_json({"资产模式": "HellGrind资产库", "项目名": "谱系T6", "核心数据包": "",
                              "输出目录": tmp, "HellGrind锁定": True})
        hg = lib.get("谱系", {}).get("HellGrind:@roco", {})
        check("T6 首次母版 母版缺失态 (库引用=真实快照, 说明保留首次原因)",
              hg.get("状态") == "母版缺失" and hg.get("类型") == "母版"
              and "首次" in (hg.get("说明") or ""), str(hg))
        check("T6 库引用=真实快照版本", bool(hg.get("库引用")) and str(hg.get("库引用")).startswith("v_"),
              str(hg.get("库引用")))
        check("T6 未选状态变体 → 无派生条目",
              not any(k.startswith("HellGrind:@roco@") for k in lib.get("谱系", {})),
              str(list(lib.get("谱系", {}).keys())))

    # ---------- T6b 变更+快照入库失败 → 母版 母版已更新待同步 (R2 MED-1new) ----------
    print("\n--- T6b 变更+入库失败 → 母版待同步 (不虚标完整锚定) ---")
    with tempfile.TemporaryDirectory() as tmp:
        proj = "谱系T6b"
        seed_master(tmp, proj, ["faceA.png", "faceB.png"])
        import aggregator.asset_master as _am
        _orig_commit = _am._lineage_commit
        _am._lineage_commit = lambda store, files: ""   # 注入: 快照入库失败
        try:
            lib = asset_ref_json({"资产模式": "角色设定", "项目名": proj, "核心数据包": "", "输出目录": tmp,
                                  "参考图_角色正面": "faceC.png", "参考图_角色侧面": "sideC.png"})
        finally:
            _am._lineage_commit = _orig_commit
        lin = lib.get("谱系", {})
        front = lin.get("角色正面", {})
        check("T6b 变更+入库失败 → 母版 母版已更新待同步 (状态与说明一致)",
              front.get("状态") == "母版已更新待同步"
              and "入库失败" in (front.get("说明") or ""), str(front))
        check("T6b 同条件派生行同标签 (待同步)",
              lin.get("角色侧面", {}).get("状态") == "母版已更新待同步", str(lin.get("角色侧面")))

    # ---------- T7 参考槽位 → 槽位序排列 + 槽位映射 ----------
    print("\n--- T7 参考槽位 → reference_images 槽位序排列 ---")
    sb7 = json.dumps({"contract_version": 2, "分镜数": 2, "分镜表": [
        {"镜号": 1, "时长": "4s", "AIGC提示词": "雨夜街头, 【参考@3】 与 【参考@1】", "参考槽位": [3, 1]},
        {"镜号": 2, "时长": "4s", "AIGC提示词": "便利店特写", "参考槽位": [1]},
    ]}, ensure_ascii=False)
    out, api = router_api(REFS4, sb7)
    refs_arr = api["Seedance 2.5"]["body"]["reference_images"]
    check("T7 reference_images 槽位序 (升序 [1,3] → [b,d])", refs_arr == ["b.png", "d.png"], str(refs_arr))
    sm = api.get("槽位映射", {})
    check("T7 槽位映射折入载荷", isinstance(sm, dict) and sm.get("协议") == "契约v2·参考槽位", str(sm)[:120])
    check("T7 映射 1:1 (槽位→数组下标)", sm.get("映射") == [
        {"槽位": 1, "标签": "参考@1", "数组下标": 0, "媒体": "b.png"},
        {"槽位": 3, "标签": "参考@3", "数组下标": 1, "媒体": "d.png"}], str(sm.get("映射")))
    check("T7 无缺失", sm.get("缺失跳过") == [], str(sm.get("缺失跳过")))
    check("T7 镜头槽位逐镜记录", sm.get("镜头槽位") == [
        {"镜号": 1, "参考槽位": [3, 1]}, {"镜号": 2, "参考槽位": [1]}], str(sm.get("镜头槽位")))
    check("T7 prompt标签=[1,3] 与槽位双射 (无核对告警)",
          sm.get("prompt标签") == [1, 3] and "标签核对" not in sm, str(sm.get("prompt标签")))

    # ---------- T8 缺槽 → 诚实跳过 + 说明 ----------
    print("\n--- T8 缺槽 → 诚实跳过 + 槽位映射说明 ---")
    refs2 = json.dumps({"参考图": {"角色正面": "a.png", "角色侧面": "b.png"},
                        "参考视频": {}, "统计": {"参考图总数": 2, "参考视频总数": 0}}, ensure_ascii=False)
    sb8 = json.dumps({"contract_version": 2, "分镜数": 1, "分镜表": [
        {"镜号": 1, "时长": "4s", "AIGC提示词": "街头 【参考@0】", "参考槽位": [0, -1, 5]},
    ]}, ensure_ascii=False)
    _, api = router_api(refs2, sb8)
    refs_arr = api["Seedance 2.5"]["body"]["reference_images"]
    check("T8 仅在场槽位注入 (槽位0)", refs_arr == ["a.png"], str(refs_arr))
    sm = api.get("槽位映射", {})
    miss = sm.get("缺失跳过", [])
    check("T8 缺槽逐槽记录 (-1 与 5)", [m.get("槽位") for m in miss] == [-1, 5], str(miss))
    check("T8 缺槽条目写明跳过原因", all(m.get("跳过") and m.get("处理") for m in miss), str(miss))
    check("T8 载荷级说明在场", "已诚实跳过" in (sm.get("说明") or ""), str(sm.get("说明")))
    check("T8 未伪造占位 (数组长度=在场槽位数)", len(refs_arr) == 1, str(refs_arr))
    check("T8 标签集合不一致 → 如实记录核对告警", "标签核对" in sm, str(sm.get("标签核对")))

    # ---------- T8b 混合合法/非法槽位元素 → 非法元素如实记录 (R2 LOW-1new) ----------
    print("\n--- T8b 混合槽位元素 → 损坏元素记录 ---")
    sb8b = json.dumps({"contract_version": 2, "分镜数": 1, "分镜表": [
        {"镜号": 1, "时长": "4s", "AIGC提示词": "街头 【参考@0】", "参考槽位": [0, "x", True]},
    ]}, ensure_ascii=False)
    _, api = router_api(refs2, sb8b)
    sm = api.get("槽位映射", {})
    check("T8b 合法元素仍入计划 (仅槽位0注入)", api["Seedance 2.5"]["body"]["reference_images"] == ["a.png"],
          str(api["Seedance 2.5"]["body"]["reference_images"]))
    check("T8b 非法元素逐镜记录 (损坏元素 ['x', True], 不静默丢弃)",
          sm.get("镜头槽位") == [{"镜号": 1, "参考槽位": [0], "损坏元素": ["x", True],
                              "处理": "非法元素未入计划 (双射校验归契约层, 此处如实记录)"}],
          str(sm.get("镜头槽位")))

    # ---------- T9 无 参考槽位 (v1) → 原路径零变化 ----------
    print("\n--- T9 v1 分镜 (无参考槽位) → 原路径零变化 ---")
    sb_v1 = json.dumps({"contract_version": 1, "分镜数": 1, "分镜表": [
        {"镜号": 1, "时长": "4s", "AIGC提示词": "雨夜街头"}]}, ensure_ascii=False)
    _, api = router_api(REFS4, sb_v1)
    check("T9 无 槽位映射 键", "槽位映射" not in api, str(list(api.keys())))
    check("T9 reference_images 保持库序",
          api["Seedance 2.5"]["body"]["reference_images"] == ["a.png", "b.png", "c.png", "d.png"],
          str(api["Seedance 2.5"]["body"]["reference_images"]))
    _, api2 = router_api(REFS4, "纯文本分镜: 雨夜街头 6 镜")
    check("T9 纯文本分镜同样零变化",
          "槽位映射" not in api2 and
          api2["Seedance 2.5"]["body"]["reference_images"] == ["a.png", "b.png", "c.png", "d.png"])

    # ---------- T10 archive 角色DNA档 非空 → 存档往返 ----------
    print("\n--- T10 archive 角色DNA档 非空 → 存档往返 ---")
    dna = json.dumps({"dna_version": 1,
                      "维度": {"眼型": "丹凤眼", "脸型": "瓜子脸", "发型": "高马尾", "发色": "黑",
                              "肤色": "麦色", "体态": "高挑", "标志着装": "深蓝工装", "气质锚": "干练"},
                      "promptBlock": "丹凤眼, 瓜子脸, 高马尾黑发, 麦色皮肤, 深蓝工装",
                      "抽象词": []}, ensure_ascii=False)
    with tempfile.TemporaryDirectory() as tmp:
        kw = {"归档模式": "自动保存全部资产", "项目名": "谱系T10", "输出目录": tmp,
              "剧本": "内. 夜. 便利店\n动作: 雨夜", "核心数据包": "", "角色DNA档": dna}
        res = DirectorMasterArchive().build(**kw)
        manifest = json.loads(res[1])
        vid = manifest.get("版本")
        check("T10 版本已提交", bool(vid), str(manifest)[:120])
        st = open_store(tmp, "谱系T10")
        v = st.get(vid) or {}
        check("T10 commit files 含 角色DNA 独立键", "角色DNA" in v.get("files", {}),
              str(list(v.get("files", {}).keys())))
        sha = v.get("files", {}).get("角色DNA", {}).get("sha256", "")
        check("T10 blob 逐字回读一致", st.data.get("blobs", {}).get(sha) == dna, "blob != 输入")
        dna_files = [f for f in manifest.get("已保存文件", []) if "角色DNA" in f]
        check("T10 磁盘独立文件落盘 (TXT+JSON)", len(dna_files) == 2, str(dna_files))
        txt_ok = json_ok = False
        for f in dna_files:
            with open(os.path.join(tmp, f), "r", encoding="utf-8") as fh:
                content = fh.read()
            if f.endswith(".txt"):
                txt_ok = content == dna
            elif f.endswith(".json"):
                json_ok = json.loads(content).get("data") == json.loads(dna)
        check("T10 TXT 原文逐字节往返", txt_ok)
        check("T10 JSON 结构化往返 (data=原DNA)", json_ok)

    # ---------- T11 archive 角色DNA档 空 → 既有行为零变化 ----------
    print("\n--- T11 archive 角色DNA档 空 → 既有 commit 零变化 ---")
    with tempfile.TemporaryDirectory() as tmp:
        kw = {"归档模式": "自动保存全部资产", "项目名": "谱系T11", "输出目录": tmp,
              "剧本": "内. 夜. 便利店\n动作: 雨夜", "核心数据包": ""}
        res = DirectorMasterArchive().build(**kw)
        manifest = json.loads(res[1])
        vid = manifest.get("版本")
        check("T11 版本照常提交", bool(vid))
        st = open_store(tmp, "谱系T11")
        v = st.get(vid) or {}
        check("T11 files 无 角色DNA 键", "角色DNA" not in v.get("files", {}),
              str(list(v.get("files", {}).keys())))
        check("T11 files 仅为既有资产集合 (剧本+核心数据, 空核心包落 {} 为既有行为)",
              set(v.get("files", {}).keys()) == {"剧本", "核心数据"},
              str(list(v.get("files", {}).keys())))
        check("T11 磁盘无 角色DNA 文件",
              not [f for f in manifest.get("已保存文件", []) if "角色DNA" in f],
              str(manifest.get("已保存文件")))

    print("\n" + "=" * 60)
    print(f"  结果: {PASS} PASS / {FAIL} FAIL")
    print("=" * 60)
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
