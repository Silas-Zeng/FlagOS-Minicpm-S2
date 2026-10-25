#!/usr/bin/env python3
"""默认共享缓存的首启/重启语义诊断；不产生官方成绩、不改服务参数。"""
from __future__ import annotations

import argparse
import ast
from datetime import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import time
import traceback
import urllib.request

ROOT = Path('/workspace/experiments/minicpm-s2')
COMMON = ROOT / 'scripts/run_accuracy_gate.py'
COMMON_SHA = '35d30dfa4fc4d583c7fc62db1f18c992a7fd6a7e54fab95749710759b5df6a54'
MONITOR = ROOT / 'scripts/monitor_gpu.sh'
MONITOR_SHA = 'af90002eebd4dade188c8efd58e025c3ce3cbcfa022a0e2d7a49fe2e8870f88a'
SAFE_ENV = {'VLLM_PLUGINS', 'VLLM_DISABLE_COMPILE_CACHE', 'BIV150_NATIVE_W8A8_LIBRARY',
            'PYTHONPATH', 'PYTHONUNBUFFERED', 'XDG_CACHE_HOME', 'USE_FLAGGEMS',
            'VLLM_FL_PREFER_ENABLED', 'VLLM_FL_BIV150_NATIVE_W8A8',
            'VLLM_FL_BIV150_GQA_TARGET_PROGRAMS', 'VLLM_FL_CONFIG', 'VLLM_FL_OP_CONFIG'}


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def dotted(node):
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return dotted(node.value) + '.' + node.attr
    return ''


def native_graph(text):
    """静态解析实际 FX 的 Assign/AnnAssign 调用与权重参数别名；不执行图。"""
    tree = ast.parse(text)
    calls = []
    for function in (n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))):
        aliases = {arg.arg: {arg.arg} for arg in function.args.args}
        for statement in function.body:
            if not isinstance(statement, (ast.Assign, ast.AnnAssign)):
                continue
            value = statement.value
            targets = statement.targets if isinstance(statement, ast.Assign) else [statement.target]
            if isinstance(value, ast.Call) and dotted(value.func) in {
                'torch.ops.biv150_native.gate_silu_auto',
                'torch.ops.biv150_native.gate_silu_auto.default',
            }:
                require(len(value.args) >= 4, 'native FX 调用缺少实际权重参数')
                bindings = []
                for arg in value.args[1:4]:
                    origins = set()
                    for node in ast.walk(arg):
                        if isinstance(node, ast.Name):
                            origins.update(aliases.get(node.id, {node.id}))
                    layers = {int(m.group(1)) for name in origins
                              for m in re.finditer(r'(?:^|_)layers_modules_(\d+)(?:_|$)', name)}
                    require(len(layers) == 1, 'native FX 权重参数层号不唯一: ' + repr(sorted(origins)))
                    bindings.append(next(iter(layers)))
                require(len(set(bindings)) == 1, 'native FX 的 wq/scales/original 跨层')
                calls.append({'function': function.name, 'line': statement.lineno,
                              'operator': dotted(value.func), 'layer': bindings[0]})
            # 只追踪直接名称别名，不能把中间计算结果误认为其所有输入权重。
            if isinstance(value, ast.Name):
                for target in targets:
                    if isinstance(target, ast.Name):
                        aliases[target.id] = aliases.get(value.id, {value.id}).copy()
    layers = [row['layer'] for row in calls]
    require(len(calls) == 34 and sorted(layers) == list(range(4, 38)),
            '真实图未闭合 34 个 native 层 4..37: ' + repr(layers))
    return {'native_call_count': len(calls), 'layers': sorted(layers), 'calls': calls}


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


def identity(source, mapping, library, library_sha):
    for relative, expected in mapping.items():
        entry = source / relative
        path = entry.resolve(strict=True)
        require(path.is_relative_to(source) and path.is_file(), '非法源码路径: ' + relative)
        # Git mode 120000 的 blob 是链接文本；仍要求实际目标存在且留在本源码树。
        digest = hashlib.sha256(os.fsencode(os.readlink(entry))).hexdigest() if entry.is_symlink() else sha(path)
        require(digest == expected, '源码身份变化: ' + relative)
    actual = {str(p.relative_to(source)).replace('\\', '/') for p in source.rglob('*')
              if p.is_file() and '__pycache__' not in p.parts and p.suffix not in {'.pyc', '.pyo'}
              and '.git' not in p.parts}
    require(actual == set(mapping), '源码闭包增删: ' + repr(sorted(actual ^ set(mapping))))
    require(sha(library) == library_sha, 'native SO 身份变化')
    return {'source_files': len(mapping), 'library_sha256': library_sha}


def cache_snapshot(root):
    # 保留共享旧缓存。仅记录已有模型图的身份，不读写/清除其它任务的缓存。
    return {str(p.resolve()): sha(p) for p in root.glob('torch_compile_cache/**/computation_graph.py') if p.is_file()}


def relative_handles(handles, directory):
    """保留编译key/符号/相对产物身份，只去各自backbone目录前缀。"""
    root = Path(directory).resolve()
    normalized = []
    for value in handles:
        require(isinstance(value, dict), '编译handle记录非dict')
        handle = value.get('graph_handle')
        require(isinstance(handle, (tuple, list)) and len(handle) == 2,
                '编译handle格式不符')
        artifact = Path(handle[1]).resolve()
        require(artifact.is_relative_to(root) and artifact != root,
                '编译artifact不在各自实际图目录内')
        normalized.append({'cache_key': value['cache_key'],
                           'graph_handle': [handle[0], artifact.relative_to(root).as_posix()]})
    return normalized


def graph_evidence(folder, cache_root, before, first=None, output_folder=None):
    output_folder = folder if output_folder is None else output_folder
    text = (folder / 'server.log').read_text(errors='replace')
    text = re.sub(r'\x1b\[[0-9;]*m', '', text)
    declared = re.findall(r"Using cache directory: (.+?) for vLLM's torch\.compile", text)
    aot = re.findall(r'Directly load AOT compilation from path (\S+)', text)
    saved_aot = re.findall(r'saved AOT compiled function to (\S+)', text)
    paths = {Path(path.strip()).resolve() for path in declared}
    require(len(paths) == 1, '日志未给出唯一真实模型 cache 目录: ' + repr([str(x) for x in paths]))
    path = paths.pop()
    require(path.is_relative_to(cache_root / 'torch_compile_cache'), '模型图不在默认共享缓存')
    graph = path / 'computation_graph.py'
    require(graph.is_file(), '已宣告模型图不存在')
    evidence = {'directory': str(path), 'graph_path': str(graph), 'graph_sha256': sha(graph),
                'aot_loaded_paths': aot, 'graph': native_graph(graph.read_text()), 'files': {}}
    target = output_folder / 'cache-evidence'
    target.mkdir()
    for name in ('computation_graph.py', 'vllm_compile_cache.py', 'cache_key_factors.json'):
        file = path / name
        require(file.is_file(), '真实图缺少缓存文件: ' + name)
        shutil.copyfile(file, target / name)
        evidence['files'][name] = sha(file)
    entries = ast.literal_eval((path / 'vllm_compile_cache.py').read_text())
    require(isinstance(entries, dict) and entries, '实际编译 cache entry 为空')
    handles = []
    for value in entries.values():
        require(isinstance(value, dict) and 'graph_handle' in value and 'cache_key' in value, '编译 cache entry 非预期')
        handle = value['graph_handle']
        require(isinstance(handle, (tuple, list)) and len(handle) == 2, '编译 handle 非预期')
        artifact = Path(handle[1]).resolve(strict=True)
        require(artifact.is_relative_to(path), '编译 artifact 不属于本次图目录')
        handles.append({'cache_key': value['cache_key'], 'graph_handle': list(handle)})
    evidence['compiled_handles'] = handles
    evidence['load_lines'] = [line for line in text.splitlines()
                              if 'Directly load AOT compilation from path ' in line
                              or 'Directly load the compiled graph(s) for compile range ' in line]
    evidence['aot_files'] = []
    for name in sorted(set(aot + saved_aot)):
        model = Path(name).resolve(strict=True)
        require(model.is_relative_to(cache_root / 'torch_compile_cache/torch_aot_compile') and model.is_file(),
                '实际 AOT 加载不在默认缓存')
        evidence['aot_files'].append({'path': str(model), 'sha256': sha(model)})
    fingerprints = [json.loads(line.split('BIV150_COMPILE_SEMANTICS ', 1)[1])
                    for line in text.splitlines() if 'BIV150_COMPILE_SEMANTICS ' in line]
    require(fingerprints and all(x == fingerprints[0] for x in fingerprints), 'cache 语义指纹未闭合')
    evidence['fingerprint'] = fingerprints[0]
    require(evidence['fingerprint'].get('native_enabled') is True, 'cache 指纹未启用 native')
    if first is None:
        require(str(graph) not in before, '首启复用了已有模型图；本诊断不删除缓存')
        require(not aot and not evidence['load_lines'], '首启实际加载已有编译图')
        require(len(saved_aot) == 1, '首启没有唯一实际 AOT 保存证据')
    else:
        require(evidence['graph_sha256'] == first['graph_sha256'],
                '二启模型图内容变化')
        require(evidence['fingerprint'] == first['fingerprint'], '二启源码/语义指纹变化')
        require(relative_handles(evidence['compiled_handles'], evidence['directory'])
                == relative_handles(first['compiled_handles'], first['directory']), '二启编译 handle 变化')
        evidence['verification_directory'] = first['directory']
        evidence['verification_cache_relocated'] = evidence['directory'] != first['directory']
        require(aot and evidence['aot_files'] == first['aot_files'], '二启未实际加载首启相同 AOT 文件')
    save(output_folder / 'graph-evidence.json', evidence)
    return evidence


def final_answer(content, expected):
    require(isinstance(content, str), '最终可见输出不是文本')
    def boundary(text):
        return re.sub(r'^(?:\s|\\[nrt])+|(?:\s|\\[nrt])+$', '', text)
    visible = boundary(content)
    while visible.startswith('<think>'):
        end = visible.find('</think>', len('<think>'))
        require(end >= 0, 'think 块未闭合')
        require('<think>' not in visible[len('<think>'):end], '嵌套 think 块不接受')
        visible = boundary(visible[end + len('</think>'):])
    require(visible, '剥离显式闭合 think 后最终可见输出为空')
    match = re.fullmatch(r'\s*(?:(?:答案(?:是|为)?|Answer)\s*[:：]?\s*)?(?:\\boxed\{)?\s*([+-]?\d+)\s*\}?\s*[。.]?\s*', visible, re.IGNORECASE)
    require(match is not None and int(match.group(1)) == expected, '可见答案不符合预期: ' + repr(visible))
    return visible


def audit_prior(prior, audit, source, mapping, library, library_sha, cache_root, common, env):
    require(prior.is_relative_to(ROOT / 'framework') and prior != ROOT / 'framework', 'prior-run 不在 framework')
    require(prior != audit and not audit.is_relative_to(prior), '接续输出不能写入 prior-run')
    manifest = json.loads((prior / 'startup-1/manifest.json').read_text())
    result = json.loads((prior / 'result.json').read_text())
    original_map = json.loads((prior / 'driver-assets/source-map.json').read_text())
    before = json.loads((prior / 'cache-before.json').read_text())
    require(original_map == mapping and manifest['source_dir'] == str(source) and manifest['library'] == str(library), '原首启 source/map/SO 路径不同')
    require(manifest['identity'] == identity(source, mapping, library, library_sha), '原首启源码或 SO 身份不同')
    require(manifest['server_command'] == common.SERVER and manifest['cache_root'] == str(cache_root), '原首启 SERVER/cache 参数不同')
    require(manifest['environment'] == {k: v for k, v in sorted(env.items()) if k in SAFE_ENV}, '原首启服务环境不同')
    require(result.get('cleanup_errors') == [] and result.get('exit_code') == 1 and result.get('completed') is False,
            '原首启不是已完整清理的失败诊断')
    require('可见答案不符合预期: add:' in result.get('error', '') and result.get('rounds') == [], '原失败不是首题格式误判')
    require(result.get('identity_after') == manifest['identity'], '原退出时 source/SO 未确认一致')
    require(sha(prior / 'driver-assets/driver.py') == 'bf48ae0faa725a7ded3559865a4bcf8d73f35ee43a33e0f26f21a12eef5a709f', '原 driver 身份不同')
    require(sha(prior / 'driver-assets/run_accuracy_gate.py') == COMMON_SHA and sha(prior / 'driver-assets/monitor_gpu.sh') == MONITOR_SHA,
            '原 common/monitor 身份不同')
    request = json.loads((prior / 'startup-1/add-request.json').read_text())
    require(request == {'model': 'minicpm', 'messages': [
        {'role': 'system', 'content': '请只输出最终答案的十进制整数，不要解释，也不要重复题目。'},
        {'role': 'user', 'content': '计算 27 + 58。'}], 'temperature': 0, 'max_tokens': 1024}, '原首题不是已知请求')
    response = json.loads((prior / 'startup-1/add-response.json').read_text())
    visible = final_answer(response['choices'][0]['message'].get('content'), 85)
    for path, digest in before.items():
        require(Path(path).is_file() and sha(path) == digest, '共享旧图已改变: ' + path)
    audit.mkdir()
    first = graph_evidence(prior / 'startup-1', cache_root, before, output_folder=audit)
    finished = datetime.fromisoformat(result['finished_utc']).timestamp()
    files = [Path(first['directory']) / name for name in first['files']]
    files += [Path(item['path']) for item in first['aot_files']]
    files += [Path(item['graph_handle'][1]) for item in first['compiled_handles']]
    timestamps = []
    for file in files:
        require(file.is_file() and file.stat().st_mtime <= finished, '缓存文件在原诊断结束后变动: ' + str(file))
        timestamps.append({'path': str(file), 'mtime': file.stat().st_mtime, 'sha256': sha(file)})
    prior_paths = ['startup-1/manifest.json', 'startup-1/server.log', 'startup-1/add-request.json',
                   'startup-1/add-response.json', 'driver-assets/source-map.json', 'cache-before.json', 'result.json']
    audit_data = {'prior_run': str(prior), 'prior_files': {name: sha(prior / name) for name in prior_paths},
                  'corrected_prior_answer': visible, 'expected': 85, 'cache_files': timestamps,
                  'limitation': '原失败发生在图证据归档之前；本次只读按原日志与结束时间核现存文件并首次保存其哈希，原件保持失败。'}
    save(audit / 'audit.json', audit_data)
    return first, audit_data


def arithmetic(folder):
    cases = [('add', '计算 27 + 58。', 85), ('multiply', '计算 17 × 19。', 323),
             ('divide', '计算 144 ÷ 12。', 12),
             ('long-prefill', ('以下均为无关背景，请勿计算或回答：山边有树，河边有桥。\n' * 256)
              + '\n背景结束。唯一问题：计算 37 + 58。', 95)]
    rows = []
    for name, prompt, expected in cases:
        request = {'model': 'minicpm', 'messages': [
            {'role': 'system', 'content': '请只输出最终答案的十进制整数，不要解释，也不要重复题目。'},
            {'role': 'user', 'content': prompt}], 'temperature': 0, 'max_tokens': 1024}
        save(folder / (name + '-request.json'), request)
        started = time.monotonic()
        http = urllib.request.Request('http://127.0.0.1:9031/v1/chat/completions',
                                      data=json.dumps(request).encode(), headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(http, timeout=600) as response:
            value = json.load(response)
        save(folder / (name + '-response.json'), value)
        message = value['choices'][0]['message']
        content = message.get('content')
        visible = final_answer(content, expected)
        usage = value.get('usage', {})
        if name == 'long-prefill':
            require(usage.get('prompt_tokens', 0) >= 4096, '长 prefill 未达到 4096 prompt tokens')
        rows.append({'name': name, 'expected': expected, 'visible': visible, 'usage': usage,
                     'elapsed_seconds': time.monotonic() - started, 'correct': True})
        save(folder / 'requests.json', rows)
    return rows


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run_dir', type=Path)
    parser.add_argument('--source-dir', required=True, type=Path)
    parser.add_argument('--source-sha256-json', required=True, type=Path)
    parser.add_argument('--library', required=True, type=Path)
    parser.add_argument('--library-sha256', required=True)
    parser.add_argument('--prior-run', required=True, type=Path, help='已清理的首启格式误判原件，只读接续')
    args = parser.parse_args(argv)
    run, source, library = args.run_dir.resolve(), args.source_dir.resolve(strict=True), args.library.resolve(strict=True)
    require(run.is_relative_to(ROOT / 'framework') and run != ROOT / 'framework', 'run 必须在 framework 下的新目录')
    require(source.is_relative_to(ROOT / 'code'), 'source 必须是独立 code 目录')
    mapping = json.loads(args.source_sha256_json.read_text())
    require(isinstance(mapping, dict) and mapping and all(isinstance(v, str) and re.fullmatch('[0-9a-f]{64}', v) for v in mapping.values()),
            'source map 必须为 relative_path -> sha256 JSON')
    require(sha(COMMON) == COMMON_SHA and sha(MONITOR) == MONITOR_SHA, '受测 common/monitor 身份变化')
    spec = importlib.util.spec_from_file_location('cache_service_common', COMMON)
    common = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(common)
    run.mkdir(parents=True, exist_ok=False)
    result = {'kind': '默认缓存首启/重启语义诊断；不是官方准确率或性能成绩', 'completed': False,
              'rounds': [], 'cleanup_errors': [], 'owned_processes': []}
    save(run / 'result.json', result)
    archive = run / 'driver-assets'
    archive.mkdir()
    for path in (Path(__file__), COMMON, MONITOR):
        shutil.copyfile(path, archive / path.name)
    save(archive / 'source-map.json', mapping)
    lock = None
    processes = []
    handlers = {}
    status = 1
    try:
        import fcntl
        lock = (ROOT / 'framework-device.lock').open('a')
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        for signum in (signal.SIGTERM, signal.SIGINT):
            handlers[signum] = signal.getsignal(signum)
            signal.signal(signum, lambda number, frame: (_ for _ in ()).throw(KeyboardInterrupt('signal ' + str(number))))
        identity(source, mapping, library, args.library_sha256)
        env = common.child_environment(source)
        env.pop('VLLM_CACHE_ROOT', None)
        env.pop('TORCHINDUCTOR_CACHE_DIR', None)
        env.update(VLLM_DISABLE_COMPILE_CACHE='0', BIV150_NATIVE_W8A8_LIBRARY=str(library))
        cache_root = (Path(env.get('XDG_CACHE_HOME', str(Path.home() / '.cache'))).expanduser() / 'vllm').resolve()
        before = cache_snapshot(cache_root)
        save(run / 'cache-before.json', before)
        first, prior_audit = audit_prior(args.prior_run.resolve(strict=True), run / 'prior-audit',
                                        source, mapping, library, args.library_sha256, cache_root, common, env)
        result['prior_audit'] = prior_audit
        for index in (2,):
            folder = run / ('startup-' + str(index))
            folder.mkdir()
            manifest = {'started_utc': common.utc(), 'server_command': common.SERVER, 'source_dir': str(source),
                        'library': str(library), 'identity': identity(source, mapping, library, args.library_sha256),
                        'preflight': common.preflight(), 'cpu_before': common.cpu_state(), 'cache_root': str(cache_root),
                        'environment': {k: v for k, v in sorted(env.items()) if k in SAFE_ENV},
                        'removed_environment': ['VLLM_CACHE_ROOT', 'TORCHINDUCTOR_CACHE_DIR']}
            save(folder / 'manifest.json', manifest)
            round_processes = []
            try:
                with (folder / 'server.log').open('w') as output:
                    server = subprocess.Popen(common.SERVER, cwd='/workspace', env=env, stdout=output,
                                              stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, start_new_session=True)
                processes.append(server)
                round_processes.append(server)
                (folder / 'server.pid').write_text(str(server.pid) + '\n')
                with (folder / 'monitor.log').open('w') as output:
                    monitor = subprocess.Popen(['bash', str(archive / MONITOR.name), str(server.pid), str(folder / 'gpu.csv')],
                                               stdout=output, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, start_new_session=True)
                processes.append(monitor)
                round_processes.append(monitor)
                (folder / 'monitor.pid').write_text(str(monitor.pid) + '\n')
                result['owned_processes'] += [{'role': role, 'startup': index, 'pid': proc.pid}
                                              for role, proc in [('server', server), ('monitor', monitor)]]
                save(run / 'result.json', result)
                common.wait_ready(server, 'BIV150_COMPILE_SEMANTICS ', folder)
                rows = arithmetic(folder)
                require(server.poll() is None, '服务在语义请求后异常退出')
                evidence = graph_evidence(folder, cache_root, before, first)
                first = evidence if index == 1 else first
                identity(source, mapping, library, args.library_sha256)
                result['rounds'].append({'startup': index, 'correct': len(rows), 'graph': evidence,
                                         'finished_utc': common.utc()})
            finally:
                clean_groups(common, round_processes, folder, result)
                manifest['cpu_after'] = common.cpu_state()
                save(folder / 'manifest.json', manifest)
                save(run / 'result.json', result)
            require(not result['cleanup_errors'], '本轮设备清理失败')
        for path, digest in before.items():
            require(Path(path).is_file() and sha(path) == digest, '共享旧图被更改或删除: ' + path)
        for relative, digest in prior_audit['prior_files'].items():
            require(sha(args.prior_run / relative) == digest, '原失败证据被更改: ' + relative)
        identity(source, mapping, library, args.library_sha256)
        result['completed'] = True
        status = 0
    except BaseException as error:
        result['error'] = repr(error)
        (run / 'failure.txt').write_text(traceback.format_exc())
    finally:
        if processes:
            clean_groups(common, processes, run, result)
        if lock is not None:
            try:
                result['postflight'] = common.preflight()
                result['identity_after'] = identity(source, mapping, library, args.library_sha256)
            except BaseException as error:
                result['cleanup_errors'].append(repr(error))
            lock.close()
        for signum, handler in handlers.items():
            signal.signal(signum, handler)
        if result['cleanup_errors']:
            status = 1
            result['completed'] = False
        result['exit_code'] = status
        result['finished_utc'] = common.utc()
        save(run / 'result.json', result)
        (run / 'exit-code.txt').write_text(str(status) + '\n')
    return status


def clean_groups(common, processes, folder, result):
    for proc in reversed(processes):
        try:
            common.stop_owned_group(proc)
        except BaseException as error:
            result['cleanup_errors'].append('stop ' + str(proc.pid) + ': ' + repr(error))
    deadline = time.monotonic() + 6
    samples = []
    while True:
        groups = [owned_group(proc.pid) for proc in processes]
        samples.append({'monotonic': time.monotonic(), 'groups': groups})
        bad = [group for group in groups if group['errors'] or any(member['state'] != 'Z' for member in group['members'])]
        if not bad or time.monotonic() >= deadline:
            break
        time.sleep(0.2)
    save(folder / 'group-cleanup.json', {'grace_seconds': 6, 'samples': samples})
    if bad:
        result['cleanup_errors'].append('6 秒后仍有本次非 Z 组成员或扫描错误: ' + repr(bad))


if __name__ == '__main__':
    sys.exit(main())
