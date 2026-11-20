"""PR24加原SAVE/FULL单次VERIFY1；无profiler或自动性能/准确率任务。"""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess

HERE = Path(__file__).resolve().parent
SEED_PATH = Path('/workspace/experiments/minicpm-s2/framework/20261024T110545Z-current-main-pr24-resume-cpu-context16k-long-control/database-original.sqlite')
SEED_SHA = '207f1bdad2e980fcddf40b8367158026332bb9c9f6e3ab2dced1246cbb0d4378'
# 原bc51 driver由SCRIPTS锁定，无native profiler driver。
ROOT = Path('/workspace/experiments/minicpm-s2')
COMMIT = '1ad9a708ee77323372f0fa5975a04a52d294852c'
TREE = 'd1a96e3f56723956a7902cba7e676fd285c83d0c'
BASE_COUNT = 467
TARGET_COUNT = 473
BLOBS_SHA = '2859052a2ffa80a217ae15c88e52e1507c2de47b431b71f56b6218ee57d7ff8d'
MANIFEST_SHA = '6db1717c9c9557404111e11bb6a422f0200c8bf50a98d72138fa264cafc7fd12'
SCRIPTS = {'run_framework_screen.py': 'bc51ac2d9daf90205bde362f8384b1ac34238e7be932e9a6df7fc618d7350be9', 'run_diagnostic_load.sh': '621dedfc11ce21d35bdcffc9918ab4ac8bf63adc0e277fe7c2117e5f7e4ec378', 'snapshot_tuning_db.py': '0f2a57bf3bdb858756a1dedab5bd386a3a8bff384d925cf76461afb8c097e7a2', 'monitor_gpu.sh': 'af90002eebd4dade188c8efd58e025c3ce3cbcfa022a0e2d7a49fe2e8870f88a'}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def save(path, value):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')


def source_maps(source):
    # 复用已审owner的Git link文字/mode及常规目标内容SHA两种身份。
    blobs, hashes = {}, {}
    for path in sorted(source.rglob('*')):
        relative = path.relative_to(source)
        if any(x in ('.git', '__pycache__') for x in relative.parts) or path.suffix in ('.pyc', '.pyo'):
            continue
        if path.is_symlink():
            if not path.resolve(strict=True).is_relative_to(source):
                raise ValueError('source symlink越界')
            data, mode = os.readlink(path).encode(), '120000'
        elif path.is_file():
            data, mode = path.read_bytes(), '100755' if path.stat().st_mode & 0o111 else '100644'
        else:
            continue
        digest = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        blobs[relative.as_posix()] = dict(mode=mode, sha=digest)
        hashes[relative.as_posix()] = sha(path)
    return blobs, hashes


def source_ready(source):
    if source.is_symlink() or not source.resolve().is_relative_to(ROOT / 'code'):
        raise ValueError('main源码必须是本实验code下独立真实目录')
    if sha(HERE / 'candidate-git-blobs.json') != BLOBS_SHA or sha(HERE / 'candidate-manifest.json') != MANIFEST_SHA:
        raise ValueError('冻结main身份材料变化')
    expected, manifest = read(HERE / 'candidate-git-blobs.json'), read(HERE / 'candidate-manifest.json')
    hashes = manifest['source_sha256']
    if (len(expected) != BASE_COUNT or manifest['base_commit'] != COMMIT
            or manifest['target_tree'] != TREE or manifest['target_blob_count'] != BASE_COUNT
            or source_maps(source) != (expected, hashes)):
        raise ValueError('并非冻结PR24完整Git源码；拒绝附带build产物')
    return expected, hashes


def native_ready(path, source_hashes):
    manifest = read(path)
    if manifest['source_commit'] != COMMIT or manifest['source_tree'] != TREE:
        raise ValueError('native构建来自其它commit/tree')
    for relative in ('csrc/iluvatar/native_w8a8.cpp', 'csrc/iluvatar/native_w8a8.cu',
                     'tools/build_biv150_native_w8a8.py'):
        if manifest['source_sha256'].get(relative) != source_hashes[relative]:
            raise ValueError('native构建源码不符: ' + relative)
    library, build_log = Path(manifest['library']), Path(manifest['build_log'])
    if (not library.is_absolute() or library.is_symlink() or not build_log.is_absolute()
            or sha(library) != manifest['library_sha256'] or sha(build_log) != manifest['build_log_sha256']
            or library.read_bytes()[:4] != b'\x7fELF' or manifest.get('exit_code') != 0
            or not manifest.get('build_command') or not manifest.get('compiler')
            or not isinstance(manifest.get('abi'), dict)
            or not manifest['abi'].get('torch_version')
            or type(manifest['abi'].get('cxx11_abi')) is not bool):
        raise ValueError('缺完整native构建/ELF/ABI/日志凭据')
    control = path.parent
    state, summary, checks = read(control / 'state.json'), read(control / 'summary.json'), read(control / 'operator-check.json')
    if ((control / 'exit-code').read_text().strip() != '0' or state.get('completed') is not True
            or state.get('database_restored') is not True or state.get('source_unchanged') is not True
            or summary.get('coverage') is not True or summary.get('source_commit') != COMMIT
            or summary.get('source_tree') != TREE or summary.get('library_sha256') != manifest['library_sha256']
            or summary['result'].get('completed') != 32 or summary['result'].get('failed') != 0
            or len(checks['records']) != 9 or not all(r.get('passed') is True for r in checks['records'])
            or checks.get('original_weight_fallback_unchanged') is not True):
        raise ValueError('本实例PR24九项+32请求/PQ/native接入或清理未完成；不继承其它实例')
    return manifest, library, build_log


def idle():
    import socket
    ports = {}
    for family, host in ((socket.AF_INET, '127.0.0.1'), (socket.AF_INET6, '::1')):
        with socket.socket(family, socket.SOCK_STREAM) as sock:
            sock.settimeout(2)
            ports[host] = sock.connect_ex((host, 9031)) != 0
    query = subprocess.check_output(['/usr/local/corex-4.5.0/bin/ixsmi', '--query-gpu=memory.used,utilization.gpu', '--format=csv,noheader,nounits'], text=True)
    table = subprocess.check_output(['/usr/local/corex-4.5.0/bin/ixsmi'], text=True)
    result = dict(ports_closed=ports, gpu=query, ixsmi=table)
    if not all(ports.values()) or query.strip() != '68, 0' or 'No running processes found' not in table:
        raise RuntimeError('当前卡/9031不空闲，拒绝启动或恢复DB')
    return result


def owned_group(pid):
    members, errors = [], []
    for proc in Path('/proc').iterdir():
        if not proc.name.isdigit():
            continue
        try:
            raw = (proc / 'stat').read_text()
            fields = raw[raw.rindex(')') + 2:].split()
            if int(fields[2]) == pid or int(fields[3]) == pid:
                members.append(dict(pid=int(proc.name), state=fields[0], pgrp=int(fields[2]), session=int(fields[3])))
        except (FileNotFoundError, ProcessLookupError):
            continue
        except (OSError, ValueError, IndexError) as error:
            errors.append(dict(pid=proc.name, error_type=type(error).__name__))
    return dict(owner_pid=pid, members=members, errors=errors)


def verify_coverage(control, run):
    """PR24+既有SAVE/FULL的VERIFY1后验；仅消费原件，不提供收益或完整准确率结论。

    事务段复用2071bff3，pitched-SAVE段复用6c5f73aa；只替换SAVE几何断言、
    planner副本位置及旧包装/标记验收。完整473来源和DB收尾由owner负责。
    """
    import ast
    import hashlib
    import json
    import math
    import re
    import runpy
    from pathlib import Path

    def require(condition, message):
        if not condition:
            raise ValueError(message)

    def integer(value, minimum=0):
        require(type(value) is int and value >= minimum, '整数类型/范围不符')
        return value

    def read(path):
        return json.loads(path.read_text(encoding='utf-8'))

    def sha(path):
        return hashlib.sha256(path.read_bytes()).hexdigest()

    control, run = Path(control), Path(run)
    sources = read(control / 'source-sha256.json')
    overrides = read(control / 'environment-overrides.json')
    require(overrides.get('BIV150_KV_VERIFY_RESTORE') == '1'
            and 'BIV150_FINITE_GROWTH_ADMISSION' not in overrides, '非原VERIFY1/finite未清除')
    manifest = read(run / 'manifest.json')
    require((run / 'exit-code').read_text().strip() == '0', 'driver未成功结束')
    require(sha(run / 'screen-driver.py') == 'bc51ac2d9daf90205bde362f8384b1ac34238e7be932e9a6df7fc618d7350be9', '非原bc51 driver')
    require(manifest['sha256']['/workspace/vllm-plugin-FL/benchmarks/benchmark_throughput_serve.py']
            == '0813eba574e9d1eb50c297c515baa426da1bcb61ce8c78a398b482f246005565', '官方benchmark源变化')
    require(manifest.get('context_long_screen') is True and manifest.get('seed') == 721201
            and all(manifest.get(name) is False for name in
                ('context_screen', 'decode_screen', 'host_profile', 'native_profile', 'smoke_only')),
            '仅原long/seed721201，无profiler')
    driver_ast = ast.parse((run / 'screen-driver.py').read_bytes())
    servers = [ast.literal_eval(n.value) for n in driver_ast.body
               if isinstance(n, ast.Assign) and len(n.targets) == 1
               and isinstance(n.targets[0], ast.Name) and n.targets[0].id == 'SERVER']
    require(len(servers) == 1 and read(run / 'launch-command.json') == manifest['server_command'] == servers[0],
            '实际SERVER偏离原命令')
    loads = read(run / 'load-commands.json')
    require(len(loads) == 1 and loads[0][3:] == ['context-16k-long', '16384', '1024', '64', '32', '721201'],
            '实际负载偏离原16K/1024/32/c64/seed')
    result_paths = list((run / 'context-16k-long/results').glob('*.json'))
    require(len(result_paths) == 1, 'benchmark必须有唯一原始结果')
    benchmark = read(result_paths[0])
    required_counts = {'num_prompts': 32, 'completed': 32, 'failed': 0,
                       'total_input_tokens': 524288, 'total_output_tokens': 32768, 'max_concurrency': 64}
    require(all(type(benchmark.get(k)) is int and benchmark[k] == value for k, value in required_counts.items()),
            'benchmark不是完整32成功/0失败或token数/并发偏离')
    duration = benchmark.get('duration')
    throughput = benchmark.get('total_token_throughput')
    require(type(duration) in (int, float) and math.isfinite(duration) and duration > 0
            and type(throughput) in (int, float) and math.isfinite(throughput)
            and abs(throughput - 557056 / duration) < 1e-8, 'benchmark时长/吞吐原始计数不闭合')
    events = []
    for line in (run / "server.log").read_text(encoding="utf-8", errors="replace").splitlines():
        if "BIV150_KV_PROTOCOL " in line:
            events.append(json.loads(line.split("BIV150_KV_PROTOCOL ", 1)[1]))
    require(bool(events), "无实际协议事件")

    def one(event):
        selected = [e for e in events if e["event"] == event]
        require(len(selected) == 1, "事件须恰一条：" + event)
        return selected[0]

    checked = one("FIRST_CHECKED")
    require(checked["eligible"] is True, "scope未实际命中")
    acks = [e for e in events if e["event"] == "RPC_ACK"]
    require([a["command"]["kind"] for a in acks] == ["SAVE", "RESTORE_FULL", "DROP"],
            "须真实SAVE→FULL→DROP三命令；ZERO/旧RESTORE fallback不算FULL通过")
    require([a["command"]["operation_serial"] for a in acks] == [1, 2, 3], "serial不符")
    save, full, drop = (a["command"] for a in acks)
    saved, restored, dropped = (a["worker_response"] for a in acks)
    key = save["key"]
    require(len(key) == 4 and all(a["command"]["key"] == key for a in acks), "事务key/epoch不同")
    r = integer(save["prefix_tokens"], 16)
    require(r % 16 == 0, "R非整页")
    pages, nbytes = r // 16, r * 43008
    require(nbytes <= 1 << 30, "payload越首版cap")
    for command, reply, event in zip((save, full, drop), (saved, restored, dropped), acks):
        require(command["prefix_tokens"] == r, "跨command的R变化")
        require(all(reply.get(k) == command[k] for k in ("key", "operation_serial", "kind", "pages", "prefix_tokens", "nbytes")), "ACK映射回显不符")
        require(reply["successful"] is True and reply["completed"] is True and reply["error"] is None, "无真实成功settled ACK")
        require(reply["worker_pid"] == event["pid"] == checked["pid"], "非同PID actual worker ACK")
        require(reply["transferred_bytes"] == command["nbytes"], "真实完成字节数不符")
    for command in (save, full):
        ids = command["pages"]
        require(command["nbytes"] == nbytes and len(ids) == pages and len(set(ids)) == pages
                and all(type(x) is int and x > 0 for x in ids), "非完整唯一的实际R页")
    runs = lambda ids: 1 + sum(b != a + 1 for a, b in zip(ids, ids[1:]))
    source_runs, destination_runs = runs(save["pages"]), runs(full["pages"])
    require(saved["full_restore_supported"] is True and saved["saved_layers"] == 42
            and saved["saved_page_bytes"] == 16384 and saved["saved_prefix_pages"] == pages
            and saved["saved_bytes"] == nbytes, "SAVE真ACK缺完整normal42能力")
    require(saved["submitted_bytes"] == nbytes and saved["copy_calls"] == saved["linear_calls"] + saved["pitched_calls"], "SAVE实际copy几何不符")
    require(restored["zero_stage_executed"] is False and restored["zero_calls"] == 0
            and restored["full_coverage"] is True and restored["destination_bound"] is True
            and restored["full_coverage_bytes"] == nbytes, "FULL完整覆盖/无ZERO证明缺失")
    require(restored["submitted_bytes"] == nbytes and restored["copy_calls"] == 42 * destination_runs, "FULL实际copy几何不符")
    require(restored["diagnostic_verify_requested"] is True and restored["verification_performed"] is True
            and restored["verification_passed"] is True and restored["verification_readback_bytes"] == nbytes
            and restored["verification_copy_calls"] == 42 * destination_runs, "42层全byte回读未通过")
    require(all(x["host_held"] is True and x["host_payload_bytes"] == nbytes for x in (saved, restored)), "copy期间host引用未持有")
    require(drop["pages"] == [] and drop["nbytes"] == 0 and dropped["dropped"] is True
            and dropped["host_held"] is False and dropped["host_payload_bytes"] == 0, "host未真实释放")
    freed, ordered = one("SAVE_ACK_FREE"), one("PRIVATE_PAGES_ORDERED")
    restore_ack, published = one("RESTORE_ACK"), one("RESUME_PUBLISHED")
    runner, consumer = one("RUNNER_RESUME_STATE_CHECKED"), one("RESUME_OUTPUT_PROCESSED")
    sequence = [acks[0], freed, ordered, acks[1], restore_ack, published, acks[2], runner, consumer]
    require([events.index(e) for e in sequence] == sorted(events.index(e) for e in sequence), "真实save/free/恢复/发布/消费次序不符")
    require(all(e["prefix_tokens"] == r for e in (freed, ordered, restore_ack, published)), "阶段R不符")
    require(ordered["page_count"] == pages and ordered["increasing_runs_after"] == destination_runs
            and full["pages"] == sorted(full["pages"]), "实际私有页排序/几何不符")
    require(all(ordered[k] is True for k in ("same_page_ids", "same_block_objects", "owned_list_identity", "future_free_order_may_change"))
            and ordered["host_logical_order_changed"] is False, "私有页映射proof缺失")
    expected_checks = {"cached_state_same", "computed_prefix", "cpu_computed_prefix", "full_block_replacement", "generator_same", "output_token_ids"}
    require(set(runner["checks"]) == expected_checks and all(v is True for v in runner["checks"].values())
            and runner["key"] == consumer["key"] == key and runner["before_attention"] is True
            and runner["gpu_completion_claimed"] is False and consumer["after_original_update"] is True, "原runner/实际消费未确认")
    consumed = integer(consumer["scheduled_tokens"], 1)
    for count in ("fast_rejects", "restore_skips", "saved", "restored", "published", "rollbacks"):
        values = [integer(e[count]) for e in events]
        require(values == sorted(values), "稀疏累计计数倒退：" + count)
    require(all(consumer[k] == 1 for k in ("saved", "restored", "published")) and consumer["rollbacks"] == 0
            and consumer["fast_rejects"] <= consumer["restore_skips"], "最终计数不符")
    geometry = {'prefix_tokens': r, 'pages': pages, 'nbytes': nbytes,
        'source_runs': source_runs, 'destination_runs': destination_runs,
        'save_copy_calls': saved['copy_calls'], 'full_copy_calls': restored['copy_calls'],
        'zero_calls': 0, 'verification_copy_calls': restored['verification_copy_calls'],
        'consumed_scheduled_tokens': consumed, 'fast_rejects': consumer['fast_rejects']}
    require(saved['save_implementation']=='C_batch_positive_stride_full_R' and saved['save_layers']==42
        and saved['save_runtime_sha256']==sources['vllm_fl/patches/biv150_kv_pitched_copy.py']
        and saved['save_bridge_sha256']==sources['vllm_fl/patches/biv150_kv_pitched_bridge.so']
        and saved['save_submission_completion_ack'] is False, '不是已验pitched-SAVE真实ACK')
    require(saved['save_verification_performed'] is True and saved['save_verification_passed'] is True
        and saved['save_verification_layers']==42 and saved['save_verification_bytes']==geometry['nbytes']
        and saved['save_verification_copy_calls']==42*geometry['source_runs'], 'SAVE源free前42字节证明缺失')
    require(saved['original_c95f_calls']==42*geometry['source_runs'], '原SAVE几何不符')
    planner = control / 'plugin-source/vllm_fl/patches/biv150_kv_pitched_copy.py'
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
    pid = checked['pid']
    log = (run / 'server.log').read_text(encoding='utf-8', errors='replace')

    def marker_rows(marker):
        rows = []
        for line in log.splitlines():
            if marker not in line:
                continue
            prefix, payload = line.split(marker, 1)
            value = json.loads(payload)
            require(type(value) is dict, '标记不是JSON对象: ' + marker)
            owner = re.search(r'EngineCore[^\s()]* pid=(\d+)', prefix)
            rows.append((None if owner is None else int(owner.group(1)), value))
        return rows

    scope_rows = marker_rows('BIV150_KV_PR24_SCOPE ')
    require(len(scope_rows) == 1, 'PR24 scope须恰一条')
    scope_pid, scope = scope_rows[0]
    require(scope.get('pid') == pid and (scope_pid is None or scope_pid == pid)
            and scope.get('native_methods_identity') is True and scope.get('q_kernel_binding_identity') is True,
            'PR24当前方法/库绑定与事务Engine不符')
    require('BIV150_Q_FRAGMENT_FALLBACK' not in log
            and 'BIV150_COMPUTE_ORDER_SCOPE_REJECTED' not in log
            and 'BIV150_KV_PR24_SCOPE_REJECTED' not in log, '当前Q/P/PR24 scope有fallback/reject')
    q_rows = [value for owner, value in marker_rows('BIV150_Q_FRAGMENT_SELECTED ')
              if owner == pid and value.get('mode') == 'selected']
    require(bool(q_rows), '同Engine当前Q SELECTED缺失')
    after_ready = log.rsplit('Application startup complete.', 1)[1] if 'Application startup complete.' in log else ''
    p_rows = []
    for line in after_ready.splitlines():
        if 'BIV150_COMPUTE_ORDER_FIRST_SELECTED ' not in line:
            continue
        prefix, payload = line.split('BIV150_COMPUTE_ORDER_FIRST_SELECTED ', 1)
        row = json.loads(payload)
        owner = re.search(r'EngineCore[^\s()]* pid=(\d+)', prefix)
        require(owner is not None and int(owner.group(1)) == pid
                and row.get('original_model_forward_returned') is True
                and row.get('runtime_mode') == 'NONE' and row.get('outside', 0) > 0
                and row.get('inverse_logits_order') == 'original_request_rows'
                and row.get('sampler_rows') == row.get('N'), 'P FIRST_SELECTED实际返回字段不符')
        p_rows.append(row)
    kv_sizes = re.findall(r'GPU KV cache size: ([\d,]+) tokens', log)
    require(len(kv_sizes) == 1, '须记录本次唯一KV容量，不套旧值')
    geometry.update(save_source_verification_bytes=saved['save_verification_bytes'],
        save_linear_calls=saved['linear_calls'], save_pitched_calls=saved['pitched_calls'],
        save_segments_per_layer=saved['save_segments_per_layer'], save_stream_handle=saved['save_current_stream_handle'])
    result = {'valid': True, 'status': 'passed_pr24_swap_verify1_mechanism', 'engine_pid': pid,
        'protocol_key': key, 'geometry': geometry, 'protocol_events': events,
        'benchmark_result': str(result_paths[0]), 'benchmark_sha256': sha(result_paths[0]),
        'benchmark': {k: benchmark[k] for k in (*required_counts, 'duration', 'total_token_throughput')},
        'kv_tokens': int(kv_sizes[0].replace(',', '')), 'pr24_binding_scope': scope,
        'q_selected_records': q_rows, 'p_after_ready_records': p_rows,
        'p_status': 'observed_selected' if p_rows else 'not_observed',
        'native_execution_per_request_asserted': False, 'gain_calculated': False,
        'legacy_protocol_validator_sha256': '2071bff34cdcd469294b406966ad86a0941d556b1d1e9ddd62dc87f927caf55b',
        'source_manifest_sha256': sha(control / 'source-sha256.json'),
        'limits': ['VERIFY1包含回读，不计性能收益，32/0和KV字节一致不替代完整准确率。',
                   'R来自固定plan_snapshot与原队列/设备围栏；原件未完整记录issued/queued/known，不能独立重算其上界。',
                   'P未观测允许通过，可能因自然有序而无需重排；未记录逐步scheduled_q，不据缺标记推断全负载形态。',
                   'native只证明当前源码/方法/SO绑定；不把安装标记或34层权重计数当作逐请求执行。',
                   'owner仍须完成源码/SO后态、进程/设备清理及DB恢复；本文件成功不覆盖收尾失败。']}
    (control / 'coverage.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return result


def run_owned(control, run, command, env, source, blobs, hashes):
    # bc51保持唯一GPU driver；外层仅交接同一设备锁，负责DB与原件收尾。
    import fcntl
    import traceback
    import time
    database = Path('/root/.flaggems/config_cache/TunedConfig_iluvatar_triton_3_6.db')
    lock = (ROOT / 'framework-device.lock').open('a')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    state = dict(owner_pid=os.getpid(), run=str(run), control=str(control), source=str(source),
                 source_count=TARGET_COUNT, base_commit=COMMIT, tree=OBSERVER_TREE, completed=False)
    backup, original, process, success = control / 'database-original.sqlite', None, None, False
    def state_save():
        (control / 'state.json').write_text(json.dumps(state, ensure_ascii=False, indent=2) + '\n')
    try:
        save(control / 'preflight.json', dict(**idle(), under_device_lock=True))
        shutil.copy2(database, backup)
        original = sha(backup)
        state['database_original_sha256'] = original
        if SEED_PATH.is_symlink() or sha(SEED_PATH) != SEED_SHA:
            raise ValueError('固定warmed DB原件不符')
        shutil.copy2(SEED_PATH, control / 'database-seed.sqlite')
        shutil.copy2(SEED_PATH, database)
        if sha(database) != SEED_SHA or sha(control / 'database-seed.sqlite') != SEED_SHA:
            raise ValueError('warmed DB复制后不符')
        state.update(database_before_sha256=SEED_SHA, database_seed=str(SEED_PATH))
        shutil.copyfile(ROOT / 'scripts/snapshot_tuning_db.py', control / 'snapshot_tuning_db.py')
        with (control / 'db-before.log').open('x') as output:
            subprocess.run(['python3', str(control / 'snapshot_tuning_db.py'), '--database', str(database),
                '--output', str(control / 'db-before')], stdout=output, stderr=subprocess.STDOUT, check=True)
        (control / 'command.txt').write_text(shlex.join(command) + '\n')
        save(control / 'scripts-sha256.json', SCRIPTS)
        fcntl.flock(lock, fcntl.LOCK_UN)
        with (control / 'runner.log').open('x') as log:
            process = subprocess.Popen(command, cwd='/workspace', env=env, stdin=subprocess.DEVNULL,
                stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
        (control / 'runner.pid').write_text(str(process.pid) + '\n')
        state.update(runner_pid=process.pid, stage='bc51-running')
        state_save()
        print(json.dumps(state), flush=True)
        code = process.wait()
        state.update(runner_exit_code=code, stage='cleanup')
        if code != 0 or (run / 'exit-code').read_text().strip() != '0':
            raise RuntimeError('bc51未成功结束；保存失败原件')
        verify_coverage(control, run)
        success = True
    except BaseException as error:
        state['error'] = repr(error)
        (control / 'failure.txt').write_text(traceback.format_exc())
        raise
    finally:
        cleanup_ok = True
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            state['postflight'] = idle()
            if process is not None:
                group = owned_group(process.pid)
                deadline = time.monotonic() + 6.0
                samples = [group]
                while not group['errors'] and any(x['state'] != 'Z' for x in group['members']) and time.monotonic() < deadline:
                    time.sleep(min(0.2, max(0, deadline - time.monotonic())))
                    group = owned_group(process.pid)
                    samples.append(group)
                save(control / 'owner-process-group-grace.json', dict(max_seconds=6, samples=samples))
                state['postflight_after_grace'] = idle()
                save(control / 'owner-process-group.json', group)
                if group['errors'] or any(x['state'] != 'Z' for x in group['members']):
                    raise RuntimeError('本次bc51进程组未清理，保留DB原件不恢复')
            if original is not None:
                with (control / 'db-after.log').open('x') as output:
                    subprocess.run(['python3', str(control / 'snapshot_tuning_db.py'), '--database', str(database),
                        '--output', str(control / 'db-after')], stdout=output, stderr=subprocess.STDOUT, check=True)
                shutil.copy2(database, control / 'database-after.sqlite')
                shutil.copy2(backup, database)
                state['database_restored'] = sha(database) == original
                if not state['database_restored']:
                    raise RuntimeError('DB恢复后hash不符')
        except Exception as error:
            cleanup_ok = False
            state.update(cleanup_error=repr(error), database_backup=str(backup))
        try:
            if source_maps(source) != (blobs, hashes) or source_maps(control / 'plugin-source') != (blobs, hashes):
                raise RuntimeError('诊断结束源码身份变化')
            state['source_unchanged'] = True
            if sha(control / 'native/biv150_native_w8a8.so') != read(control / 'native/runtime-receipt.json')['library_sha256']:
                raise RuntimeError('诊断结束native库变化')
            state['native_unchanged'] = True
        except Exception as error:
            cleanup_ok = False
            state['source_error'] = repr(error)
        state.update(completed=success and cleanup_ok, finished_utc=datetime.now(timezone.utc).isoformat())
        state_save()
        (control / 'exit-code').write_text('0\n' if success and cleanup_ok else '1\n')
        lock.close()
        if not cleanup_ok:
            raise RuntimeError('收尾未完成；参见state.json及保留的DB备份')




OBSERVER_MANIFEST_SHA = '74c884cc0af17530570edf7ab5bc7f48757d3dd1e7ee7a29990aadd48f5340ce'
OBSERVER_TREE = 'b2322c71c67f23e8b1ba509c7e0922dec18bfdec'
OBSERVER_PINS = {'vllm_fl/__init__.py': '791c38c20a648f4868e56e24efdae7351671960462232defb85997738f41a2b8', 'vllm_fl/patches/biv150_kv_worker.py': 'e7316368e6c3a28a4b910688426c707b9f6ddce1123a691795d689041e60776a', 'vllm_fl/patches/biv150_kv_protocol.py': 'b86a91fc8b9f7441080f4725a2652fe151a6a2770cedd137492e192e293c8f43', 'vllm_fl/patches/biv150_kv_transaction.py': '84be2242656e6ae0a30d65c803c2ae5076e836e0d1b6686731c4197a85b21883', 'vllm_fl/patches/biv150_kv_completion_probe.py': 'a4de3abea10b333aeb73d3c3ab49f82c91510c89cc8f9210c531f666feefb2c6', 'vllm_fl/patches/biv150_kv_pitched_bridge.so': '9e33ecbf9cf57f52469db6b1d509a600cd1a8eeafe78a54095e88dc474c71fc0', 'vllm_fl/patches/biv150_kv_pr24_scope.py': 'd22b4acd3405d820caf0a1f071afd51bece87f522238724135697b6a58bf6af7'}


def prepare_source(stamp, blobs, hashes, base_source):
    raw = (HERE / 'observer-manifest.json').read_bytes()
    manifest = json.loads(raw)
    if (hashlib.sha256(raw).hexdigest() != OBSERVER_MANIFEST_SHA
            or manifest['base_tree'] != TREE or manifest['source_count'] != TARGET_COUNT):
        raise ValueError('observer两路径身份变化')
    source = ROOT / 'code' / ('pr24-kv-swap-v1-' + stamp)
    if source.exists():
        raise FileExistsError(source)
    expected = dict(blobs)
    payload = {}
    for name, pin in OBSERVER_PINS.items():
        data = (HERE / 'files' / name).read_bytes()
        if hashlib.sha256(data).hexdigest() != pin:
            raise ValueError('observer payload变化：' + name)
        payload[name] = data
        expected[name] = dict(mode='100644', sha=hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest())
    delta = {name: dict(before=blobs.get(name), after=expected[name], sha256=hashlib.sha256(data).hexdigest())
             for name, data in payload.items()}
    if manifest['changed_paths'] != delta or manifest['target_tree'] != OBSERVER_TREE:
        raise ValueError('不是声明的PR24加原KV/scope差异')
    shutil.copytree(base_source, source, symlinks=True, ignore=shutil.ignore_patterns('.git','__pycache__','*.pyc','*.pyo'))
    for name, data in payload.items():
        target = source / name
        if target.is_symlink():
            raise ValueError('不覆写payload symlink')
        target.write_bytes(data)
        target.chmod(0o644)
    actual_blobs, actual_hashes = source_maps(source)
    if (len(actual_blobs) != TARGET_COUNT or actual_blobs != expected
            or {k:v for k,v in actual_hashes.items() if k not in payload}
                != {k:v for k,v in hashes.items() if k not in payload}
            or source_maps(base_source) != (blobs, hashes)):
        raise ValueError('原PR24或新473出现未声明变更')
    return source, actual_blobs, actual_hashes


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-dir', type=Path, required=True)
    parser.add_argument('--native-build-manifest', type=Path, required=True)
    args = parser.parse_args()
    base_source = args.source_dir
    blobs, hashes = source_ready(base_source)
    native, library, build_log = native_ready(args.native_build_manifest, hashes)
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    source, blobs, hashes = prepare_source(stamp, blobs, hashes, base_source)
    for name, pin in SCRIPTS.items():
        if sha(ROOT / 'scripts' / name) != pin:
            raise ValueError('原bc51/负载/快照/monitor变化：' + name)
    env = os.environ.copy()
    removed = [name for name in env if name.startswith('BIV150_') or name in
               ('MINICPM_NATIVE_PROFILE_EVENTS', 'MINICPM_DECODE_GAP_RUN_DIR')]
    for name in removed:
        env.pop(name)
    env['BIV150_KV_VERIFY_RESTORE'] = '1'
    for name in ('VLLM_FL_BIV150_PREFILL_NORMALIZE', 'VLLM_FL_BIV150_GQA_DECODE', 'VLLM_FL_BIV150_Q_FRAGMENT', 'VLLM_FL_BIV150_NATIVE_W8A8'):
        if env.get(name, '1') != '1':
            raise ValueError('不允许关闭受测normalized/GQA：' + name)
    run = ROOT / 'framework' / (stamp + '-pr24-kv-swap-v1-verify1-context16k-long')
    control = run.with_name(run.name + '-control')
    if run.exists():
        raise FileExistsError(run)
    control.mkdir(parents=True, exist_ok=False)
    shutil.copytree(source, control / 'plugin-source', symlinks=True,
                    ignore=shutil.ignore_patterns('.git', '__pycache__', '*.pyc', '*.pyo'))
    if source_maps(source) != (blobs, hashes) or source_maps(control / 'plugin-source') != (blobs, hashes):
        raise ValueError('归档期间源码变化')
    save(control / 'source-sha256.json', hashes)
    save(control / 'source-git-blobs.json', blobs)
    for name in ('candidate-git-blobs.json', 'candidate-manifest.json', 'observer-manifest.json'):
        shutil.copyfile(HERE / name, control / name)
    shutil.copyfile(__file__, control / 'launch_kv_verify1.py')
    native_dir = control / 'native'
    native_dir.mkdir()
    runtime_library = native_dir / 'biv150_native_w8a8.so'
    shutil.copyfile(library, runtime_library)
    shutil.copyfile(build_log, native_dir / 'build.log')
    shutil.copyfile(args.native_build_manifest, native_dir / 'build-manifest.original.json')
    if (sha(runtime_library) != native['library_sha256']
            or sha(native_dir / 'build.log') != native['build_log_sha256']):
        raise ValueError('native复制后身份变化')
    receipt = dict(native, runtime_library=str(runtime_library))
    receipt_path = native_dir / 'runtime-receipt.json'
    save(receipt_path, receipt)
    env['BIV150_NATIVE_W8A8_LIBRARY'] = str(runtime_library)
    env['BIV150_RESUME_NATIVE_RECEIPT'] = str(receipt_path)
    env['BIV150_RESUME_NATIVE_RECEIPT_SHA256'] = sha(receipt_path)
    (control / 'q-hoist-artifacts').mkdir()
    env['BIV150_Q_FRAGMENT_SERVICE_ARTIFACT_DIR'] = str(control / 'q-hoist-artifacts')
    save(control / 'environment-overrides.json', {name:value for name,value in env.items() if name.startswith('BIV150_') or name.startswith('VLLM_FL_BIV150_')})
    save(control / 'purpose.json', dict(kind='PR24加原SAVE/FULL VERIFY1组合字节门，不计算收益' ,
        source=str(source), source_count=TARGET_COUNT, base_source=str(base_source),
        base_commit=COMMIT, base_tree=TREE, tree=OBSERVER_TREE,
        removed_environment_names=sorted(removed), native_library_sha256=native['library_sha256'],
        limits=['完整PR24 main仅旧KV协议接线与新scope；P/Q/native原字节，非profile' ,
            '原bc51 32x16K+1024/seed721201/SERVER/锁/到达/采样不变，VERIFY1含全字节回读' ,
            '原单victim完整页R、queued/fence/ACK/私有页序/消费者/host释放；不自动VERIFY0或accuracy' ,
            '新实例新main诊断不继承其它实例PR24容量/正确性/性能资格']))
    command = ['python3', str(ROOT / 'scripts/run_framework_screen.py'), str(run), '--source-dir', str(source),
        '--context-long-screen', '--seed', '721201', '--require-log-marker', 'BIV150_KV_PROTOCOL_INSTALLED']
    quota_root=Path('/sys/fs/cgroup/cpu,cpuacct')
    quota={name:(quota_root/name).read_text() for name in ('cpu.cfs_quota_us','cpu.cfs_period_us','cpu.stat')}
    if int(quota['cpu.cfs_quota_us']) != 6*int(quota['cpu.cfs_period_us']):
        raise ValueError('不是当前6CPU quota，拒绝静默改变条件')
    save(control / 'cpu-before.json', quota)
    run_owned(control, run, command, env, source, blobs, hashes)



if __name__ == '__main__':
    main()
