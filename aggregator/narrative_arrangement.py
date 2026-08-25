# -*- coding: utf-8 -*-
"""
aggregator/narrative_arrangement.py — V16.1 叙事编排引擎
==========================================================
把「节拍时序」重排为「银幕时序」: 正叙/倒叙(结果先行)/穿插倒叙/穿插乱叙/循环叙事,
叠加 单线/双线/三线/POV 的线索交织。全部确定性 (seed 哈希驱动), 同输入同输出。

设计依据 (真实影片语法):
  倒叙(结果先行)  — in medias res: 先给结果, 观众的问题从"会发生什么"变成"为什么会这样"
  穿插倒叙        — 现在主轴 + 情感谷峰处闪回 (黑夜/中点/转折之后), 闪回后必回锚
  穿插乱叙        — 碎片叙事 (低俗小说/记忆碎片式): 钩子开场固定, 中段多时间线打散, 高潮收拢
  循环叙事        — 终点即起点 (前目的地/星际穿越式): 末场置首, 意义反转
  双线/三线交织   — A/B(/C) 线每 2-3 场一切, 交汇场合流 (巴别塔/撞车式)

操作顺序: 线索分配 → 线间交织(双/三线) → 时间编排 → 字段写回。
先交织后时移, 保证倒叙开场/循环首尾等时间操作是最终顺序, 不被交织破坏。

输出:
  arrange_scenes(scenes, arrangement, narrative_mode, seed)
      -> (ordered_scenes, plan)
      scenes: feature_film_engine.generate_feature_scenes 的场次 dict 列表
      ordered_scenes: 重排后的场次列表, 每场新增字段:
          screen_order/story_order/timeline/line/pov/arrangement_note
      plan: {方式, 叙事结构, 时间线图谱, 线索图谱, 导演批注, 字幕位}
"""
import hashlib as _hashlib
import random as _random

ARRANGEMENT_MODES = [
    "跟随叙事结构", "正叙", "倒叙(结果先行)", "穿插倒叙", "穿插乱叙", "循环叙事(首尾相扣)",
]

NARRATIVE_LINE_MODES = ["单线", "双线并行", "三线交织", "POV切换", "非线性"]

# ============================================================
# 工具
# ============================================================

def _seeded_rng(seed):
    return _random.Random(int(_hashlib.md5(str(seed).encode("utf-8", "replace")).hexdigest(), 16) % (2 ** 32))


def _tension(sc):
    try:
        return int(sc.get("tension_level", 5))
    except Exception:
        return 5


def _sf(sc):
    return str(sc.get("story_function", "") or "")


def _is_memory_scene(sc):
    s = _sf(sc)
    return any(k in s for k in ("闪回", "记忆", "回忆", "过去", "旧日", "当年"))


def _is_anchor_scene(sc):
    """情感谷峰锚点 — 闪回插在这些场之后最有戏剧价值."""
    s = _sf(sc)
    return any(k in s for k in ("黑夜", "中点", "转折", "失去一切", "灵魂"))


def _is_confluence_scene(sc):
    s = _sf(sc)
    return any(k in s for k in ("交汇", "碰撞", "合流", "撞击", "汇聚", "A+B"))


def _is_hook_scene(sc):
    s = _sf(sc)
    return any(k in s for k in ("开场", "钩子", "悬念", "in medias"))


def _is_climax_scene(sc):
    s = _sf(sc)
    return any(k in s for k in ("高潮", "终局", "对决", "决战"))


# ============================================================
# 线索分配 (单线/双线/三线/POV)
# ============================================================

def assign_lines(scenes, narrative_mode):
    """给每场分配 line/pov 标签. 优先读节拍生成器已写入的 A线/B线/视角 标记,
    没有时按确定性规则补充分配。返回 scenes (原地修改)."""
    mode = narrative_mode or "单线"
    n = len(scenes)
    if n == 0:
        return scenes

    # 1) 已有显式线标记 (dual_line/multi_line/pov 节拍生成器) → 直接读
    has_explicit = any(("A线" in _sf(sc)) or ("B线" in _sf(sc)) or ("C线" in _sf(sc))
                       or _sf(sc).startswith("视角") for sc in scenes)

    if mode == "单线":
        for sc in scenes:
            sc["line"] = "A"
            sc["pov"] = "全知"
        return scenes

    if has_explicit:
        for sc in scenes:
            s = _sf(sc)
            if s.startswith("视角A") or s.startswith("视角 A"):
                sc["line"], sc["pov"] = "A", "视角A"
                continue
            if s.startswith("视角B") or s.startswith("视角 B"):
                sc["line"], sc["pov"] = "B", "视角B"
                continue
            if s.startswith("视角C") or s.startswith("视角 C"):
                sc["line"], sc["pov"] = "C", "视角C"
                continue
            if "C线" in s:
                sc["line"] = "C"
            elif "B线" in s:
                sc["line"] = "B"
            elif "A线" in s:
                sc["line"] = "A"
            else:
                sc["line"] = "A"
            if _is_confluence_scene(sc):
                sc["line"] = "A+B" if mode == "双线并行" else "A+B+C"
            sc.setdefault("pov", "全知")
        return scenes

    # 2) 无显式标记 → 确定性分配 (中段交替, 首尾归主线, 交汇点合并)
    lines = ["A", "B"] if mode in ("双线并行", "POV切换", "非线性") else ["A", "B", "C"]
    confluence_idx = set()
    for i, sc in enumerate(scenes):
        if _is_confluence_scene(sc) or _is_climax_scene(sc):
            confluence_idx.add(i)
    for i, sc in enumerate(scenes):
        if i in confluence_idx:
            sc["line"] = "+".join(lines)
            sc["pov"] = "全知"
            continue
        # 首场与末两场归 A 线 (开头建立主线, 结尾收束)
        if i == 0 or i >= n - 2:
            sc["line"] = "A"
        else:
            sc["line"] = lines[(i - 1) % len(lines)]
        if mode == "POV切换":
            sc["pov"] = f"视角{sc['line']}"
        else:
            sc["pov"] = "全知"
    return scenes


# ============================================================
# 时间线分配
# ============================================================

def _base_timeline(sc):
    s = _sf(sc)
    if any(k in s for k in ("闪前", "未来")):
        return "未来·闪前"
    if _is_memory_scene(sc):
        return "过去·闪回"
    return "现在"


# ============================================================
# 五种编排 (notes 一律以 id(scene) 为键, 与位置无关)
# ============================================================

def _arrange_flashback_first(scenes, rng):
    """倒叙(结果先行): 高潮段置首 → 字幕回退 → 从起点时序推进 → 末场接回开场."""
    n = len(scenes)
    if n < 4:
        return list(scenes), {}
    # 在后 60% 里找张力最高场 (优先高潮场)
    start = max(1, int(n * 0.4))
    cand = list(range(start, n))
    climax_i = max(cand, key=lambda i: (_is_climax_scene(scenes[i]), _tension(scenes[i])))
    opener = scenes[climax_i]
    rest = [sc for i, sc in enumerate(scenes) if i != climax_i]
    ordered = [opener] + rest
    notes = {
        id(opener): "结果先行: 先给结局的碎片, 观众带着'为什么'进入故事",
        id(rest[-1]): "走到这里, 故事即将接回开场那一幕 — 最后一块拼图留给观众自己补",
    }
    # 时间线: 开场=现在·结局边缘; 字幕回退后从过去按时序推进
    opener["_tl_override"] = "现在·结局边缘"
    for sc in rest:
        sc["_tl_override"] = "过去" if sc is not rest[-1] else "过去·逼近开场"
    return ordered, notes


def _arrange_interleaved_flashback(scenes, rng):
    """穿插倒叙: 现在主轴 + 情感谷峰后插入闪回场."""
    n = len(scenes)
    if n < 5:
        return list(scenes), {}
    # 闪回候选: 记忆类场 优先; 不足则取前半低张力场
    mem_idx = [i for i, sc in enumerate(scenes) if _is_memory_scene(sc)]
    if len(mem_idx) < 2:
        low = [i for i, sc in enumerate(scenes)
               if i < n // 2 and _tension(sc) <= 4 and not _is_hook_scene(sc)
               and i not in mem_idx]
        mem_idx = mem_idx + low[:max(0, 2 - len(mem_idx))]
    mem_idx = sorted(set(mem_idx))[:3]
    if not mem_idx:
        return list(scenes), {}
    # 锚点: 黑夜/中点/转折 场
    anchors = [i for i, sc in enumerate(scenes) if _is_anchor_scene(sc)]
    if not anchors:
        anchors = [n // 2]
    ordered, notes = [], {}
    mem_set = set(mem_idx)
    anchor_queue = sorted(a for a in anchors if a not in mem_set)
    pending_flash = []
    for i, sc in enumerate(scenes):
        if i in mem_set:
            # 闪回场暂存, 等锚点后插入
            pending_flash.append(i)
            continue
        ordered.append(sc)
        if i in anchor_queue and pending_flash:
            fi = pending_flash.pop(0)
            notes[id(scenes[fi])] = "在情感谷峰后切入过去: 观众刚感到痛, 此刻最需要知道痛的来处"
            scenes[fi]["_tl_override"] = "过去·闪回"
            ordered.append(scenes[fi])
    # 未插完的闪回依次补在中点之后
    if pending_flash:
        mid = max(1, len(ordered) // 2)
        for fi in pending_flash:
            notes[id(scenes[fi])] = "插叙: 过去线在此浮出, 与现在线互相照亮"
            scenes[fi]["_tl_override"] = "过去·闪回"
            ordered.insert(mid, scenes[fi])
            mid += 1
    return ordered, notes


def _arrange_fragmented(scenes, rng):
    """穿插乱叙: 钩子开场固定 + 高潮收束固定 + 中段多时间线确定性打散.
    场次不足时退化为"现在/过去"两线碎片, 仍保证乱叙的拼图感."""
    n = len(scenes)
    if n < 4:
        return list(scenes), {}

    # 开场: 前 30% 里张力最高的钩子场 (至少前 2 场)
    head_zone = max(2, int(n * 0.3))
    hook_i = max(range(head_zone), key=lambda i: (_is_hook_scene(scenes[i]), _tension(scenes[i])))
    notes = {id(scenes[hook_i]): "乱叙开场: 把最有疑问的画面放在第一秒, 观众自己拼时间"}

    if n < 6:
        # 简化乱叙: opener + 中段切为 现在/过去 两桶并交织 + 收束场
        rest = [sc for i, sc in enumerate(scenes) if i != hook_i]
        # 后半部分标为过去·闪回, 前半为现在, 保持原序分桶
        split = max(1, len(rest) // 2)
        now_bucket = rest[:split]
        past_bucket = rest[split:]
        for sc in past_bucket:
            sc["_tl_override"] = "过去·闪回"
        # 交织: 现在 → 过去 → 现在 → 过去, 不丢场
        ordered_mid, pi = [], 0
        for i, sc in enumerate(now_bucket):
            ordered_mid.append(sc)
            if pi < len(past_bucket):
                ordered_mid.append(past_bucket[pi])
                pi += 1
        while pi < len(past_bucket):
            ordered_mid.append(past_bucket[pi])
            pi += 1
        return [scenes[hook_i]] + ordered_mid, notes

    # 结尾: 最后两场 (高潮+收束)
    tail = scenes[-2:]
    middle = [sc for i, sc in enumerate(scenes) if i != hook_i and i < n - 2]
    # 三时间线分桶: 按场次原序轮转分配 现在/过去/未来, 记忆类场强制过去线
    buckets = {"现在": [], "过去": [], "未来": []}
    cycle = ["现在", "过去", "现在", "未来"]
    for j, sc in enumerate(middle):
        if _is_memory_scene(sc):
            buckets["过去"].append(sc)
        elif "闪前" in _sf(sc) or "未来" in _sf(sc):
            buckets["未来"].append(sc)
        else:
            buckets[cycle[j % len(cycle)]].append(sc)
    # 轮转交织三桶, 同时间线不连续超过 2 场
    ordered_mid, last_tl, run = [], None, 0
    order_pool = ["现在", "过去", "未来"]
    while any(buckets[b] for b in order_pool):
        placed = False
        for b in order_pool:
            if not buckets[b]:
                continue
            if b == last_tl and run >= 2:
                continue
            sc = buckets[b].pop(0)
            sc["_tl_override"] = "过去·闪回" if b == "过去" else ("未来·闪前" if b == "未来" else "现在")
            ordered_mid.append(sc)
            last_tl, run = b, (run + 1 if b == last_tl else 1)
            placed = True
            break
        if not placed:
            for b in order_pool:
                if buckets[b]:
                    sc = buckets[b].pop(0)
                    sc["_tl_override"] = "过去·闪回" if b == "过去" else ("未来·闪前" if b == "未来" else "现在")
                    ordered_mid.append(sc)
                    last_tl, run = b, run + 1
                    break
    return [scenes[hook_i]] + ordered_mid + tail, notes


def _arrange_loop(scenes, rng):
    """循环叙事: 末场置首(终点即起点), 首场置尾(起点即终点)."""
    n = len(scenes)
    if n < 4:
        return list(scenes), {}
    opener, closer = scenes[-1], scenes[0]
    middle = scenes[1:-1]
    notes = {
        id(opener): "循环: 先把结局放在开头 — 观众以为看到了终点, 其实看到的是起点",
        id(closer): "循环: 走到这里才明白, 开头那一幕是这一切的结尾",
    }
    opener["_tl_override"] = "循环·终点即起点"
    closer["_tl_override"] = "循环·起点即终点"
    return [opener] + middle + [closer], notes


# ============================================================
# 双线/三线交织 (在线性时序上做 A/B(/C) 分段穿插)
# ============================================================

def _weave_lines(ordered, narrative_mode):
    """A/B(/C) 线每 2 场一切; 交汇场按其相对位置就地合流。
    POV/非线性/单线不做位置重排。"""
    if narrative_mode not in ("双线并行", "三线交织"):
        return ordered
    n = len(ordered)
    if n < 6:
        return ordered
    # 保序分组 (交汇场独立成组, 记住其原始位置)
    groups = {}
    order_of_lines = []
    for sc in ordered:
        ln = str(sc.get("line", "A"))
        if "+" in ln:
            key = f"X{len(order_of_lines)}"
            groups[key] = [sc]
            order_of_lines.append(key)
        else:
            key = ln[:1]
            if key not in groups:
                groups[key] = []
                order_of_lines.append(key)
            groups[key].append(sc)
    line_keys = [k for k in order_of_lines if not k.startswith("X")]
    x_pos = {k: i for i, k in enumerate(order_of_lines) if k.startswith("X")}
    if len(line_keys) < 2:
        return ordered
    result = []
    ptrs = {k: 0 for k in line_keys}
    chunk = 2
    li = 0
    total = sum(len(groups[k]) for k in order_of_lines)
    x_queue = sorted(x_pos.keys(), key=lambda k: x_pos[k])
    xi = 0
    while len(result) < total:
        # 交汇场到达其原始相对位置时插入
        if xi < len(x_queue):
            xk = x_queue[xi]
            if len(result) >= int((x_pos[xk] + 1) * total / max(len(order_of_lines), 1)):
                result.extend(groups[xk])
                xi += 1
                continue
        k = line_keys[li % len(line_keys)]
        taken = 0
        while ptrs[k] < len(groups[k]) and taken < chunk:
            result.append(groups[k][ptrs[k]])
            ptrs[k] += 1
            taken += 1
        if taken == 0:
            line_keys_left = [kk for kk in line_keys if ptrs[kk] < len(groups[kk])]
            if not line_keys_left:
                while xi < len(x_queue):
                    result.extend(groups[x_queue[xi]])
                    xi += 1
                break
            line_keys = line_keys_left
            li = 0
            continue
        li += 1
    return result


# ============================================================
# 导演批注 (叙事设计说明 — 为什么这样排)
# ============================================================

_NOTE_POOLS = {
    "正叙": [
        "按时间走, 不耍结构花活 — 这个故事的力量在积累, 观众和角色一起走过每一分钟, 谁也不提前知道答案。",
        "正叙不是平铺: 每一场都比上一场多知道一点, 信息差就是钩子, 情绪坡度靠场次密度控制。",
    ],
    "倒叙(结果先行)": [
        "先给结果。观众第一眼看到结局的碎片, 问题就从'会发生什么'变成'为什么会这样' — 悬念从情节层挪到因果层。",
        "开场即高潮的残片, 其余部分是倒着还债: 每个现在的细节都在回答开场那一幕的重量。",
    ],
    "穿插倒叙": [
        "现在线是脊柱, 闪回是肋骨 — 只在观众情感最需要的位置插过去: 痛感刚出现的下一秒, 给他看痛的来处。",
        "闪回不做信息补丁, 做情感注脚。每次回到过去, 都让现在线的某个动作获得第二层意思。",
    ],
    "穿插乱叙": [
        "时间打碎, 情绪保持连续。观众放弃'接下来呢', 开始问'这是为什么' — 拼图感就是这一版的观影快感。",
        "乱叙不是随机: 钩子开场钉住注意力, 高潮留在最后收网, 中段的碎片按情感引力而不是日历排序。",
    ],
    "循环叙事(首尾相扣)": [
        "终点即起点。最后一场放到最前, 观众以为看到的是结局, 看到最后才发现是开端 — 结构本身就是主题。",
        "故事是一个环: 开场的画面在结尾重现, 但意义已经反转。同一个画面, 两次阅读。",
    ],
    "跟随叙事结构": [
        "结构跟随所选叙事理论的原生节拍推进, 不在时间轴上额外动手 — 理论自带的顺序就是这一版的叙事立场。",
    ],
}

_LINE_NOTES = {
    "单线": "一条线走到底, 所有镜头服务同一个主角的同一个目标。",
    "双线并行": "A线管外部目标, B线管内部情感, 两线在中点与高潮两次合流 — 观众在切换中自己看出两条线的关系。",
    "三线交织": "三组人物各自独立推进, 只在命运交叉处相遇 — 撞击瞬间, 三条线互相解释。",
    "POV切换": "同一事件经不同视角折射, 每个视角都有自己的盲区, 真相由观众拼合。",
    "非线性": "时间线打乱重组, 情绪优先于时序。",
}


def arrangement_director_note(arrangement, narrative_mode, theory, mood, scenes):
    rng = _seeded_rng(f"note_{arrangement}_{narrative_mode}_{theory}_{mood}_{len(scenes)}")
    pool = _NOTE_POOLS.get(arrangement, _NOTE_POOLS["跟随叙事结构"])
    main = pool[rng.randrange(len(pool))]
    line_note = _LINE_NOTES.get(narrative_mode, "")
    # 时间线图谱
    tls = [str(sc.get("timeline", "现在")) for sc in scenes]
    tl_map = []
    for t in tls:
        if t not in tl_map:
            tl_map.append(t)
    # 线索图谱
    lines_seen = []
    for sc in scenes:
        ln = str(sc.get("line", "A"))
        if ln not in lines_seen:
            lines_seen.append(ln)
    return {
        "批注": main + (f" 线索设计: {line_note}" if line_note else ""),
        "时间线图谱": " / ".join(tl_map) if tl_map else "现在",
        "线索图谱": " × ".join(lines_seen) if lines_seen else "A",
    }


# ============================================================
# 主入口
# ============================================================

def arrange_scenes(scenes, arrangement="跟随叙事结构", narrative_mode="单线", seed=""):
    """对场次做叙事编排. 返回 (ordered_scenes, plan). 入参场次做浅拷贝, 不污染上游."""
    if not scenes:
        return [], {"方式": arrangement, "叙事结构": narrative_mode,
                    "时间线图谱": "现在", "线索图谱": "A", "导演批注": "", "字幕位": []}
    scenes = [dict(sc) for sc in scenes]  # 浅拷贝, 不污染上游
    rng = _seeded_rng(f"arrange_{seed}_{arrangement}_{narrative_mode}_{len(scenes)}")

    # 1) 线索分配
    assign_lines(scenes, narrative_mode)

    # 2) 线间交织 (双线/三线) — 先在线性时序上织好, 时间编排随后拥有最终顺序
    ordered = _weave_lines(list(scenes), narrative_mode)

    # 3) 时间编排
    arrangement = arrangement if arrangement in ARRANGEMENT_MODES else "跟随叙事结构"
    subtitle_slots = []
    notes = {}
    if arrangement == "正叙":
        pass  # ordered 保持交织后的时序
    elif arrangement == "倒叙(结果先行)":
        if len(ordered) >= 4:
            ordered, notes = _arrange_flashback_first(ordered, rng)
            subtitle_slots = [{"位置": 1, "字幕": _flashback_title_card(len(scenes), seed)}]
    elif arrangement == "穿插倒叙":
        ordered, notes = _arrange_interleaved_flashback(ordered, rng)
    elif arrangement == "穿插乱叙":
        ordered, notes = _arrange_fragmented(ordered, rng)
    elif arrangement == "循环叙事(首尾相扣)":
        ordered, notes = _arrange_loop(ordered, rng)
    # 跟随叙事结构: 保持节拍生成器原生顺序

    # 4) 写回字段
    story_pos = {id(sc): i for i, sc in enumerate(scenes)}
    for screen_i, sc in enumerate(ordered):
        sc["screen_order"] = screen_i + 1
        sc["story_order"] = story_pos.get(id(sc), screen_i) + 1
        tl = sc.pop("_tl_override", None) or _base_timeline(sc)
        sc["timeline"] = tl
        sc.setdefault("line", "A")
        sc.setdefault("pov", "全知")
        sc["arrangement_note"] = notes.get(id(sc), "")

    # 5) 导演批注 + 图谱
    dn = arrangement_director_note(arrangement, narrative_mode, "", "", ordered)
    plan = {
        "方式": arrangement,
        "叙事结构": narrative_mode,
        "时间线图谱": dn["时间线图谱"],
        "线索图谱": dn["线索图谱"],
        "导演批注": dn["批注"],
        "字幕位": subtitle_slots,
    }
    return ordered, plan


def _flashback_title_card(n_scenes, seed):
    """倒叙开场的回退字幕 (确定性选择)."""
    rng = _seeded_rng(f"card_{seed}_{n_scenes}")
    return rng.choice(["七天前", "三天前", "二十四小时前", "那年冬天", "一切开始之前", "十二小时前"])


# ============================================================
# 镜头级编排 (分镜节点用: 按场次的银幕序重排镜头, 同场镜头不拆散)
# ============================================================

def arrange_shots_by_scenes(shots, ordered_scenes):
    """把 shots (含 scene=scene_num 字段) 按 ordered_scenes 的银幕序重排.
    同一场戏的镜头保持内部顺序不被拆散。镜头不增不减."""
    if not shots or not ordered_scenes:
        return shots
    # scene_num -> screen_order
    screen_rank = {}
    for sc in ordered_scenes:
        screen_rank[sc.get("scene_num")] = sc.get("screen_order", 0)
    # scene_num -> 场次 meta (timeline/line/pov/arrangement_note)
    meta_by_num = {sc.get("scene_num"): sc for sc in ordered_scenes}

    def _rank(shot):
        return screen_rank.get(shot.get("scene"), 10 ** 6)

    # 稳定排序: 同场镜头保持原相对顺序
    ordered = sorted(shots, key=lambda s: (_rank(s), s.get("n", 0)))
    # 重新编号 (银幕镜号), 保留原镜号为 source_shot
    for i, shot in enumerate(ordered):
        shot["source_shot"] = shot.get("n", i + 1)
        shot["n"] = i + 1
        meta = meta_by_num.get(shot.get("scene"), {})
        shot["timeline"] = meta.get("timeline", "现在")
        shot["line"] = meta.get("line", "A")
        shot["pov"] = meta.get("pov", "全知")
        shot["screen_order"] = i + 1
        shot["story_order"] = meta.get("story_order", i + 1)
        if meta.get("arrangement_note"):
            shot["arrangement_note"] = meta["arrangement_note"]
    return ordered


# ============================================================
# 自检
# ============================================================
if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    demo = []
    funcs = ["开场画面 (钩子)", "铺垫 (世界)", "铺垫 (冲突种子)", "触发事件", "中点 (真假胜利)",
             "灵魂的黑夜", "闪回 · 过去时间线", "决定/承诺", "高潮 · 终极对决", "结尾画面 (对称开场)"]
    tensions = [3, 3, 4, 6, 8, 9, 4, 7, 10, 4]
    for i, (f, t) in enumerate(zip(funcs, tensions)):
        demo.append({"scene_num": i + 1, "act": 1 if i < 4 else (2 if i < 8 else 3),
                     "story_function": f, "tension_level": t, "location": f"场景{i+1}"})
    ok = True
    for arr in ARRANGEMENT_MODES:
        for nm in ("单线", "双线并行", "三线交织", "POV切换"):
            out, plan = arrange_scenes(demo, arr, nm, seed="自检")
            assert len(out) == len(demo), f"{arr}|{nm} 场次数量变化"
            assert sorted(s["scene_num"] for s in out) == list(range(1, len(demo) + 1)), f"{arr}|{nm} 场次丢失"
            tls = [s["timeline"].split("·")[0] for s in out]
            lines = sorted(set(s["line"] for s in out))
            print(f"[{arr}|{nm}] 时间线: {'→'.join(tls)} | 线: {lines}")
            if arr == "倒叙(结果先行)" and len(out) >= 4:
                assert out[0]["timeline"] == "现在·结局边缘", "倒叙开场时间线错误"
            if arr == "循环叙事(首尾相扣)" and len(out) >= 4:
                assert out[0]["timeline"] == "循环·终点即起点", "循环首场标记错误"
                assert out[-1]["timeline"] == "循环·起点即终点", "循环末场标记错误"
                assert out[0]["scene_num"] != out[-1]["scene_num"], "循环首末场重复"
            if arr == "穿插乱叙" and len(out) >= 6:
                tl_set = set(s["timeline"] for s in out)
                assert len(tl_set) >= 2, "乱叙时间线种类不足"
            if nm in ("双线并行", "三线交织"):
                assert len(lines) >= 2, f"{nm} 线索种类不足"
            # 确定性: 同输入两次结果一致
            out2, _ = arrange_scenes(demo, arr, nm, seed="自检")
            assert [s["scene_num"] for s in out] == [s["scene_num"] for s in out2], "确定性失败"
    print("自检通过: 全部编排×线型 断言 OK")
