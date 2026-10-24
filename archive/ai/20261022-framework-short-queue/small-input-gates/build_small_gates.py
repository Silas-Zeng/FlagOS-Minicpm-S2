"""从已验两个门派生唯一新增短shape；不运行控制器/worker。"""
import ast
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
TMP = HERE.parent


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    variants = (
        ("hot-key-v2", "hot-key-v2/validate_attention_hot_launch.py", "validate_small_hot_key.py",
         "hot-key-v2/biv150_attention_key_recipe.py", "biv150_attention_key_recipe.py"),
        ("c3views", "next-c3-views/validate_c3_views.py", "validate_small_c3_views.py",
         "next-c3-views/biv150_c3_view_reuse.py", "biv150_c3_view_reuse.py"),
    )
    rows = []
    for name, source_path, gate_name, policy_path, policy_name in variants:
        original = (TMP / source_path).read_bytes()
        source = original.decode("utf-8")
        old_cases = 'for label, lengths in (("C3-P2019-KV16K", [1] * 29 + [2019]),\n                               ("Q2048-KV16K", [2048])):'
        new_cases = 'for label, lengths in (("C3-D29-P128-KV1024", [1] * 29 + [128]),):'
        assert source.count(old_cases) == 1
        source = source.replace(old_cases, new_cases)
        for old, new in (
            ('previous.make_data(torch, lengths, 16384)', 'previous.make_data(torch, lengths, 1024)'),
            ('prepare_pages(torch, common, k, v, 16384)', 'prepare_pages(torch, common, k, v, 1024)'),
            ('plan.prefill.num_actual_tokens != 2019', 'plan.prefill.num_actual_tokens != 128\n                                            or plan.prefix_tokens != 29 or plan.total_tokens != 157\n                                            or plan.decode.num_actual_tokens != 29'),
            ('"kv_len": 16384', '"kv_len": 1024'),
            ('Only P2019/KV16K timed; Q2048/KV16K correctness only.',
             '新增D29/P128/KV1024正确性与计时；复用既有大shape/纯prefill证据，不重跑。'),
        ):
            assert source.count(old) == 1, old
            source = source.replace(old, new)
        source = source.replace('P2019 ABBA', 'D29/P128/KV1024 ABBA')
        source = source.replace('audited P2019 suffix', 'required D29/P128 suffix')
        source = source.replace('two actual-layer', 'one short actual-layer')
        source = source.replace('Two actual-backend cases', 'One short actual-backend case')
        assert 'P2019' not in source and 'Q2048-KV16K' not in source
        changed = source.encode('utf-8')
        compile(changed, gate_name, 'exec')
        # 复用原计时/物理页/清理流程，不重复旧运行合同。
        before_tree, after_tree = ast.parse(original), ast.parse(changed)
        for function in ('cpu_snapshot', 'timed_batch', 'delta', 'prepare_pages'):
            before = next(n for n in before_tree.body if isinstance(n, ast.FunctionDef) and n.name == function)
            after = next(n for n in after_tree.body if isinstance(n, ast.FunctionDef) and n.name == function)
            assert ast.dump(before) == ast.dump(after), function
        policy = (TMP / policy_path).read_bytes()
        tree = ast.parse(changed)
        expected = next(n.value.value for n in tree.body if isinstance(n, ast.Assign)
                        and any(isinstance(t, ast.Name) and t.id == 'EXPECTED_POLICY' for t in n.targets))
        assert sha(policy) == expected
        (HERE / gate_name).write_bytes(changed)
        (HERE / policy_name).write_bytes(policy)
        rows.append({'method': name, 'parent_gate': source_path, 'parent_gate_sha256': sha(original),
                     'gate': gate_name, 'gate_sha256': sha(changed), 'policy': policy_name,
                     'policy_sha256': sha(policy), 'policy_unchanged': True,
                     'shape': {'decode_requests': 29, 'prefill_tokens': 128, 'kv_len': 1024, 'total_tokens': 157},
                     'ab_order': ['baseline', 'candidate', 'candidate', 'baseline'], 'calls_per_window': 32,
                     'new_token_min_position': 896, 'reused_prefix_end_exclusive': 256,
                     'new_tokens_outside_reused_prefix': 896 >= 256,
                     'timing_and_page_functions_ast_unchanged': True,
                     'compiled': True, 'executed_controller_or_worker': False})
    (HERE / 'preparation.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(rows, ensure_ascii=False))


if __name__ == '__main__':
    main()
