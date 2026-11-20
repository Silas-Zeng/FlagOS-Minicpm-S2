def verify_coverage(control, run):
    """PR24+既有SAVE/FULL的VERIFY1后验；仅消费原件，不提供收益或完整准确率结论。

    事务段复用2071bff3，pitched-SAVE段复用6c5f73aa；只替换SAVE几何断言、
    planner副本位置及旧包装/标记验收。完整535来源和DB收尾由owner负责。
    """
    import ast
    import importlib.util
    import sys
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
    require(sha(run / 'screen-driver.py') == 'f02358d05e08c8e6eae3154bfbda58685f2875ae35850f61322cf064b664e0ca', '非冻结同服务语义门driver')
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
    require(restored["submitted_bytes"] == nbytes and restored["copy_calls"] == restored["linear_calls"] + restored["pitched_calls"], "FULL实际copy几何不符")
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

    restore_geometry = verify_restore_geometry(control, sources, acks[1], geometry)
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
    result = {'valid': True, 'status': 'passed_main0bf9_restore_pitched_verify1_mechanism', 'engine_pid': pid,
        'protocol_key': key, 'geometry': geometry, 'restore_geometry': restore_geometry, 'protocol_events': events,
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
