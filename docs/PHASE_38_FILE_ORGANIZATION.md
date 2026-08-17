# Phase 38 - 文件整理报告

**日期**: 2026-08-09
**目标**: 按类型归纳, 剔除无用临时文件

## 整理前状态
- 总文件数: 264
- 根目录调试文件 _*.py: 130+
- 根目录 .md: 15
- tests/ 测试: 23
- tools/ 工具: 24
- workflows/ 工作流: 9
- knowledge_base/ 知识库: 23
- docs/ 文档: 15

## 整理规则

### 必须保留 (核心节点代码)
41 节点 .py + director_soul.py + director_engine.py + director_real_scripts.py
+ prompt_builder.py + anti_ai_vocab.py + scene_library.py + story_sense_data.py
+ format_templates.py + master_director_data.py + modes_*.py + engine_story_arc.py
+ production_pipeline_v3.py + pln_*.py + doctor.py
+ _addon_injector.py (核心, __init__.py 引用)

### 保留为工具 (移到 tools/)
_audit_*.py, _check_io.py, _check_remote.py, _check_utility.py, _check_soul.py
_dual_ai.py, _gen_all_nodes_workflow.py, _gen_workflows_v2.py
_inspect_wf.py, _push_final.py, _rebuild_init.py
_self_question.py, _show_issues.py, _stat_workflows.py
_update_tests.py, _update_tests_32.py, _e2e_validation.py

### 移到 tests/ (已经是测试)
_test_*.py 已有

### 移到 docs/ (已经存在)
PHASE_*.md, AUDIT_*.md, MASTER_*.md, DEEP_*.md, EXPANSION_*.md
HOW_TO_USE.md, INSTALL_GUIDE.md, NODE_INPUT_GUIDE.md, WORKFLOWS_README.md
CHANGELOG.md, RELEASE_NOTES_*.md

### 移到 archive/_trash/ (临时调试 - 可恢复)
_add1_*.py, _add5_*.py, _add7_*.py, _add8_*.py, _add9_*.py, _add11_*.py, _add13_*.py
_phase_a_batch*.py, _phase_a_inject.py, _phase_a_summary.py
_phase_b_batch*.py, _phase_b_inject*.py, _phase_b_templates.py
_v5.py, _v6.py, _v6b.py, _v6c.py, _v7.py, _v8.py, _v8b.py, _v9.py, _v10.py
_diff*.py, _show*.py, _count_*.py, _list_*.py, _dump_*.py
_verify2.py, _verify3.py, _verify_push.py
_audit_*.json, _check.txt, _n.txt, _fstring_test.txt, _all_keys.txt
_rollback_b11.py, _append_audit.py, _append_phase14.md
_enhance_*.py, _sample2.py
_e2e_b5.py, _e2e_batch4.py
_phase13_append.py, _phase13_rewrite.py
_final_summary*.py, _summary.py, _find_stray.py, _show_stray.py
_batch_nodes.py, _gen_simple.py, _gen14.py
_dual_ai_review.json
