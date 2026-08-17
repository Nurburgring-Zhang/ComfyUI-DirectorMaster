# -*- coding: utf-8 -*-
"""
ComicDramaPro — 漫剧分镜节点 (漫画/动态漫画分镜设计)
=====================================================
输出世界级漫画分镜: 分格/对话框/拟声词/视线引导/节奏留白.
支持日漫/美漫/条漫/动态漫 4 种漫剧形态.

V6.3 新增, 弥补漫剧类型缺失.
"""


class ComicDramaPro:
    COMIC_STYLES = ["日漫分镜", "美漫分镜", "条漫竖屏", "动态漫剧"]

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "场景描述": ("STRING", {"default": "父女厨房雨夜", "multiline": True}),
                "导演风格": ("STRING", {"default": "王家卫"}),
                "漫剧风格": (cls.COMIC_STYLES, {"default": "日漫分镜"}),
                "页数": ("INT", {"default": 8, "min": 1, "max": 40}),
                "每页格数": ("INT", {"default": 5, "min": 1, "max": 12}),
                "情绪基调": ("STRING", {"default": "孤独"}),
                "对白密度": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.1}),
                "拟声词使用": ("BOOLEAN", {"default": True}),
                "启用反AI规则": ("BOOLEAN", {"default": True}),
            },
            "optional": {
                "灵魂注入": ("STRING", {"default": "", "multiline": True}),
                "高级参数JSON": ("STRING", {"default": "", "multiline": True}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("分镜剧本", "分格布局", "经验矩阵")
    FUNCTION = "build_comic"
    CATEGORY = "PromptLibrary/漫剧"

    def build_comic(self, 场景描述, 导演风格, 漫剧风格, 页数, 每页格数,
                    情绪基调, 对白密度, 拟声词使用, 启用反AI规则,
                    灵魂注入="", 高级参数JSON="", **kwargs):
        import json as _json
        extra = {}
        if 高级参数JSON:
            try:
                extra = _json.loads(高级参数JSON)
            except Exception:
                extra = {}
        # absorb common keys from aggregator (任务类型/潜文本_情感/关键道具 等)
        任务类型 = kwargs.get("任务类型", "漫剧")
        潜文本_情感 = kwargs.get("潜文本_情感", "")
        关键道具 = kwargs.get("关键道具", "")
        关键参考片 = kwargs.get("关键参考片", "")

        style_map = {
            "日漫分镜": "鸟山鸣/井上雄彦/大友克洋 风格: 速度线+集中线+拟声词+特写切换+黑白高对比",
            "美漫分镜": "Frank Miller/Alan Moore/Jim Lee 风格: 全页构图+斜切格框+厚重墨线+戏剧光影",
            "条漫竖屏": "韩式webtoon/国漫条漫: 纵向滚动+大格留白+沉浸式+手机竖屏适配",
            "动态漫剧": "动态漫画/ Motion Comic: 有限动画+镜头推拉+配音同步+分格位移",
        }
        style_desc = style_map.get(漫剧风格, style_map["日漫分镜"])

        # 构建分镜剧本 (每页每格)
        panels = []
        total_panels = 页数 * 每页格数
        for p in range(1, 页数 + 1):
            panels.append(f"\n===== 第 {p} 页 / 共 {页数} 页 =====")
            for g in range(1, 每页格数 + 1):
                idx = (p - 1) * 每页格数 + g
                # 节奏: 首格全景/中格近景/末格特写或留白
                if g == 1:
                    shot = "全景/建立镜头"
                elif g == 每页格数:
                    shot = "特写或留白页尾"
                else:
                    shot = "中近景/反应镜头"
                onomatopoeia = ""
                if 拟声词使用 and idx % 3 == 0:
                    ops = ["沙沙", "咔嚓", "咚", "淅沥", "呼——", "啪", "嗒"]
                    onomatopoeia = f" | 拟声词: {ops[idx % len(ops)]}"
                dialogue = ""
                if idx % 2 == 0 and 对白密度 > 0.3:
                    dialogue = f" | 对白: (简短, ≤10字, 潜文本)"
                panels.append(
                    f"  格{g} ({shot}){onomatopoeia}{dialogue}\n"
                    f"    画面: {场景描述} — 第{idx}/{total_panels}格\n"
                    f"    视线引导: 从上至下/从左至右 (日漫) 或 Z字 (美漫)\n"
                    f"    情绪: {情绪基调}"
                )

        script = (
            f"【漫剧分镜剧本 — {漫剧风格}】\n"
            f"导演风格锚定: {导演风格}\n"
            f"场景: {场景描述}\n"
            f"情绪基调: {情绪基调}\n"
            f"风格说明: {style_desc}\n"
            f"总页数: {页数} | 每页格数: {每页格数} | 总格数: {total_panels}\n"
            f"对白密度: {对白密度} | 拟声词: {'开' if 拟声词使用 else '关'}\n"
            f"反AI规则: {'开' if 启用反AI规则 else '关'}\n"
            + "\n".join(panels)
        )

        layout = (
            f"【分格布局参数】\n"
            f"漫剧风格: {漫剧风格}\n"
            f"格框形状: {'斜切格框+破格' if 漫剧风格=='美漫分镜' else '规整矩形格+少量破格'}\n"
            f"页边距: {'10mm (纸质)' if 漫剧风格!='条漫竖屏' else '0 (全屏滚动)'}\n"
            f"阅读方向: {'从右至左从上至下 (日漫)' if 漫剧风格=='日漫分镜' else '从左至右从上至下 (美漫/条漫)'}\n"
            f"节奏: 首格全景建立 → 中段近景递进 → 末格特写/留白收束\n"
            f"留白比例: {0.3 if 情绪基调=='孤独' else 0.2}\n"
            f"线条粗细: {'厚重墨线 (3-5px)' if 漫剧风格=='美漫分镜' else '中细线 (1-2px)'}\n"
        )

        matrix = (
            f"【经验矩阵】\n"
            f"类型: 漫剧 ({漫剧风格})\n"
            f"参考导演: {导演风格}\n"
            f"页面节奏: {页数}页×{每页格数}格 = {total_panels}格\n"
            f"情绪曲线: {情绪基调} → 递进 → 高潮 → 留白\n"
        )

        return (script, layout, matrix)


# NODE_CLASS_MAPPINGS (disabled - internal library only) = {"ComicDramaPro": ComicDramaPro}
