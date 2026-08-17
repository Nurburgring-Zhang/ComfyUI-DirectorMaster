# -*- coding: utf-8 -*-
"""
ComfyUI-DirectorMaster V8.0 — 彻底重建版
==========================================
9 个独立 ComfyUI 节点, 无 legacy 依赖, 自包含.

每个节点:
  - 有 LLM → 调用 llm_engine.generate_native 原生生成 (世界顶级导演级)
  - 无 LLM → 使用内置深度模板 (高质量, 无降级)
  - ComfyUI 合规: INPUT_TYPES @classmethod, RETURN_TYPES==RETURN_NAMES,
    OUTPUT_NODE, IS_CHANGED, forceInput, sys.path 修复

目录:
  aggregator/__init__.py          — 包入口
  aggregator/llm_engine.py         — LLM 原生引擎 + 7 域规则
  aggregator/director_master.py   — ① Core (11输出)
  aggregator/script_studio.py     — ② Script
  aggregator/vibe_studio.py       — ③ Vibe
  aggregator/art_master.py        — ④ Art
  aggregator/sound_master.py      — ⑤ Sound
  aggregator/cinematic_studio.py  — ⑥ Cinematic
  aggregator/final_master.py      — ⑦ Final
  aggregator/router.py            — ⑧ Router
  aggregator/archive_master.py    — ⑨ Archive
  aggregator/node_base.py         — 公共基类 (ComfyUI 规范 + 双轨)

所有 legacy .py 文件保留在当前目录作历史参考, 不再被 import.
"""