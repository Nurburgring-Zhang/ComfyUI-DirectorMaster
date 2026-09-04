# -*- coding: utf-8 -*-
"""pack_registry: dm_pack.json 插件包注册表 (批次5 生态层, V17.1.0)。

dm_pack 声明六字段全必填: pack_id / version / min_dm_version / dependencies /
tags / entry。三道闸缺一不可 (fail loud, 不静默跳过):
  1. 字段闸 — 六字段缺失/类型非法 → errors 显式列出, 拒绝载入;
  2. 版本闸 — min_dm_version > 当前 DM 版本 (或非 semver 串) → 拒绝载入;
  3. 依赖闸 — dependencies 指向未注册包 → 拒绝载入 (依赖链不动点收敛)。
另含 pack_id 冲突检测与 entry 文件存在校验。

纯函数纪律: 无随机/无时间戳/无 locale/无 dict 迭代序依赖 (目录枚举 sorted +
排序显式 key)。stdlib-only, 零第三方依赖。思想层独立重写 (xed-editor dm_pack
零代码借鉴)。
"""
import json
import os

# 当前 DM 版本 (生态层 additive 收官批 V17.1.0); 版本闸基准, 硬编码防循环依赖
CURRENT_DM_VERSION = "17.1.0"

# dm_pack.json 六必填字段 (设计冻结 §1 builder-p1, 顺序固定)
REQUIRED_FIELDS = ("pack_id", "version", "min_dm_version", "dependencies", "tags", "entry")

_MANIFEST_NAME = "dm_pack.json"

_ASCII_DIGITS = frozenset("0123456789")


def _parse_semver(text):
    """semver 前缀解析 -> (major, minor, patch); 非法串 -> None。

    三段全数值才认; 预发布段 (-) 与构建段 (+) 后缀取前缀比较
    (如 "17.1.0-rc1" 按 (17, 1, 0) 计)。诚实拦截, 不引 packaging 库。
    """
    if not isinstance(text, str):
        return None
    core = text.strip().split("-", 1)[0].split("+", 1)[0]
    parts = core.split(".")
    if len(parts) != 3:
        return None
    out = []
    for p in parts:
        if not p or any(c not in _ASCII_DIGITS for c in p):
            return None
        out.append(int(p))
    return (out[0], out[1], out[2])


def semver_ok(min_dm_version, current):
    """版本兼容判定: min_dm_version <= current 时兼容 (True)。

    任一端非 semver 串 -> False (诚实拦截, 宁拒勿放)。
    """
    lo = _parse_semver(min_dm_version)
    hi = _parse_semver(current)
    if lo is None or hi is None:
        return False
    return lo <= hi


def load_pack(pack_dir):
    """解析单个包目录的 dm_pack.json -> (pack dict, errors)。

    六字段全必填校验 (缺失逐个显式列出) + 基本类型校验 (str / str 列表,
    皆不静默强转)。任何失败 -> (None, errors), errors 逐条自包含可读。
    成功 -> (pack, []) 其中 pack 为六字段回读 + pack_dir 绝对路径。
    """
    errors = []
    pack_dir = str(pack_dir)
    if not os.path.isdir(pack_dir):
        return None, ["pack 目录不存在或不可读: %s" % pack_dir]
    manifest_path = os.path.join(pack_dir, _MANIFEST_NAME)
    if not os.path.isfile(manifest_path):
        return None, ["%s 缺失 (pack 目录: %s)" % (_MANIFEST_NAME, pack_dir)]
    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            raw = f.read()
    except OSError as exc:
        return None, ["%s 读取失败: %s" % (manifest_path, exc)]
    try:
        data = json.loads(raw)
    except ValueError as exc:
        return None, ["%s 非合法 JSON: %s" % (manifest_path, exc)]
    if not isinstance(data, dict):
        return None, ["%s 顶层必须是 JSON 对象 (dict)" % manifest_path]

    missing = [k for k in REQUIRED_FIELDS if k not in data]
    if missing:
        return None, ["%s 缺少必填字段: %s" % (manifest_path, ", ".join(missing))]

    bad_types = []
    for k in ("pack_id", "version", "min_dm_version", "entry"):
        if not isinstance(data[k], str) or not data[k]:
            bad_types.append(k)
    deps = data["dependencies"]
    if not isinstance(deps, list) or not all(isinstance(x, str) for x in deps):
        bad_types.append("dependencies")
    tags = data["tags"]
    if not isinstance(tags, list) or not all(isinstance(x, str) for x in tags):
        bad_types.append("tags")
    if bad_types:
        return None, ["%s 字段类型非法 (须为非空 str / str 列表): %s"
                      % (manifest_path, ", ".join(bad_types))]

    pack = {
        "pack_id": data["pack_id"],
        "version": data["version"],
        "min_dm_version": data["min_dm_version"],
        "dependencies": list(deps),
        "tags": list(tags),
        "entry": data["entry"],
        "pack_dir": os.path.abspath(pack_dir),
    }
    return pack, []


def _candidate_pack_dirs(search_dirs, errors):
    """枚举候选包目录 (去重, sorted 确定性)。

    两级有界扫描, 对齐存储布局 <out_dir>/eco/packs/<pack_id>/dm_pack.json:
      - 搜索目录各子目录含 dm_pack.json -> 直接是包目录 (doctor 默认
        <仓库根>/eco/packs 直传即此形态);
      - 子目录名为 packs 时下钻一层 (聚合门面默认传 <out_dir>/eco 即此形态)。
    搜索目录不存在 -> 跳过 (无 packs 目录 -> 空结果不报错, 验收①)。
    """
    candidates = []
    seen = set()
    if search_dirs is None:
        return candidates
    if isinstance(search_dirs, (str, bytes, os.PathLike)):
        search_dirs = [search_dirs]
    for d in search_dirs:
        d = str(d)
        if not os.path.isdir(d):
            continue
        try:
            names = sorted(os.listdir(d))
        except OSError as exc:
            errors.append("搜索目录不可枚举: %s (%s)" % (d, exc))
            continue
        for name in names:
            sub = os.path.join(d, name)
            if not os.path.isdir(sub):
                continue
            if os.path.isfile(os.path.join(sub, _MANIFEST_NAME)):
                key = os.path.abspath(sub)
                if key not in seen:
                    seen.add(key)
                    candidates.append(sub)
                continue
            if name == "packs":
                # sub 即 packs 目录, 包目录直接在其下一层
                try:
                    inner_names = sorted(os.listdir(sub))
                except OSError:
                    continue
                for inner in inner_names:
                    inner_dir = os.path.join(sub, inner)
                    if os.path.isdir(inner_dir) and os.path.isfile(
                            os.path.join(inner_dir, _MANIFEST_NAME)):
                        key2 = os.path.abspath(inner_dir)
                        if key2 not in seen:
                            seen.add(key2)
                            candidates.append(inner_dir)
    return candidates


def register_packs(search_dirs):
    """扫描 search_dirs 下各包目录的 dm_pack.json -> registry{ok, packs, errors}。

    逐包四查: 字段缺失 / 版本不兼容 / entry 文件不存在 / pack_id 冲突;
    再做依赖图校验 (dependencies 指向未注册包 -> err, 依赖链不动点收敛,
    上游被拒则下游一并拒绝)。任何负样本 -> errors 显式列出且该包拒绝载入
    (fail loud 不静默跳过); 其余合规包照常注册。结果排序显式 key
    (packs 按 pack_id, 目录枚举 sorted) 保证同输入两次调用结果一致。
    无 packs 目录/目录为空 -> {ok: True, packs: [], errors: []} (不报错)。
    """
    errors = []
    candidates = _candidate_pack_dirs(search_dirs, errors)

    # 阶段1: 逐包 字段闸 + 版本闸 + entry 文件存在校验
    provisional = []
    for cand in candidates:
        pack, lerrs = load_pack(cand)
        if lerrs:
            errors.extend(lerrs)
            continue
        if not semver_ok(pack["min_dm_version"], CURRENT_DM_VERSION):
            errors.append("pack '%s' 版本不兼容: min_dm_version=%s 高于当前 DM 版本 %s (拒绝载入)"
                          % (pack["pack_id"], pack["min_dm_version"], CURRENT_DM_VERSION))
            continue
        entry_path = os.path.join(cand, pack["entry"])
        if not os.path.isfile(entry_path):
            errors.append("pack '%s' entry 文件不存在: %s (拒绝载入)"
                          % (pack["pack_id"], entry_path))
            continue
        provisional.append(pack)

    # 阶段2: pack_id 冲突检测 (同 id 先到先得, 后到者拒绝; 目录枚举已 sorted 保确定)
    kept = []
    claimed = {}
    for pack in provisional:
        pid = pack["pack_id"]
        if pid in claimed:
            errors.append("pack_id 冲突: '%s' 已由 %s 注册, 拒绝载入重复包 (%s)"
                          % (pid, claimed[pid], pack["pack_dir"]))
        else:
            claimed[pid] = pack["pack_dir"]
            kept.append(pack)

    # 阶段3: 依赖图校验 (不动点: 任一依赖不在已注册集合 -> 拒, 链式传导)
    accepted = kept
    changed = True
    while changed:
        changed = False
        ids = {p["pack_id"] for p in accepted}
        remaining = []
        for pack in accepted:
            missing_deps = sorted({d for d in pack["dependencies"] if d not in ids})
            if missing_deps:
                errors.append("pack '%s' 依赖未注册包: %s (拒绝载入)"
                              % (pack["pack_id"], ", ".join(missing_deps)))
                changed = True
            else:
                remaining.append(pack)
        accepted = remaining

    packs = sorted(accepted, key=lambda p: p["pack_id"])
    return {"ok": not errors, "packs": packs, "errors": errors}
