"""将既有三处H2D变换静态迁移到固定main；不导入框架或运行测试。"""
import ast
import difflib
import hashlib
import json
from pathlib import Path
import runpy

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUNNER = 'vllm_fl/worker/model_runner.py'
sha = lambda raw: hashlib.sha256(raw).hexdigest()
blob = lambda raw: hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
recipe_path = ROOT / 'archive/ai/20261022-framework-kv/skip-computed-h2d/prepare_skip_computed_h2d.py'
assert sha(recipe_path.read_bytes()) == '23d833a1bd3f4155652a2457b19bdaedf29b918de488e18e5b986b2cb5e08427'
# 只载入原标准库常量/定义；不调用原main、transform_source或任何fixture。
r = runpy.run_path(str(recipe_path))
old_candidate = (ROOT / 'archive/ai/20261022-framework-kv/skip-computed-h2d/candidate_model_runner.py').read_bytes()
assert sha(old_candidate) == r['OUTPUT_SHA']
changes = [(r['CONDITION'], r['PENDING'] + r['CONDITION']),
           (b'        else:\n' + r['COPY'], r['DEFERRED']),
           (r['METADATA'], r['COPY_ON_FALSE'])]


def apply(raw, replacements):
    for before, after in replacements:
        assert raw.count(before) == 1
        raw = raw.replace(before, after, 1)
    return raw


inverse = [(b, a) for a, b in reversed(changes)]
old_base = apply(old_candidate, inverse)
assert sha(old_base) == r['INPUT_SHA']
base = (HERE / 'main' / RUNNER).read_bytes()
assert sha(base) == 'cc7f834d25ccbe5d839a731b8e9aa8bf7533bea6f2f937c394423b3844842dfe'
candidate = apply(base, changes)
assert apply(candidate, inverse) == base


def methods(raw):
    return {cls.name + '.' + node.name: ast.dump(node, include_attributes=False)
            for cls in ast.parse(raw).body if isinstance(cls, ast.ClassDef)
            for node in cls.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}


old_methods, base_methods = methods(old_base), methods(base)
old_candidate_methods, candidate_methods = methods(old_candidate), methods(candidate)
target_method = 'ModelRunnerFL._prepare_inputs'
assert base_methods[target_method] == old_methods[target_method]
assert candidate_methods[target_method] == old_candidate_methods[target_method]
changed = [name for name in base_methods if base_methods[name] != candidate_methods[name]]
assert changed == [target_method]
historical_class_differences = [name for name in base_methods
    if base_methods[name] != old_methods.get(name)]
assert historical_class_differences == []
compile(candidate, RUNNER, 'exec')
output = HERE / 'files' / RUNNER
output.parent.mkdir(parents=True, exist_ok=True)
output.write_bytes(candidate)
patch = ''.join(difflib.unified_diff(base.decode().splitlines(True), candidate.decode().splitlines(True),
    fromfile='a/' + RUNNER, tofile='b/' + RUNNER))
(HERE / 'method.patch').write_text(patch, encoding='utf-8', newline='')
pair_path = ROOT / 'analysis/skip-computed-h2d-service-pair.json'
pair = json.loads(pair_path.read_text(encoding='utf-8'))
assert pair['pair_comparable'] and len(pair['checks']) == 30 and all(pair['checks'].values())
snapshot = json.loads((HERE / 'main-snapshot.json').read_text())
manifest = {
    'status': '仅本地Draft PR材料；未发布、未重新上卡',
    'repository': snapshot['repository'], 'base_branch': 'main',
    'base_commit': snapshot['commit'], 'base_tree': snapshot['tree'],
    'suggested_branch': 'codex/skip-computed-h2d',
    'method': 'skip_computed_h2d', 'files': [{
        'path': RUNNER, 'operation': 'replace', 'mode': '100644',
        'base_blob': blob(base), 'base_sha256': sha(base),
        'target_blob': blob(candidate), 'target_sha256': sha(candidate),
        'package_path': 'files/' + RUNNER}],
    'static_migration': {'exact_inverse_main_bytes': True,
        'three_edits_identical_to_tested_recipe': True,
        'current_prepare_inputs_ast_equals_tested_baseline': True,
        'candidate_prepare_inputs_ast_equals_tested_candidate': True,
        'other_current_class_methods_unchanged': True,
        'historical_class_method_differences': historical_class_differences,
        'changed_methods': changed, 'compile': True,
        'cpu_metadata_helper_unchanged_sha256': '0e96152454a9197f65a34c2fe8805bd5073e1fa473070d59d4ec4f20a6d8846f',
        'gqa_footer_and_C500_files_preserved': True},
    'historical_evidence': {'recipe_sha256': sha(recipe_path.read_bytes()),
        'baseline_runner_sha256': sha(old_base), 'candidate_runner_sha256': sha(old_candidate),
        'method_gate': '20261022T214819Z-skip-computed-h2d-method',
        'baseline_run': pair['runs']['baseline']['run_id'],
        'candidate_run': pair['runs']['candidate']['run_id'],
        'analysis_path': 'analysis/skip-computed-h2d-service-pair.json',
        'analysis_sha256': sha(pair_path.read_bytes()), 'checks_passed': 30,
        'gain': pair['gain'], 'platform': 'BI-V150',
        'source_scope': '历史QGQA414组合；不等同当前main整树性能'},
    'limits': ['单pair小幅正信号，非稳定统计或官方成绩',
        '本次仅静态迁移；无新设备/准确率/官方性能或C500验证',
        'helper没有vendor开关；C500若满足既有scope也可能采用本省略，需要平台负责人确认后再合并',
        '不新增平台开关或修改原helper；不触碰队友#14草稿',
        '发布前再核main；如前进，以新tree为基保留队友修改并重看本方法局部差异，不force或整树覆盖']}
(HERE / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'target_sha256': sha(candidate), 'target_blob': blob(candidate),
                  'changed_files': [RUNNER], 'static_migration': manifest['static_migration']}, ensure_ascii=False))
