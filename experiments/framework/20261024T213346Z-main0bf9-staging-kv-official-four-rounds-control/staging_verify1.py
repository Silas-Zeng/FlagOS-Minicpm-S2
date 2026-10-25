def _verify_staging_submission(control, sources, reply, geometry, direction):
    """仅核已完成ACK与冻结文件；不导入Torch/加载SO或执行设备planner。"""
    import hashlib
    from pathlib import Path

    def require(ok, message):
        if not ok:
            raise ValueError(message)

    require(direction in ('save', 'restore'), '非法staging方向')
    pins = {
        'runtime': ('biv150_kv_staging.py', 'bd02b2b83e5990ce8c9a75076f1e64396f1770aa9f2630eaf83f69a3a10477ac'),
        'source': ('biv150_kv_staging_bridge.cu', 'f1b576b6c3eba2bf22257695aa5d8b5a39a2086fd31b2f213540a828ecb9d74b'),
        'library': ('biv150_kv_staging_bridge.so', '71608fea43df03f279985f18e505aa652393f0a59884142422c7e195bdf54223'),
    }
    for kind, (name, digest) in pins.items():
        relative = 'vllm_fl/patches/' + name
        path = Path(control) / 'plugin-source' / relative
        require(not path.is_symlink() and path.is_file()
                and sources.get(relative) == digest
                and hashlib.sha256(path.read_bytes()).hexdigest() == digest
                and reply.get('stage_' + kind + '_sha256') == digest,
                'staging实际文件/响应身份不符: ' + kind)
    implementation = {'save': 'GPU_gather_contiguous_D2H_full_R',
                      'restore': 'GPU_scatter_contiguous_H2D_full_R'}[direction]
    require(reply.get(direction + '_implementation') == implementation
            and type(reply.get(direction + '_layers')) is int and reply[direction + '_layers'] == 42
            and reply.get(direction + '_submission_completion_ack') is False,
            'staging方向/42层或提交非ACK合同不符')
    expected = dict(copy_calls=43, kernels=42, index_copies=1, data_copies=42,
                    index_bytes=geometry['pages'] * 8, scratch_bytes=geometry['pages'] * 16384,
                    device_index_bytes=geometry['pages'] * 8, submitted_bytes=geometry['nbytes'])
    require(all(type(reply.get(k)) is int and reply[k] == v for k, v in expected.items()),
            'staging提交几何/索引与payload字节不符')
    require(reply.get('staging_temporary_released') is True,
            'staging完成后scratch/索引临时引用未释放')
    stream = reply.get(direction + '_current_stream_handle')
    require(type(stream) is int and 0 <= stream < 1 << 64, 'staging实际stream handle不符')
    return dict(expected, layers=42, stream_handle=stream, temporary_released=True,
                payload_bytes=geometry['nbytes'], total_dma_bytes=geometry['nbytes'] + expected['index_bytes'],
                stage_sha256={kind: digest for kind, (_, digest) in pins.items()},
                boundary='43次SDK copy包含一次索引上传；42次gather/scatter另外计数，不由调用数推收益。')


def verify_coverage(control, run):
    """PR24+既有SAVE/FULL的VERIFY1后验；仅消费原件，不提供收益或完整准确率结论。

    事务段复用2071bff3，SAVE源与FULL目的仍逐层完整回读；仅替换staging提交
    几何、实际源/SO身份及每方向完成后临时量释放验收。完整538来源和DB收尾由owner负责。
    """
    import ast
    import hashlib
    import json
    import math
    import re
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
    require(saved["submitted_bytes"] == nbytes, "SAVE实际payload字节不符")
    require(restored["zero_stage_executed"] is False and restored["zero_calls"] == 0
            and restored["full_coverage"] is True and restored["destination_bound"] is True
            and restored["full_coverage_bytes"] == nbytes, "FULL完整覆盖/无ZERO证明缺失")
    require(restored["submitted_bytes"] == nbytes, "FULL实际payload字节不符")
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
    require(saved['save_verification_performed'] is True and saved['save_verification_passed'] is True
        and saved['save_verification_layers']==42 and saved['save_verification_bytes']==geometry['nbytes']
        and saved['save_verification_copy_calls']==42*geometry['source_runs'], 'SAVE源free前42字节证明缺失')
    save_geometry = _verify_staging_submission(control, sources, saved, geometry, 'save')
    restore_geometry = _verify_staging_submission(control, sources, restored, geometry, 'restore')
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
        save_copy_calls=saved['copy_calls'], save_kernels=saved['kernels'],
        save_stream_handle=saved['save_current_stream_handle'],
        staging_temporary_released_both=save_geometry['temporary_released'] and restore_geometry['temporary_released'])
    result = {'valid': True, 'status': 'passed_main0bf9_staging_verify1_mechanism', 'engine_pid': pid,
        'protocol_key': key, 'geometry': geometry, 'save_geometry': save_geometry, 'restore_geometry': restore_geometry, 'protocol_events': events,
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
