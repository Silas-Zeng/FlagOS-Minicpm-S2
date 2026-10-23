"""仅本地stdlib：复用2071原事务验收，补422身份/pitched-SAVE/QGQA兼容。"""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import re
import runpy
import sys

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).parent
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


def legacy_functions():
    require(sha(LEGACY) == LEGACY_SHA, '原2071入口变更')
    text = LEGACY.read_text(encoding='utf-8')
    funcs = {n.name:ast.get_source_segment(text, n) for n in ast.parse(text).body if isinstance(n, ast.FunctionDef)}
    raw = funcs['inspect_raw'].replace('e155a16669e69b7eb7aff370dbcbcf225a4f593fa42b2399722e96999b53a1f1', RUNNER)
    require(raw.count(', 416)') == 1, '原raw计数切口不唯一')
    raw = raw.replace(', 416)', ', 422)')
    _, separator, body = funcs['inspect'].partition('    events = []\n')
    require(bool(separator), '原事务段提取边界变化')
    old = 'saved["copy_calls"] == 42 * source_runs'
    require(body.count(old) == 1, '原SAVE线性断言切口变化')
    body = body.replace(old, 'saved["copy_calls"] == saved["linear_calls"] + saved["pitched_calls"]')
    namespace = dict(globals(), BASE_REVIEW=ROOT/'analysis/source/mm-cta-service-pair/recompute.py',
        BASE_REVIEW_SHA='81f227fb4c4eca992024fc0d7cebb6416f3ffda054d8e9a536d35040011122bd')
    exec(compile(raw+'\n\ndef inspect_protocol(evidence, run, control):\n    events = []\n'+body,
                 str(LEGACY)+':qgqa_adapter', 'exec'), namespace)
    return namespace['inspect_raw'], namespace['inspect_protocol']


def inspect(name):
    require(re.fullmatch(r'\d{8}T\d{6}Z-q-gqa-kv-swap-verify1-context16k-long', name), '只接受本组合VERIFY1 run ID')
    raw, protocol = legacy_functions()
    evidence, manifest, sources, _ = raw(name)
    run = ROOT/'experiments/framework'/name
    control = run.with_name(run.name+'-control')
    require(sha(HERE/'expected-source-sha256.json') == MAP_SHA, '固定422 map变化')
    require(sources == read(HERE/'expected-source-sha256.json'), '不是完整固定QGQA+swap422源')
    for name_, pin in (('launch.sh', '1bd16b321ae7d1d11e105f7c0e3ed19e3712afb059b1989a5974556872d8e03e'),
                       ('prepare_q_gqa_kv_swap.py', '6d09374054f2ae1df54f7dc9fceb5e221eae3f8b39bcbaf5a93c0500c5181cc4')):
        require(sha(control/name_) == pin, '封存接线身份不符: '+name_)
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
    planner = HERE/'biv150_kv_pitched_copy.py'
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
    result.update(status='passed_qgqa_swap_verify1_compatibility', protocol_key=acks[0]['command']['key'],
        engine_pid=pid, q_gqa_actual_markers=markers, legacy_protocol_validator_sha256=LEGACY_SHA,
        q_gqa_marker_boundary='两路可在不同execute首次命中；不证明恢复那一步全部层路由或graph replay逐步覆盖',
        safe_R_boundary='R来自固定84be plan_snapshot与原队列/device-fence；raw无完整issued/queued/known，不能独立重算安全上界',
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
