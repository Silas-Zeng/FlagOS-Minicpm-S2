"""仅准备固定实验PR2的本地增量计划；不联网、不改Git对象/分支、不发布。"""
import argparse
import csv
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import re

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'experiments/registry.csv').is_file())
HERE = Path(__file__).resolve().parent
BASE = 'c01f660eb57e94bfa8d438bd0fc63694380d4a31'
PARENT = '84678bde9dddd674d83eaecfb87369e3b40cc6b9'
BASE_TREE = '33c1449903832de3d3c3b7e0123881f53c679e75'
MAIN = 'f75b549a44a0f3cf35da3923766a2cc6b69ae6ee'
RUN = '20261023T144620Z-current-main-compute-order-official'


def main():
    if not __debug__:
        raise RuntimeError('禁止 -O/PYTHONOPTIMIZE')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target-local', required=True, help='root完成206/203登记、正文和交接后保存的完整40位commit')
    args = parser.parse_args()
    if not re.fullmatch('[0-9a-f]{40}', args.target_local):
        raise ValueError('必须显式固定完整commit，不接受HEAD/分支/短SHA')
    os.environ['GIT_NO_LAZY_FETCH'] = '1'
    receipt = ROOT / 'archive/github/20261023-math4-event-update.json'
    assert hashlib.sha256(receipt.read_bytes()).hexdigest() == 'e798b3fb92b026119bda36ee25a655a2097e705c6dd66c0d88a085a7cd7b1653'
    prior = json.loads(receipt.read_text(encoding='utf-8'))
    assert (prior['local_revision'], prior['published_commit'], prior['verified_tree']) == (BASE, PARENT, BASE_TREE)
    source = ROOT / 'scripts/publish_experiment_pr.py'
    assert hashlib.sha256(source.read_bytes()).hexdigest() == 'f8e8819654ab87c7772d325304a95bb3a3c8cb918eba922f5e2954c66470ef08'
    spec = importlib.util.spec_from_file_location('reviewed_publisher', source)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    target = mod.git(ROOT, 'rev-parse', args.target_local + '^{commit}').decode().strip()
    assert target == args.target_local
    mod.git(ROOT, 'merge-base', '--is-ancestor', BASE, target)
    before, after = mod.git_map(ROOT, BASE), mod.git_map(ROOT, target)
    assert mod.tree_oid(before) == BASE_TREE
    edits = [dict(path=p, after=after.get(p)) for p in sorted(set(before) | set(after)) if before.get(p) != after.get(p)]
    for row in edits:
        path, entry = row['path'], row['after']
        if entry is None:
            raise ValueError('本批不含删除；若确有必要由root单独审核：' + path)
        if entry['type'] != 'blob' or entry['mode'] not in ('100644', '100755', '120000'):
            raise ValueError('拒绝新增gitlink或未知文件模式：' + path)
        if path.startswith(('tmp/', 'collaboration/', 'recovery/', 'output/', '.ssh/', '.aws/', '.codex/')) or path.endswith(('.tgz', '.tar.gz', '.tar', '.zip', '.pack', '.bundle')):
            raise ValueError('仅发布展开原件；拒绝本轮压缩包、镜像或本地工具状态：' + path)
    rows = list(csv.DictReader(io.StringIO(mod.git(ROOT, 'show', target + ':experiments/registry.csv').decode('utf-8'))))
    assert len(rows) == 206 and len({r['run_id'] for r in rows}) == 203
    assert len([r for r in rows if r['run_id'] == RUN]) == 1
    summary = json.loads(mod.git(ROOT, 'show', target + ':analysis/compute-order-current-main-official.json'))
    assert summary['run_id'] == RUN and summary['gain'] is None
    assert summary['完成']['exit_code'] == 0 and summary['完成']['raw_rows'] == 8 and summary['完成']['summary_rows'] == 2
    assert summary['源码']['tree'] == '5c77e68caff6aa0c8b6c230adb78a2d4c293cca1'
    blobs = mod.changed_blobs(ROOT, dict(edits=edits))
    old_ids = {e['sha'] for e in before.values()}
    missing = {e['sha'] for e in after.values()} - old_ids
    tree = mod.tree_oid(after)
    assert mod.git(ROOT, 'rev-parse', target + '^{tree}').decode().strip() == tree
    plan = dict(repository='Silas-Zeng/FlagOS-Minicpm-S2', repository_id=1427279927, pr_number=2,
                pr_url='https://github.com/Silas-Zeng/FlagOS-Minicpm-S2/pull/2', branch='codex/framework-experiments-20261022',
                local_base=BASE, local_target=target, parent=PARENT, remote_parent_tree=BASE_TREE,
                verified_tree=tree, main_unchanged=MAIN, private=True, registry_rows=206, unique_runs=203,
                changed_paths=len(edits), scanned_blobs=len(blobs), new_unique_blobs=len(missing),
                new_unique_bytes=sum(len(blobs[oid]) for oid in missing),
                status='prepared_locally_no_remote_write')
    (HERE / 'publish-plan.json').write_text(json.dumps(plan, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (HERE / 'commit.request.json').write_text(json.dumps(dict(message='补充当前main计算顺序组合的准确率与完整官方结果', tree=tree, parents=[PARENT]), ensure_ascii=False), encoding='utf-8')
    body = (HERE / 'body.md').read_text(encoding='utf-8')
    (HERE / 'body.request.json').write_text(json.dumps(dict(body=body), ensure_ascii=False), encoding='utf-8')
    print(json.dumps(plan, ensure_ascii=False))


if __name__ == '__main__':
    main()
