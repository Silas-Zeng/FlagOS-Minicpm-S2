"""只生成142019收尾薄适配并归档；不执行判卷、封存、导入或设备命令。"""
import difflib
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVE = ROOT / 'archive/ai/20261022-framework-kv/current-main-combined-accuracy'
RUN = '20261023T142019Z-current-main-compute-order'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(source, destination, edits):
    raw = (ROOT / source).read_bytes()
    original = text = raw.decode('utf-8')
    for old, new in edits:
        assert text.count(old) == 1, old[:100]
        text = text.replace(old, new, 1)
    inverse = text
    for old, new in reversed(edits):
        assert inverse.count(new) == 1
        inverse = inverse.replace(new, old, 1)
    assert inverse.encode() == raw
    compile(text, destination, 'exec')
    with (HERE / destination).open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(text)
    (HERE / (destination + '.diff')).write_text(''.join(difflib.unified_diff(
        original.splitlines(True), text.splitlines(True), fromfile=source,
        tofile=destination)), encoding='utf-8')
    return dict(source=source, source_sha256=sha(ROOT / source), sha256=sha(HERE / destination),
                inverse_exact=True, syntax_compiled=True, executed=False, edits=len(edits))


def main():
    identity = '''    if args.run_id != '20261023T142019Z-current-main-compute-order':
        raise ValueError('仅处理固定142019准确率')
    if sha(args.reviewer) != 'ba22e1a337b8a62c7a385ae31e0a71af148cfd0a1cab8ff3b0f84e9bf36b1010':
        raise ValueError('原105题审阅器变化')
'''
    closure = '''    launcher = control / 'launch_combined_accuracy.py'
    if sha(launcher) != 'c5ec1da7e43d54f2bca1bf4da91d4b7a57119168ceb239e422b11ccde5ec036d':
        raise ValueError('已运行的准确率launcher变化')
    if (sha(control / 'candidate-git-blobs.json') != '340e2ce1254510864d2b8b8d90939a98622f70a28f10573f9a887eebface106e'
            or sha(control / 'candidate-manifest.json') != '0b17b3a18fc89a3968f409d9e340190a19ffd4e7aadec3f456293f91281f4ec4'):
        raise ValueError('冻结446源码身份变化')
    import runpy
    namespace = runpy.run_path(str(launcher))  # 仅stdlib/定义，绝不调用main/reference_ready。
    blobs, purpose = read(control / 'candidate-git-blobs.json'), read(control / 'purpose.json')
    if (source != namespace['SOURCE'] or purpose['source'] != str(source)
            or purpose['source_count'] != 446 or len(blobs) != 446
            or purpose['base_commit'] != namespace['COMMIT'] or purpose['tree'] != namespace['TREE']
            or purpose['reference_short_screen'] != namespace['REFERENCE_NAME']
            or read(control / 'source-git-blobs.json') != blobs
            or namespace['source_maps'](source) != (blobs, expected)
            or namespace['source_maps'](control / 'plugin-source') != (blobs, expected)):
        raise ValueError('固定446 live/control源码或purpose不符')
'''
    coverage = '''    import ast
    log = (run / 'server.log').read_text(errors='replace')
    selected, normalized, rejected, malformed = [], [], [], []
    for line in log.splitlines():
        pid = re.search(r'EngineCore pid=(\\d+)', line)
        for marker, destination in (
                ('BIV150_COMPUTE_ORDER_FIRST_SELECTED ', selected),
                ('BIV150_PREFILL_NORMALIZATION_SELECTED ', normalized),
                ('BIV150_COMPUTE_ORDER_SCOPE_REJECTED ', rejected)):
            if marker not in line:
                continue
            try:
                if destination is normalized:
                    value = ast.literal_eval(line.split(marker, 1)[1])
                    if not pid or not isinstance(value, tuple) or len(value) != 3 or not all(type(v) is int and v > 0 for v in value):
                        raise ValueError('normalization marker几何/PID不完整')
                    destination.append(dict(pid=int(pid.group(1)), shape=list(value)))
                    continue
                item = json.loads(line.split(marker, 1)[1])
                if not pid or not isinstance(item, dict) or item.get('pid') != int(pid.group(1)):
                    raise ValueError('marker PID不匹配')
                if destination is selected and not (item.get('original_model_forward_returned') is True
                        and item.get('runtime_mode') == 'NONE'
                        and item.get('sampler_rows') == item.get('N')
                        and 0 < item.get('Dprefix', 0) < item.get('Dall', 0)
                        and item.get('outside') == item['Dall'] - item['Dprefix']):
                    raise ValueError('P marker资格不完整')
                destination.append(item)
            except Exception as error:
                malformed.append(dict(marker=marker, error_type=type(error).__name__, line=line))
    normalized_pids = {item['pid'] for item in normalized}
    p_valid = bool(selected) and all(item['pid'] in normalized_pids for item in selected) and not (rejected or malformed)
    coverage = dict(run_id=args.run_id, source_count=446, p_first_selected=selected,
        normalization_selected=normalized, scope_rejected=rejected, malformed_markers=malformed,
        actual_p_observed=p_valid,
        p_coverage_status=('actual_P_observed' if p_valid else
            'invalid_or_rejected_marker' if selected or rejected or malformed else 'not_observed'),
        complete_105_evaluation=parsed['validity'] == 'valid' and parsed['samples'] == 105,
        accuracy_gate=parsed['accuracy_gate'],
        limitations=['FIRST_SELECTED仅首命中，不是所有题目/全程覆盖或完整答案前作用证明',
            'P日志零命中不否定原105题完整完成，但不能据此证明新P分支准确率',
            '本轮准确率不计性能；140324/141159因KV521840/521936失配，gain=null'])
    save(run / 'method-coverage.json', coverage)
'''
    sealer = build('scripts/remote/seal_completed_accuracy.py', 'seal_combined_accuracy.py', [
        ('    parent = ROOT / \'accuracy\'\n', identity + '    parent = ROOT / \'accuracy\'\n'),
        ("    outputs = [run/'postflight-full.json'", "    outputs = [run/'method-coverage.json', run/'postflight-full.json'"),
        ("    actual = {p.relative_to(source).as_posix():sha(p)", closure + "    actual = {p.relative_to(source).as_posix():sha(p)"),
        ("    save(run/'postflight-full.json',post)\n", coverage + "    save(run/'postflight-full.json',post)\n"),
        ("control/'seal_completed_accuracy.py',", "control/'seal_combined_accuracy.py',"),
        ("    with (control/'seal_completed_accuracy.py').open('xb') as stream:\n", "    with (control/'seal_combined_accuracy.py').open('xb') as stream:\n"),
    ])
    importer = build('tmp/pr15-accuracy/import_pr15_accuracy.py', 'import_combined_accuracy.py', [
        ('PR15单次准确率原件导入；唯一已审symlink材料化，原tgz及seal不变。', '当前main加P准确率原件导入；复用唯一symlink材料化与全seal门。'),
        ("RUN = '20261023T112356Z-pr15-computed-h2d'", 'RUN = ' + repr(RUN)),
        ('assert len(git_map) == 432', 'assert len(git_map) == 446'),
    ])
    receipt = dict(run=RUN, sealer=sealer, importer=importer,
        reviewer=dict(path='scripts/review_accuracy_gate.py', sha256=sha(ROOT / 'scripts/review_accuracy_gate.py'), changed=False),
        gpu_or_ssh=False, raw_read=False, sealed_or_imported=False)
    (HERE / 'recovery-preparation.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    for name in ('launch_combined_accuracy.py', 'candidate-git-blobs.json', 'candidate-manifest.json',
                 'cpu-preparation.json', 'README.md', 'prepare_recovery.py', 'seal_combined_accuracy.py',
                 'seal_combined_accuracy.py.diff', 'import_combined_accuracy.py', 'import_combined_accuracy.py.diff',
                 'recovery-preparation.json'):
        data = (HERE / name).read_bytes()
        target = ARCHIVE / name
        if target.exists():
            assert target.read_bytes() == data, '已有不同字节，拒覆盖：' + name
        else:
            with target.open('xb') as stream:
                stream.write(data)
    print(json.dumps(receipt, ensure_ascii=True, indent=2))


if __name__ == '__main__':
    main()
