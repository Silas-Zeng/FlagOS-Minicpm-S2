#!/usr/bin/env python3
"""通过已登录 gh 的 Git Data API 发布完整 Git tree；不读取或创建凭据。

仅允许三个已授权的私有实验仓库。源码副本保留本地上游历史，远端发布
带精确来源 commit/tree 的快照。网络中断可复用 state；只在 tree 完全吻合后
以非强制方式更新 main。原始 Git 文件模式和字节均保留。
"""
import argparse
import base64
import datetime
import hashlib
import json
from pathlib import Path
import re
import subprocess

ALLOWED = {'Silas-Zeng/FlagOS-S2-Minicpm-throughput',
           'Silas-Zeng/FlagOS-S2-vllm-plugin-FL', 'Silas-Zeng/FlagGems'}
GH = 'C:/Program Files/GitHub CLI/gh.exe'
PATTERNS = [rb'-----BEGIN (?:OPENSSH |RSA |EC |DSA |ENCRYPTED )?PRIVATE KEY-----',
            rb'\bgh[pousr]_[A-Za-z0-9]{30,}\b', rb'\bgithub_pat_[A-Za-z0-9_]{30,}\b',
            rb'\bsk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{32,}\b']


def main():
    if not __debug__:
        raise RuntimeError('发布验收需要启用断言，禁止 -O 或 PYTHONOPTIMIZE。')
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('local', type=Path)
    p.add_argument('repository', choices=sorted(ALLOWED))
    p.add_argument('--revision', default='HEAD')
    p.add_argument('--state', required=True, type=Path)
    p.add_argument('--message', required=True)
    p.add_argument('--publish', action='store_true')
    args = p.parse_args()
    args.local = args.local.resolve()
    args.state.parent.mkdir(parents=True, exist_ok=True)

    def git(*items):
        return subprocess.check_output(['git', '-c', 'safe.directory=' + args.local.as_posix(), '-C', str(args.local), *items])

    revision = git('rev-parse', args.revision).decode().strip()
    expected_tree = git('rev-parse', revision + '^{tree}').decode().strip()
    entries, objects = [], {}
    for raw in git('ls-tree', '-rz', revision).split(b'\0'):
        if not raw:
            continue
        header, name = raw.split(b'\t', 1)
        mode, kind, oid = header.decode().split()
        name = name.decode('utf-8')
        if Path(name).name in {'.env', 'credentials', 'id_rsa', 'id_ed25519'}:
            raise ValueError('疑似凭据文件：' + name)
        entry = {'path': name, 'mode': mode, 'type': kind, 'sha': oid}
        entries.append(entry)
        if kind == 'blob':
            objects.setdefault(oid, {})
    packed = subprocess.run(['git', '-c', 'safe.directory=' + args.local.as_posix(), '-C', str(args.local), 'cat-file', '--batch'],
                            input=('\n'.join(objects) + '\n').encode(), capture_output=True, check=True).stdout
    offset = 0
    for oid in objects:
            end = packed.index(b'\n', offset)
            header = packed[offset:end].decode().split()
            assert header[0] == oid and header[1] == 'blob'
            length = int(header[2])
            content = packed[end + 1:end + 1 + length]
            assert len(content) == length and packed[end + 1 + length:end + 2 + length] == b'\n'
            offset = end + 2 + length
            if any(re.search(pattern, content) for pattern in PATTERNS):
                raise ValueError('疑似凭据内容（不打印），Git blob：' + oid)
            try:
                decoded = content.decode('utf-8')
                is_text = '\x00' not in decoded
            except UnicodeDecodeError:
                is_text, decoded = False, None
            objects[oid] = {'bytes': content, 'text': decoded if is_text else None}
    plan = {'repository': args.repository, 'local_revision': revision,
            'expected_tree': expected_tree, 'files': len(entries),
            'unique_bytes': sum(len(o['bytes']) for o in objects.values()),
            'binary_blobs': sum(o['text'] is None for o in objects.values())}
    print(json.dumps(plan, ensure_ascii=False), flush=True)
    if not args.publish:
        return

    def api(method, path, body=None, allow_missing=False):
        command = [GH, 'api', '-X', method, 'repos/' + args.repository + ('/' + path if path else '')]
        if body is not None:
            request = args.state.with_suffix('.request.json')
            request.write_text(json.dumps(body, ensure_ascii=True), encoding='utf-8')
            command += ['--input', str(request)]
        response = subprocess.run(command, capture_output=True, timeout=180)
        if response.returncode:
            if allow_missing and (b'(HTTP 404)' in response.stderr or
                                  b'Git Repository is empty. (HTTP 409)' in response.stderr):
                return None
            raise RuntimeError(response.stderr.decode('utf-8', errors='replace'))
        return json.loads(response.stdout)

    metadata = api('GET', '')
    assert metadata['private'] is True and metadata['full_name'] == args.repository
    state = json.loads(args.state.read_text(encoding='utf-8')) if args.state.exists() else {
        **plan, 'created_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'blobs': {}, 'tree': None, 'next_entry': 0}
    assert all(state[key] == plan[key] for key in plan), '来源发生变化，另建 state'

    def save():
        args.state.write_text(json.dumps(state, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    head = api('GET', 'git/ref/heads/main', allow_missing=True)
    if head is None:
        seed = '# 团队代码协作\n\n完整源码同步中，实验与中文报告见 [实验记录库](https://github.com/Silas-Zeng/FlagOS-S2-Minicpm-throughput)。\n'
        api('PUT', 'contents/README.md', {'message': '初始化私有团队协作库',
                                        'content': base64.b64encode(seed.encode()).decode(), 'branch': 'main'})
        head = api('GET', 'git/ref/heads/main')
    current = head['object']['sha']
    if state.get('published_commit'):
        assert current == state['published_commit'], '发布后 main 已变化，请人工核对'
        print(json.dumps({'status': 'already_published', 'commit': current}), flush=True)
        return
    state.setdefault('parent', current)
    assert current == state['parent'], 'main 在同步期间发生变化，禁止覆盖'
    save()

    # 同一私有仓库已有的 blob 可直接复用，避免每轮重新上传全部源码副本。
    # 仍创建和核对完整目标 tree；不依赖路径相同，也不跳过最终字节/模式验收。
    parent_commit = api('GET', 'git/commits/' + state['parent'])
    parent_tree = api('GET', 'git/trees/' + parent_commit['tree']['sha'] + '?recursive=1')
    assert parent_tree.get('truncated') is False, '远端父 tree 不完整，禁止猜测已存在对象'
    existing_blobs = {entry['sha'] for entry in parent_tree['tree'] if entry['type'] == 'blob'}
    print('reuse remote blobs ' + str(len(existing_blobs & objects.keys())), flush=True)

    for oid, obj in objects.items():
        if obj['text'] is None and oid not in state['blobs'] and oid not in existing_blobs:
            blob = api('POST', 'git/blobs', {'content': base64.b64encode(obj['bytes']).decode(), 'encoding': 'base64'})
            assert blob['sha'] == oid
            state['blobs'][oid] = oid
            save()
            print('binary ' + oid[:12], flush=True)
    while state['next_entry'] < len(entries):
        start, batch, size = state['next_entry'], [], 0
        for entry in entries[start:]:
            element = dict(entry)
            obj = objects.get(entry['sha'])
            if obj is not None and obj['text'] is not None and entry['sha'] not in existing_blobs:
                element.pop('sha')
                element['content'] = obj['text']
            length = len(json.dumps(element, ensure_ascii=True))
            if batch and size + length > 2_000_000:
                break
            batch.append(element)
            size += length
        payload = {'tree': batch}
        if state['tree']:
            payload['base_tree'] = state['tree']
        response = api('POST', 'git/trees', payload)
        state.update(tree=response['sha'], next_entry=start + len(batch))
        save()
        print('tree ' + str(state['next_entry']) + '/' + str(len(entries)), flush=True)
    assert state['tree'] == expected_tree, '远端 tree 不等于本地完整 tree，禁止更新 main'
    remote_tree = api('GET', 'git/trees/' + expected_tree + '?recursive=1')
    assert remote_tree.get('truncated') is False
    actual = [{k: e[k] for k in ('path', 'mode', 'type', 'sha')} for e in remote_tree['tree'] if e['type'] != 'tree']
    assert sorted(actual, key=lambda e: e['path']) == sorted(entries, key=lambda e: e['path'])
    assert api('GET', 'git/ref/heads/main')['object']['sha'] == state['parent']
    if not state.get('commit'):
        message = args.message + '\n\n本地来源 commit: ' + revision + '\n完整 tree: ' + expected_tree + '\n'
        commit = api('POST', 'git/commits', {'message': message, 'tree': expected_tree, 'parents': [state['parent']]})
        state['commit'] = commit['sha']
        save()
    api('PATCH', 'git/refs/heads/main', {'sha': state['commit'], 'force': False})
    assert api('GET', 'git/ref/heads/main')['object']['sha'] == state['commit']
    state.update(published_commit=state['commit'], published_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                 verified_entries=len(entries), verified_tree=expected_tree)
    save()
    print(json.dumps({'status': 'published', **{key: state[key] for key in ['repository', 'published_commit',
                      'verified_tree', 'verified_entries']}}, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
