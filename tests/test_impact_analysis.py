# -*- coding: utf-8 -*-
"""
V16.7-MERGED D5 测试 — 修订影响面 compute_impact + Archive 版本提交接线
================================================================
不依赖 pytest:  python -X utf8 tests/test_impact_analysis.py
覆盖 (design_batch3.md §5 D5 验收):
  1. 无变化 → 全空 (changed_dims/affected/reasons 皆空)
  2. 改导演/情绪/场景 → 全链 (分镜表/AIGC提示词/音频/角色 四段)
  3. 改角色 DNA → 仅引用它的镜 (逐镜子串定位, 未引用镜不误伤)
  4. 改资产/道具 → 仅引用镜; 改时长 → 全部时序字段
  5. 未知维度 → "未建模维度" 诚实列出, 不猜测影响
  6. 分镜表逐镜差集 (内容变化/新增/移除/音频/时序派生段)
  7. 确定性: 两次调用结果逐字节一致; AI配置/项目名不影响内容链; 坏输入诚实报错
  8. Archive 接线实测: 版本提交对比上一版核心数据包, 交付 JSON 附 impact 段;
     首版无上一版 → 段缺席; 既有键零改变 (258/ten_rounds 红线)
退出码: 0 = 全部通过, 1 = 有失败
"""
import os
import sys
import json
import shutil
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

PASS = 0
FAIL = 0
ERRORS = []


def check(label, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
    else:
        FAIL += 1
        ERRORS.append("%s %s" % (label, detail))
        print("  [FAIL] %s %s" % (label, detail))


from aggregator.impact_analysis import compute_impact, _IMPACT_RULES  # noqa: E402


def base_pack():
    return {
        "_项目名": "影响面测试",
        "_导演风格": "王家卫式疏离",
        "_情绪基调": "孤独",
        "_场景描述": "雨夜便利店",
        "_成片时长": "60s",
        "_ai_api_key": "sk-test",
        "_关键道具": {"怀表": "金色, 齿轮外露", "打火机": "黄铜"},
        "角色": [
            {"名字": "林小满", "DNA": "短发, 红色风衣, 左手戴表"},
            {"名字": "陈默", "DNA": "高个, 黑框眼镜"},
        ],
        "分镜表": [
            {"镜号": 1, "时长": "3.0s", "首帧描述": "雨夜便利店门口 全景 林小满推门", "声音": "雨声"},
            {"镜号": 2, "时长": "2.5s", "首帧描述": "特写 怀表齿轮转动", "声音": "滴答"},
            {"镜号": 3, "时长": "4.0s", "首帧描述": "陈默在货架间回头", "声音": "环境音"},
        ],
    }


def copy_pack(p):
    return json.loads(json.dumps(p, ensure_ascii=False))


def test_no_change():
    old, new = base_pack(), base_pack()
    r = compute_impact(old, new)
    check("无变化-changed_dims空", r["changed_dims"] == [])
    check("无变化-affected空", r["affected"] == {})
    check("无变化-reasons空", r["reasons"] == [])
    r2 = compute_impact({}, {})
    check("空包无变化-全空", r2 == {"changed_dims": [], "affected": {}, "reasons": []})


def test_global_chain():
    old = base_pack()
    new = copy_pack(old)
    new["_导演风格"] = "韦斯·安德森对称"
    r = compute_impact(old, new)
    check("改导演-变化维度", "_导演风格" in r["changed_dims"])
    aff = r["affected"]
    check("改导演-全链四段齐", all(k in aff for k in ("分镜表", "AIGC提示词", "音频", "角色")))
    check("改导演-分镜表全镜头标注", any("全部镜头" in e and "3镜" in e for e in aff["分镜表"]))
    check("改导演-reasons全链", any("全链" in x for x in r["reasons"]))
    for dim in ("_情绪基调", "_场景描述"):
        o, n = base_pack(), base_pack()
        n[dim] = "变化后"
        rr = compute_impact(o, n)
        check("改%s→全链" % dim, all(k in rr["affected"] for k in ("分镜表", "AIGC提示词", "音频", "角色")))
    # 情绪/导演同改, reasons 每维度一条
    o, n = base_pack(), base_pack()
    n["_情绪基调"] = "压抑"
    n["_导演风格"] = "改"
    rm = compute_impact(o, n)
    check("多维度reasons逐条", len(rm["reasons"]) >= 2 and len(rm["changed_dims"]) == 2)


def test_character_refs():
    old = base_pack()
    new = copy_pack(old)
    new["角色"][0]["DNA"] = "长发, 蓝色风衣, 右手戴表"  # 林小满 DNA 变化
    r = compute_impact(old, new)
    check("改角色-变化维度", "角色" in r["changed_dims"])
    aff = r["affected"]
    check("改角色-仅引用镜1", aff["分镜表"] == ["镜1: 引用角色'林小满'"])
    check("改角色-提示词段同镜", aff["AIGC提示词"] == ["镜1: 引用角色'林小满'"])
    check("改角色-角色段标注DNA", any("林小满" in e and "DNA" in e for e in aff["角色"]))
    check("改角色-不误伤其他镜", not any("镜2" in e or "镜3" in e for e in aff["分镜表"]))
    check("改角色-非全链(无音频段)", "音频" not in aff)
    # 新增角色 (无镜引用) — 档案级, 诚实注明未找到引用镜
    o2, n2 = base_pack(), base_pack()
    n2["角色"].append({"名字": "新角色", "DNA": "白衬衫"})
    r2 = compute_impact(o2, n2)
    check("新增角色-角色段", any("新角色" in e for e in r2["affected"]["角色"]))
    check("新增角色-不猜测镜", "分镜表" not in r2["affected"]
          and any("未找到引用镜" in x for x in r2["reasons"]))


def test_asset_refs():
    old = base_pack()
    new = copy_pack(old)
    new["_关键道具"]["怀表"] = "金色, 齿轮外露, 表盘裂纹"
    r = compute_impact(old, new)
    check("改道具-变化维度", "_关键道具" in r["changed_dims"])
    aff = r["affected"]
    check("改道具-仅引用镜2", aff["分镜表"] == ["镜2: 引用资产'怀表'"])
    check("改道具-AIGC段同镜", "镜2: 引用资产'怀表'" in aff["AIGC提示词"])
    check("改道具-不误伤", not any("镜1" in e or "镜3" in e
                                   for e in aff["分镜表"] + aff["AIGC提示词"]))


def test_duration():
    old = base_pack()
    new = copy_pack(old)
    new["_成片时长"] = "90s"
    r = compute_impact(old, new)
    check("改时长-变化维度", "_成片时长" in r["changed_dims"])
    aff = r["affected"]
    check("改时长-时序段含总时长", "时序" in aff and any("总时长" in e for e in aff["时序"]))
    check("改时长-时序段含逐镜", any("时长/start/end" in e and "3镜" in e for e in aff["时序"]))
    check("改时长-不触发全链", "角色" not in aff and "分镜表" not in aff)


def test_unknown_dims():
    old = base_pack()
    new = copy_pack(old)
    new["_外星科技等级"] = "III级"  # 规则表外的新维度
    r = compute_impact(old, new)
    check("未知维度-列入changed", "_外星科技等级" in r["changed_dims"])
    check("未知维度-未建模段", any("_外星科技等级" in e for e in r["affected"]["未建模维度"]))
    check("未知维度-reasons不猜测", any("未建模" in x and "不猜测" in x for x in r["reasons"]))
    check("未知维度-不编造链影响",
          all(k not in r["affected"] for k in ("分镜表", "AIGC提示词", "音频", "角色", "时序")))


def test_storyboard_diff():
    old = base_pack()
    new = copy_pack(old)
    new["分镜表"][1]["时长"] = "5.0s"          # 镜2 时长变化
    new["分镜表"][1]["声音"] = "滴答+心跳"      # 镜2 音频字段变化
    new["分镜表"].append({"镜号": 4, "时长": "2.0s", "首帧描述": "收尾空镜"})
    del new["分镜表"][0]                        # 镜1 移除 (列表位置随删除变化, 按 镜号 识别)
    r = compute_impact(old, new)
    aff = r["affected"]
    sb = aff.get("分镜表", [])
    check("分镜差集-镜2内容变化", "镜2: 内容变化" in sb)
    check("分镜差集-镜4新增", "镜4: 新增镜" in sb)
    check("分镜差集-镜1移除", "镜1: 移除镜" in sb)
    check("分镜差集-镜2音频段", any("镜2" in e for e in aff.get("音频", [])))
    check("分镜差集-镜2时序段", any("镜2" in e for e in aff.get("时序", [])))
    check("分镜差集-未动镜不列", not any("镜3" in e for e in sb))
    check("分镜差集-reasons统计", any("新增1/移除1/修改1" in x for x in r["reasons"]))


def test_determinism_and_meta():
    old, new = base_pack(), copy_pack(base_pack())
    new["_导演风格"] = "变体"; new["_关键道具"]["怀表"] = "银色"
    r1 = compute_impact(old, new)
    r2 = compute_impact(old, new)
    check("确定性-两次相等", r1 == r2)
    check("确定性-逐字节", json.dumps(r1, ensure_ascii=False, sort_keys=True)
          == json.dumps(r2, ensure_ascii=False, sort_keys=True))
    # AI 配置/项目名 — 元数据维度, 不影响内容链
    o, n = base_pack(), base_pack()
    n["_ai_api_key"] = "sk-other"
    rm = compute_impact(o, n)
    check("AI配置-不影响内容链", rm["affected"] == {}
          and any("不影响内容链" in x for x in rm["reasons"]))
    o2, n2 = base_pack(), base_pack()
    n2["_项目名"] = "新项目名"
    rm2 = compute_impact(o2, n2)
    check("项目名-不影响内容链", rm2["affected"] == {})
    # changed_dims 排序确定性
    o3, n3 = base_pack(), base_pack()
    n3["_情绪基调"] = "X"; n3["_导演风格"] = "Y"
    check("changed_dims已排序", compute_impact(o3, n3)["changed_dims"]
          == sorted(compute_impact(o3, n3)["changed_dims"]))
    # 规则表条数固定 (报告口径)
    check("规则表条数=14", len(_IMPACT_RULES) == 14)
    # 坏输入诚实报错
    for bad in ("not-a-dict", None, 42, [1, 2]):
        try:
            compute_impact(bad, {})
            check("坏输入报错-%s" % type(bad).__name__, False, "(未抛错)")
        except ValueError:
            check("坏输入报错-%s" % type(bad).__name__, True)
        try:
            compute_impact({}, bad)
            check("坏输入报错-new-%s" % type(bad).__name__, False, "(未抛错)")
        except ValueError:
            check("坏输入报错-new-%s" % type(bad).__name__, True)


def test_archive_wiring():
    """Archive 接线实测: 版本提交对比上一版核心数据包 → 交付 JSON 附 impact 段."""
    from aggregator.archive_master import DirectorMasterArchive
    tmp = tempfile.mkdtemp(prefix="dm_impact_arch_")
    try:
        node = DirectorMasterArchive()
        proj = "影响面接线测试"
        pack1 = base_pack()
        kw1 = {"归档模式": "版本提交", "项目名": proj, "输出目录": tmp,
               "剧本": "接线测试剧本第一版",
               "核心数据包": json.dumps(pack1, ensure_ascii=False)}
        out1 = node.build(**kw1)
        meta1 = json.loads(out1[1])
        check("首版-impact段缺席", "impact" not in meta1)
        check("首版-既有键完好", all(k in meta1 for k in ("项目", "模式", "时间", "已保存文件", "版本")))
        pack2 = base_pack()
        pack2["_导演风格"] = "韦斯·安德森对称"
        pack2["角色"][0]["DNA"] = "长发, 蓝色风衣"
        kw2 = {"归档模式": "版本提交", "项目名": proj, "输出目录": tmp,
               "剧本": "接线测试剧本第二版",
               "核心数据包": json.dumps(pack2, ensure_ascii=False)}
        out2 = node.build(**kw2)
        meta2 = json.loads(out2[1])
        check("次版-impact段存在", "impact" in meta2)
        imp = meta2.get("impact", {})
        check("次版-impact结构三键", set(imp.keys()) == {"changed_dims", "affected", "reasons"})
        check("次版-导演维度命中", "_导演风格" in imp["changed_dims"])
        check("次版-全链段存在", "分镜表" in imp["affected"] and "角色" in imp["affected"])
        check("次版-既有键零改变", all(k in meta2 for k in meta1.keys())
              and all(meta2[k] == meta1[k] for k in ("项目", "模式")))
        # 第三版: 核心包无变化 → impact 为空结果 (诚实), 既有键不变
        kw3 = {"归档模式": "版本提交", "项目名": proj, "输出目录": tmp,
               "剧本": "接线测试剧本第三版",
               "核心数据包": json.dumps(pack2, ensure_ascii=False)}
        meta3 = json.loads(node.build(**kw3)[1])
        check("三版-无变化impact空", "impact" in meta3
              and meta3["impact"]["changed_dims"] == [] and meta3["impact"]["affected"] == {})
        # 核心数据包缺席 → 不报错, impact 段缺席
        kw4 = {"归档模式": "版本提交", "项目名": proj + "无包", "输出目录": tmp,
               "剧本": "只有剧本"}
        meta4 = json.loads(node.build(**kw4)[1])
        check("无核心包-不报错无impact", "impact" not in meta4)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    print("--- 无变化→空 ---")
    test_no_change()
    print("--- 全链规则 ---")
    test_global_chain()
    print("--- 角色引用 ---")
    test_character_refs()
    print("--- 资产引用 ---")
    test_asset_refs()
    print("--- 时长规则 ---")
    test_duration()
    print("--- 未知维度 ---")
    test_unknown_dims()
    print("--- 分镜逐镜差集 ---")
    test_storyboard_diff()
    print("--- 确定性/元数据/坏输入 ---")
    test_determinism_and_meta()
    print("--- Archive 接线 ---")
    test_archive_wiring()
    print("\n" + "=" * 60)
    print("  结果: %d PASS / %d FAIL" % (PASS, FAIL))
    if ERRORS:
        for e in ERRORS[:20]:
            print("  -", e)
    print("=" * 60)
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
