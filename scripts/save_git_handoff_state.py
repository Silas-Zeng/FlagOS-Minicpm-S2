#!/usr/bin/env python3
"""保存本地 Git 身份、index 和 diff，不修改 refs 或 index。

Git bundle 单独制作并与状态快照一起保存。最终工作树字节（含未跟踪及被忽略
文件）由完整工作 ZIP 保存。本脚本不保存 Git config 或凭据，不访问远端。
"""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'recovery/git'
REPOS = {
    'experiment': ROOT,
    'plugin-base': ROOT / 'tmp/src/vllm-plugin-FL',
    'flaggems-team': ROOT / 'collaboration/FlagGems',
    'plugin-team': ROOT / 'collaboration/FlagOS-S2-vllm-plugin-FL',
}


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, GIT_OPTIONAL_LOCKS='0')
    manifest = {'captured_utc': datetime.now(timezone.utc).isoformat(),
                'note': '最终文件字节保存在工作 ZIP 中；不保存 .git/config。',
                'repositories': {}, 'bundles': {}}
    commands = {
        'head.txt': ['rev-parse', 'HEAD'],
        'head-tree.txt': ['rev-parse', 'HEAD^{tree}'],
        'refs.txt': ['show-ref', '--head'],
        'shallow.txt': ['rev-parse', '--is-shallow-repository'],
        'reachable-commits.txt': ['rev-list', '--all', '--count'],
        'status.txt': ['status', '--porcelain=v1', '--untracked-files=all'],
        'index-stage.z': ['ls-files', '--stage', '-z'],
        'unstaged.patch': ['diff', '--binary', '--full-index', '--no-ext-diff'],
        'staged.patch': ['diff', '--cached', '--binary', '--full-index', '--no-ext-diff'],
    }
    for name, repo in REPOS.items():
        # 只信任本次明确列出的仓库，避免不同 sandbox 身份导致 dubious ownership。
        # 使用进程内配置，不写全局 config，也不使用 safe.directory=*。
        git = ['git', '-c', 'safe.directory=' + repo.resolve().as_posix(),
               '-C', str(repo)]
        saved = {}
        for suffix, arguments in commands.items():
            result = subprocess.run([*git, *arguments], env=env,
                                    capture_output=True, check=True)
            path = OUTPUT / (name + '-' + suffix)
            path.write_bytes(result.stdout)
            saved[path.name] = {'bytes': len(result.stdout),
                                'sha256': hashlib.sha256(result.stdout).hexdigest()}
        result = subprocess.run([*git, 'rev-parse', '--path-format=absolute',
                                 '--git-path', 'shallow'], env=env,
                                capture_output=True, check=True)
        shallow = Path(os.fsdecode(result.stdout.strip()))
        if shallow.is_file():
            path = OUTPUT / (name + '-shallow-boundary.txt')
            path.write_bytes(shallow.read_bytes())
            saved[path.name] = {'bytes': path.stat().st_size,
                                'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
        manifest['repositories'][name] = {'path': repo.relative_to(ROOT).as_posix(), 'files': saved}
    for path in sorted(OUTPUT.glob('*.bundle')):
        with path.open('rb') as source:
            digest = hashlib.file_digest(source, 'sha256').hexdigest()
        manifest['bundles'][path.name] = {'bytes': path.stat().st_size, 'sha256': digest}
    path = OUTPUT / 'git-state-manifest.json'
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'manifest': str(path), 'bundles': manifest['bundles']}, indent=2))


if __name__ == '__main__':
    main()
