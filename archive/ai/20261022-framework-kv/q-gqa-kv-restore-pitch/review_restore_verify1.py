"""仅本地stdlib：复用2071/422验收，仅适配425 FULL H2D身份及动态提交几何。"""
import argparse
import ast
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import runpy
import sys

sys.dont_write_bytecode = True  # 不在原件 plugin-source 内创建 __pycache__。

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).parent
if os.name == 'nt':
    value = str(ROOT)
    if not value.startswith('\\\\?\\'):
        ROOT = Path('\\\\?\\UNC\\'+value[2:] if value.startswith('\\\\') else '\\\\?\\'+value)
    HERE = ROOT/'tmp/q-gqa-kv-restore-pitch'
LEGACY = ROOT/'scripts/review_kv_full_restore_run.py'
LEGACY_SHA = '2071bff34cdcd469294b406966ad86a0941d556b1d1e9ddd62dc87f927caf55b'
RUNNER = 'cc442e54e66c81f4375ac7b3311953441245f53bd0a576d27798528ce02e2663'
MAP_SHA = '82514a24cebdb3ae8ce8eb1562049168fa158894364d1dd87ae4b4a724f66136'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text(encoding='utf-8'))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def integer(value, minimum=0):
    require(type(value) is int and value >= minimum, '整数类型/范围不符')
    return value


def sqlite_fingerprint_path(fingerprint, path):
    """只适配SQLite URI入口；其它原件仍用扩展路径，指纹算法原样执行。"""
    if os.name == 'nt':
        value = str(path)
        if value.startswith('\\\\?\\UNC\\'):
            value = '\\\\'+value[8:]
        elif value.startswith('\\\\?\\'):
            value = value[4:]
        path = Path(value)
        require(path.is_absolute() and len(value) < 260,
                'SQLite普通Windows路径必须绝对且短于260字符，不能省略DB指纹')
    return fingerprint(path)


def legacy_functions():
    require(sha(LEGACY) == LEGACY_SHA, '原2071入口变更')
    text = LEGACY.read_text(encoding='utf-8')
    funcs = {n.name:ast.get_source_segment(text, n) for n in ast.parse(text).body if isinstance(n, ast.FunctionDef)}
    raw = funcs['inspect_raw'].replace('e155a16669e69b7eb7aff370dbcbcf225a4f593fa42b2399722e96999b53a1f1', RUNNER)
    require(raw.count(', 416)') == 1, '原raw计数切口不唯一')
    raw = raw.replace(', 416)', ', 425)')
    base_exec = '    exec(compile(prefix, str(BASE_REVIEW) + ":long_adapter", "exec"), namespace)\n'
    require(raw.count(base_exec) == 1, '原base reader namespace切口变化')
    sqlite_call = 'helper.fingerprint((d / "snapshot.sqlite").resolve())'
    replacement = 'sqlite_fingerprint_path(helper.fingerprint, (d / "snapshot.sqlite").resolve())'
    sqlite_adapter = (f'    require(prefix.count({sqlite_call!r}) == 1, "原SQLite指纹入口切口变化")\n'
        f'    prefix = prefix.replace({sqlite_call!r}, {replacement!r})\n')
    raw = raw.replace(base_exec, sqlite_adapter+base_exec
        +'    namespace["ROOT"] = ROOT  # 同一Windows扩展绝对路径。\n'
        +'    namespace["sqlite_fingerprint_path"] = sqlite_fingerprint_path\n')
    _, separator, body = funcs['inspect'].partition('    events = []\n')
    require(bool(separator), '原事务段提取边界变化')
    old = 'saved["copy_calls"] == 42 * source_runs'
    require(body.count(old) == 1, '原SAVE线性断言切口变化')
    body = body.replace(old, 'saved["copy_calls"] == saved["linear_calls"] + saved["pitched_calls"]')
    old_full = 'restored["copy_calls"] == 42 * destination_runs'
    require(body.count(old_full) == 1, '原FULL提交断言切口变化')
    body = body.replace(old_full, 'restored["copy_calls"] == restored["linear_calls"] + restored["pitched_calls"]')
    # 不触碰 restored["verification_copy_calls"] == 42 * destination_runs。
    namespace = dict(globals(), BASE_REVIEW=ROOT/'analysis/source/mm-cta-service-pair/recompute.py',
        BASE_REVIEW_SHA='81f227fb4c4eca992024fc0d7cebb6416f3ffda054d8e9a536d35040011122bd')
    exec(compile(raw+'\n\ndef inspect_protocol(evidence, run, control):\n    events = []\n'+body,
                 str(LEGACY)+':qgqa_adapter', 'exec'), namespace)
    return namespace['inspect_raw'], namespace['inspect_protocol']


PREPARER_SHA = 'f29f23e7de55d4acbacc7ee87e364e1c9f3ab32b002a8808b1c44b9a3495937a'
LAUNCHER_SHA = '352bc6b2c8f377293c6822196d8714385d9b0d924326779d07903d1b23011d31'
DRAFT_SHA = '9f178a70b48cf19e97d32f7b9bea26195f7e447b593be9784659916d36120475'


def verify_source(control, sources):
    """复用已审builder完整gate验收，逐字节绑定其封存凭据/实际SO/425源。"""
    require(sha(control/'launch.sh') == LAUNCHER_SHA, '425 launcher身份不符')
    builder = control/'prepare_restore_worker_source.py'
    require(sha(builder) == PREPARER_SHA, '425 preparer身份不符')
    # 只读取固定builder常量；不运行其main、passed_gate、copytree或SO加载。
    nodes = {n.targets[0].id: n.value for n in ast.parse(builder.read_bytes()).body
        if isinstance(n, ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0], ast.Name)}
    gate_pins = ast.literal_eval(nodes['GATE_SOURCE'])
    gate_checks = ast.literal_eval(nodes['CHECKS'])
    controller_pin = ast.literal_eval(nodes['CONTROLLER'])
    base_map = control/'base-source-sha256.json'
    draft = control/'biv150_kv_pitched_restore_worker.py'
    require(sha(base_map) == MAP_SHA and sha(draft) == DRAFT_SHA, '原422 map或9f draft身份不符')
    before = read(base_map)
    require(len(before) == 422 and before['vllm_fl/worker/model_runner.py'] == RUNNER, '原422源不符')
    receipt = read(control/'preparation.json')
    require(receipt == read(control/'purpose.json') and receipt['preparer_sha256'] == PREPARER_SHA
        and receipt['base_source_sha256'] == before and receipt['input_map_sha256'] == MAP_SHA
        and receipt['worker_draft_sha256'] == DRAFT_SHA and receipt['source_count'] == 425,
        '准备凭据与原422/新425身份不符')
    proof = control/'passed-H2D-gate'
    provenance = receipt['passed_H2D_gate']
    seal = read(proof/'control-seal.json')
    require(sha(proof/'control-seal.json') == provenance['seal_sha256']
        and seal['exit_code'] == 0 and seal['run'] == provenance['run']
        and seal['control'] == provenance['control'] and len(seal['files']) == provenance['seal_files'],
        '原H2D seal凭据不一致')
    gate_name = Path(provenance['run']).name
    require(re.fullmatch(r'\d{8}T\d{6}Z-kv-pitched-restore-gate', gate_name), '原H2D门run格式不符')
    copied = {'results.json': gate_name+'/results.json', 'manifest.json': gate_name+'/manifest.json',
        'exit-code': gate_name+'/exit-code',
        **{'control-'+n: gate_name+'-control/'+n for n in
            ('source-sha256.json', 'source-post-sha256.json', 'compile-input-identity.json')}}
    for local, remote in copied.items():
        path = proof/local
        require(seal['files'][remote] == {'sha256': sha(path), 'bytes': path.stat().st_size},
            '原H2D附证不在原完整seal: '+local)
    result, manifest = read(proof/'results.json'), read(proof/'manifest.json')
    require(sha(proof/'results.json') == provenance['results_sha256']
        and sha(proof/'manifest.json') == provenance['manifest_sha256']
        and (proof/'exit-code').read_text().strip() == '0' and result['status'] == 'pass'
        and manifest['exit_code'] == manifest['worker_exit_code'] == 0
        and manifest['controller_sha256'] == controller_pin and manifest['source_unchanged'] is True
        and set(result['case']['checks']) == gate_checks
        and all(v is True for v in result['case']['checks'].values())
        and result['RNG_unchanged'] == {'CPU': True, 'GPU': True}, '单层门未真实PASS')
    bridge = provenance['bridge_sha256']
    require(type(bridge) is str and re.fullmatch('[0-9a-f]{64}', bridge), '实际SO pin无效')
    gate_source = {**gate_pins, 'bridge.so': bridge}
    require(provenance['source_sha256'] == read(proof/'control-source-sha256.json')
        == read(proof/'control-source-post-sha256.json') == result['source_sha256'] == gate_source
        and result['bridge_sha256'] == manifest['bridge_sha256'] == bridge
        and seal['files'][gate_name+'/source/bridge.so']['sha256'] == bridge,
        '原实际PASS SO/完整source来源不一致')
    raw = draft.read_bytes(); anchor = b'RESTORE_BRIDGE = None\n'
    require(raw.count(anchor)==1, '原None pin切口不唯一')
    worker = raw.replace(anchor, ('RESTORE_BRIDGE = '+repr(bridge)+'\n').encode('ascii'))
    expected = dict(before)
    expected['vllm_fl/patches/biv150_kv_worker.py'] = hashlib.sha256(worker).hexdigest()
    additions = {'biv150_kv_pitched_restore.py': gate_pins['biv150_kv_pitched_restore.py'],
        'biv150_kv_pitched_restore_bridge.cpp': gate_pins['bridge.cpp'],
        'biv150_kv_pitched_restore_bridge.so': bridge}
    for name, pin in additions.items():
        rel = 'vllm_fl/patches/'+name
        require(rel not in expected, 'restore路径不能覆盖旧源')
        expected[rel] = pin
    require(sources == receipt['source_sha256'] == expected and len(expected)==425
        and receipt['worker_sha256'] == expected['vllm_fl/patches/biv150_kv_worker.py']
        and (control/'plugin-source/vllm_fl/patches/biv150_kv_worker.py').read_bytes() == worker,
        '固定422只允许worker+3新restore文件')
    return provenance


def load_stdlib_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def verify_restore_geometry(control, sources, ack, geometry):
    """仅调用已pin新runtime纯整数planner，不构造Bridge/PreparedRestore或导入Torch。"""
    restored = ack['worker_response']
    patch = control/'plugin-source/vllm_fl/patches'
    for name in ('biv150_kv_pitched_copy.py', 'biv150_kv_pitched_restore.py'):
        require(sha(patch/name) == sources['vllm_fl/patches/'+name], '原件planner字节不符: '+name)
    save = load_stdlib_module(patch/'biv150_kv_pitched_copy.py', 'reader_restore_818e')
    restore = load_stdlib_module(patch/'biv150_kv_pitched_restore.py', 'reader_restore_a743')
    ids = ack['command']['pages']
    plan = restore.make_restore_plan(ids, max(ids)+1, save_runtime=save)
    maximum = integer(restored['restore_max_pitch_bytes'], 16384)
    pieces, fallback = restore.segments_for_pitch(plan, max_pitch=maximum)
    pitched = sum(s.height>1 and s.physical_step>1 for s in pieces)
    linear = len(pieces)-pitched
    require(restored['restore_implementation']=='C_batch_positive_stride_FULL_H2D'
        and restored['restore_layers']==42 and restored['restore_submission_completion_ack'] is False
        and restored['restore_runtime_sha256']==sources['vllm_fl/patches/biv150_kv_pitched_restore.py']
        and restored['restore_bridge_sha256']==sources['vllm_fl/patches/biv150_kv_pitched_restore_bridge.so'],
        '不是已验SO的真实FULL H2D提交')
    require(plan.logical_pages==geometry['pages'] and plan.original_c95f_runs==geometry['destination_runs']
        and restored['restore_segments_per_layer']==len(plan.segments)
        and restored['copy_calls']==42*len(pieces) and restored['linear_calls']==42*linear
        and restored['pitched_calls']==42*pitched and restored['fallback_pitched_segments']==42*fallback
        and restored['original_c95f_calls']==42*geometry['destination_runs']
        and restored['verification_copy_calls']==42*geometry['destination_runs'],
        'FULL动态提交或原c95f回读几何不符')
    integer(restored['restore_current_stream_handle'])
    return {'segments_per_layer': len(plan.segments), 'linear_calls': 42*linear,
        'pitched_calls': 42*pitched, 'copy_calls': 42*len(pieces), 'fallback_pitched_segments': 42*fallback,
        'original_c95f_calls': restored['original_c95f_calls'],
        'verification_copy_calls_unchanged': restored['verification_copy_calls'],
        'actual_max_pitch_bytes': maximum, 'stream_handle': restored['restore_current_stream_handle'],
        'boundary': '按本次真实目的页及max_pitch重算；不硬编码14段/588调用，也不从calls推速度'}


def inspect(name):
    require(re.fullmatch(r'\d{8}T\d{6}Z-q-gqa-kv-restore-pitched-verify1-context16k-long', name), '只接受本组合VERIFY1 run ID')
    raw, protocol = legacy_functions()
    evidence, manifest, sources, _ = raw(name)
    run = ROOT/'experiments/framework'/name
    control = run.with_name(run.name+'-control')
    provenance = verify_source(control, sources)
    command = (control/'command.txt').read_text(encoding='utf-8')
    require('BIV150_KV_VERIFY_RESTORE=1' in command and 'BIV150_Q_FRAGMENT_SERVICE_ARTIFACT_DIR=' in command
        and '-u BIV150_FINITE_GROWTH_ADMISSION' in command, 'VERIFY1/QENV/finiteunset缺失')
    driver = ast.parse((run/'screen-driver.py').read_bytes())
    server, = [ast.literal_eval(n.value) for n in driver.body if isinstance(n, ast.Assign)
        and len(n.targets)==1 and isinstance(n.targets[0], ast.Name) and n.targets[0].id=='SERVER']
    require(manifest['server_command']==server and manifest['seed']==721201, '原SERVER/seed偏离')
    result = protocol(evidence, run, control)
    events = result.pop('protocol_events')
    acks = [e for e in events if e['event']=='RPC_ACK']
    saved = acks[0]['worker_response']; geometry = result['geometry']
    require(saved['save_implementation']=='C_batch_positive_stride_full_R' and saved['save_layers']==42
        and saved['save_runtime_sha256']==sources['vllm_fl/patches/biv150_kv_pitched_copy.py']
        and saved['save_bridge_sha256']==sources['vllm_fl/patches/biv150_kv_pitched_bridge.so']
        and saved['save_submission_completion_ack'] is False, '不是已验pitched-SAVE真实ACK')
    require(saved['save_verification_performed'] is True and saved['save_verification_passed'] is True
        and saved['save_verification_layers']==42 and saved['save_verification_bytes']==geometry['nbytes']
        and saved['save_verification_copy_calls']==42*geometry['source_runs'], 'SAVE源free前42字节证明缺失')
    require(saved['original_c95f_calls']==42*geometry['source_runs'], '原SAVE几何不符')
    planner = control/'plugin-source/vllm_fl/patches/biv150_kv_pitched_copy.py'
    require(sha(planner)==sources['vllm_fl/patches/biv150_kv_pitched_copy.py'], '冻结整数planner不符')
    # 只调旧818e纯整数make_plan；不构造Bridge/PreparedSave，不载库或框架。
    ids = acks[0]['command']['pages']
    plan = runpy.run_path(str(planner))['make_plan'](ids, max(ids)+1)
    linear = pitched = fallbacks = 0
    max_pitch = integer(saved['save_max_pitch_bytes'], 16384)
    for segment in plan.segments:
        is_pitched = segment.height>1 and segment.source_step>1
        if is_pitched and segment.source_step*16384>max_pitch:
            fallbacks += 1; linear += segment.height
        elif is_pitched:
            pitched += 1
        else:
            linear += 1
    require(saved['save_segments_per_layer']==len(plan.segments)
        and saved['linear_calls']==42*linear and saved['pitched_calls']==42*pitched
        and saved['fallback_pitched_segments']==42*fallbacks, 'SAVE完整正等差几何不符')
    integer(saved['save_current_stream_handle'])
    restore_geometry = verify_restore_geometry(control, sources, acks[1], geometry)
    pid = acks[0]['pid']; log = (run/'server.log').read_text(encoding='utf-8', errors='replace')
    markers = {}
    for marker, field in (('BIV150_Q_FRAGMENT_SERVICE_FIRST_ACTUAL_EXECUTE_SELECTED ', 'selected_calls_in_execute'),
                          ('BIV150_Q_GQA_FIRST_ACTUAL_EXECUTE_SELECTED ', 'gqa_calls_in_execute')):
        values = []
        for line in log.splitlines():
            if marker not in line:
                continue
            prefix, payload = line.split(marker, 1); value = json.loads(payload)
            owner = re.search(r'EngineCore[^\s()]* pid=(\d+)', prefix)
            if (owner and int(owner.group(1))==value.get('pid')==pid and value.get('actual_execute') is True
                    and value.get('complete_step_return') is True and value.get('num_requests',0)>=2
                    and value.get('gqa_python_count_excludes_graph_replay') is True
                    and value.get('scheduled_tokens',0)>0 and value.get(field,0)>0):
                values.append(value)
        require(bool(values), '组合同Engine真实成功execute标记缺失: '+marker)
        markers[marker.strip()] = values
    geometry.update(save_source_verification_bytes=saved['save_verification_bytes'],
        save_linear_calls=saved['linear_calls'], save_pitched_calls=saved['pitched_calls'],
        save_segments_per_layer=saved['save_segments_per_layer'], save_stream_handle=saved['save_current_stream_handle'])
    result.update(status='passed_qgqa_pitched_full_restore_verify1_compatibility', protocol_key=acks[0]['command']['key'],
        engine_pid=pid, q_gqa_actual_markers=markers, legacy_protocol_validator_sha256=LEGACY_SHA,
        q_gqa_marker_boundary='两路可在不同execute首次命中；不证明恢复那一步全部层路由或graph replay逐步覆盖',
        safe_R_boundary='R来自固定84be plan_snapshot与原队列/device-fence；raw无完整issued/queued/known，不能独立重算安全上界',
        passed_H2D_gate=provenance, restore_submission_geometry=restore_geometry,
        reader_boundary='仅适配FULL提交几何；原c95f回读计数/事务/consumer/cleanup保持，非accuracy或收益',
        gain_calculated=False)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run_id'); parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = inspect(args.run_id)
    with args.output.open('x', encoding='utf-8', newline='\n') as output:
        json.dump(result, output, ensure_ascii=False, indent=2); output.write('\n')
    print(json.dumps({'status':result['status'], 'geometry':result['geometry'], 'output':str(args.output)}, ensure_ascii=False))
