"""生成447 CPU诊断收尾薄适配；不执行原件读取、封存、导入或设备命令。"""
import difflib
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(source, destination, edits):
    raw = (ROOT / source).read_bytes()
    original = text = raw.decode('utf-8')
    for old, new in edits:
        assert text.count(old) == 1, old[:120]
        text = text.replace(old, new, 1)
    inverse = text
    for old, new in reversed(edits):
        assert inverse.count(new) == 1, new[:120]
        inverse = inverse.replace(new, old, 1)
    assert inverse.encode() == raw
    compile(text, destination, 'exec')
    if (HERE / destination).exists():
        assert (HERE / destination).read_bytes() == text.encode(), '已有不同输出，拒覆盖'
    else:
        with (HERE / destination).open('x', encoding='utf-8', newline='\n') as stream:
            stream.write(text)
    (HERE / (destination + '.diff')).write_text(''.join(difflib.unified_diff(
        original.splitlines(True), text.splitlines(True), fromfile=source, tofile=destination)), encoding='utf-8')
    return dict(source=source, source_sha256=sha(ROOT / source), sha256=sha(HERE / destination),
                edits=len(edits), inverse_exact=True, syntax_compiled=True, executed=False)


def main():
    original = (ROOT / 'tmp/current-main-baseline/seal_current_main_candidate.py').read_text(encoding='utf-8')
    old_identity = original[original.index("launcher=control/'launch_compute_order_main.py'"):original.index('ports={}\n')]
    old_functions = (ROOT / 'tmp/current-main-baseline/launch_current_main_baseline.py').read_text(encoding='utf-8')
    tree_functions = old_functions[old_functions.index('def oid('):old_functions.index('def expected_tree(')]
    identity = """launcher=control/'launch_resume_cpu.py'
if sha(launcher)!='800a4fa8f2cde61d5c66fdd657dc32283fde891a9da0dfe25df2e48237faa8cb':raise RuntimeError('frozen observer owner changed')
import runpy
namespace=runpy.run_path(str(launcher))  # 仅stdlib/定义；绝不调用prepare_source/main/reference_ready。
for filename,pin in {
    'candidate-git-blobs.json':'340e2ce1254510864d2b8b8d90939a98622f70a28f10573f9a887eebface106e',
    'candidate-manifest.json':'0b17b3a18fc89a3968f409d9e340190a19ffd4e7aadec3f456293f91281f4ec4',
    'observer-manifest.json':'64e819251918ea03be2965d9ec86f6140aa0de47800f762191dfb97c18b93c21',
}.items():
    if sha(control/filename)!=pin:raise RuntimeError('frozen identity changed: '+filename)
expected_blobs=json.loads((control/'candidate-git-blobs.json').read_text())
observer=json.loads((control/'observer-manifest.json').read_text())
""" + tree_functions + """if (len(expected_blobs)!=446 or tree_oid(expected_blobs)!=namespace['TREE']
        or observer['base_tree']!=namespace['TREE'] or observer['base_count']!=446
        or set(observer['changed_paths'])!=set(namespace['OBSERVER_PINS'])):
    raise RuntimeError('not fixed446 plus two declared observer paths')
for path,entry in observer['changed_paths'].items():
    if expected_blobs.get(path)!=entry['before'] or entry['sha256']!=namespace['OBSERVER_PINS'][path]:
        raise RuntimeError('observer base blob or payload mismatch')
    expected_blobs[path]=entry['after']
    if expected.get(path)!=entry['sha256']:raise RuntimeError('observer content SHA mismatch')
if (len(expected_blobs)!=447 or tree_oid(expected_blobs)!='cd50086ea3dd618c890533bc37e6637888b6dbf5'
        or observer['target_tree']!=namespace['OBSERVER_TREE'] or observer['source_count']!=447
        or purpose['source_count']!=447 or purpose['tree']!=observer['target_tree']
        or purpose['base_tree']!=namespace['TREE'] or purpose['base_commit']!=namespace['COMMIT']):
    raise RuntimeError('447 complete tree or purpose mismatch')
archived_blobs=json.loads((control/'source-git-blobs.json').read_text())
if len(expected)!=447 or archived_blobs!=expected_blobs:
    raise RuntimeError('not complete observer Git tree')
if namespace['source_maps'](source)!=(expected_blobs,expected) or namespace['source_maps'](control/'plugin-source')!=(expected_blobs,expected):
    raise RuntimeError('live/archive complete Git blobs, modes or symlink changed')
"""
    group = """owner_pid=int((control/'runner.pid').read_text())
# 原800a Popen(start_new_session=True)，bc51的负载客户端继承该组；只检查，不发信号。
group_members=[];group_errors=[];owner_stat=None
for proc in Path('/proc').iterdir():
    if not proc.name.isdigit():continue
    try:
        raw=(proc/'stat').read_text()
        tail=raw[raw.rindex(')')+2:].split()
        pid=int(proc.name);pgrp=int(tail[2]);session=int(tail[3])
        item=dict(pid=pid,state=tail[0],ppid=int(tail[1]),pgrp=pgrp,session=session,start_ticks=int(tail[19]),stat=raw)
        if pid==owner_pid:owner_stat=item
        if pgrp==owner_pid or session==owner_pid:group_members.append(item)
    except (FileNotFoundError,ProcessLookupError):
        continue
    except (OSError,ValueError,IndexError) as error:
        group_errors.append(dict(pid=proc.name,error_type=type(error).__name__))
group=dict(owner_pid=owner_pid,expected_pgid=owner_pid,expected_session=owner_pid,
    basis='原800a start_new_session=True；原bc51客户端继承组，仅事后读取/proc',
    owner_stat=owner_stat,members=group_members,scan_errors=group_errors,
    no_signals_sent=True,limits='这是采样时的组成员检查，非全程进程追踪。')
save(run/'owner-process-group.json',group)
"""
    group_gate = """if (group_errors or any(member['state']!='Z' for member in group_members)
        or (owner_stat is not None and (owner_stat['pgrp']!=owner_pid or owner_stat['session']!=owner_pid))):
    raise RuntimeError('owner进程组/SID仍有活跃成员或检查不完整；只记录，不杀进程')
"""
    events = """events=[];malformed=[]
known={'ARMED','PREEMPT_BEFORE','RESUME_FIRST_ATTEMPT','RESUME_ADMITTED','TARGET_EXECUTE','FINAL','OBSERVATION_DISABLED','SCOPE_REJECTED'}
for line_number,line in enumerate(log.splitlines(),1):
    if 'BIV150_RESUME_CPU ' not in line:continue
    try:
        item=json.loads(line.split('BIV150_RESUME_CPU ',1)[1])
        pid=re.search(r'EngineCore[^\\s()]* pid=(\\d+)',line)
        if (not isinstance(item,dict) or not pid or item.get('pid')!=int(pid.group(1))
                or item.get('event') not in known):raise ValueError('unknown event/PID')
        events.append(dict(line_number=line_number,value=item))
    except Exception as error:
        malformed.append(dict(line_number=line_number,error_type=type(error).__name__,line=line))
counts={kind:sum(row['value']['event']==kind for row in events) for kind in sorted(known)}
save(run/'resume-cpu-events.json',dict(run_id=name,exit_code=terminal_code,events=events,counts=counts,
    malformed=malformed,final_cpu_recording_complete=[row['value'].get('cpu_recording_complete')
        for row in events if row['value']['event']=='FINAL'],
    final_present=bool(counts['FINAL']),causal_chain_reviewed=False,gain=None,
    limits=['保留FINAL/抢占/APC/execute原字段；缺覆盖、观察失败或exit1不阻封包。',
        '仅CPU提交/原方法返回，GPU完成下界未知；未计算重算GPU时间或性能收益。',
        'FINAL缺失不推定成功，后续按同PID/RID/epoch分析；不自动补跑。']))
"""
    run_guard = """RUN = None  # root取得实际run ID后可仅锁此项；当前仅接受严格UTC+固定后缀。
match=re.fullmatch(r'(\\d{8}T\\d{6}Z)-current-main-resume-cpu-context16k-long',name)
if not match or (RUN is not None and name!=RUN):raise ValueError('not this observer diagnostic run')
stamp=match.group(1)
datetime.datetime.strptime(stamp,'%Y%m%dT%H%M%SZ')
"""
    sealer = build('tmp/current-main-baseline/seal_current_main_candidate.py', 'seal_resume_cpu.py', [
        ('保留短服务原件，补齐 DB 后态、实际源码及进程清理证据。', '保留447 CPU诊断exit0/1及未覆盖原件；核源码/DB/清理，不计算性能。'),
        ("if name != '20261023T141159Z-current-main-compute-order-context16k':raise RuntimeError('not this fixed current-main compute-order run')\n", run_guard),
        ("source=Path(purpose['source'])\n", "source=Path(purpose['source'])\nif source!=ROOT/'code'/('current-main-resume-cpu-'+stamp) or source.is_symlink():raise RuntimeError('not isolated observer source')\n"),
        (old_identity, identity),
        ("re.findall(r'EngineCore pid=(\\d+)',log)", "re.findall(r'EngineCore[^\\s()]* pid=(\\d+)',log)"),
        ("post={'utc':", group + "post={'utc':"),
        ("attention=Path('/usr/local", group_gate + "attention=Path('/usr/local"),
        ("# P未命中/scope拒绝/失败只记录原日志，不阻止完整证据封存；可比性由pair reader判。\n", events),
        ("tool=control/'seal_current_main_candidate.py'", "tool=control/'seal_resume_cpu.py'"),
        ("'current-main short candidate only; no new accuracy or causal performance gain from sealing alone'", "'CPU observer diagnostic including exit1/uncovered; no accuracy or performance gain'"),
    ])
    importer = build('tmp/current-main-baseline/import_current_main_candidate.py', 'import_resume_cpu.py', [
        ('当前main短服务原件导入；唯一已审symlink材料化，原tgz及seal不变。', '447 CPU诊断原件导入；复用唯一symlink材料化与全部seal门，允许exit1/未覆盖。'),
        ('import os\n', 'import os\nimport re\nfrom datetime import datetime\n'),
        ("RUN = '20261023T141159Z-current-main-compute-order-context16k'", 'RUN = None  # root取得实际run ID后可仅锁此项。'),
        ("    assert name == RUN and (not sys.argv[5:] or controller_seal)\n", "    match = re.fullmatch(r'(\\d{8}T\\d{6}Z)-current-main-resume-cpu-context16k-long', name)\n    assert match and (RUN is None or name == RUN) and not sys.argv[5:] and not controller_seal\n    datetime.strptime(match.group(1), '%Y%m%dT%H%M%SZ')\n"),
        ('assert len(git_map) == 446', 'assert len(git_map) == 447'),
        ("pattern = 'context-16k/results/*.json'", "pattern = 'context-16k-long/results/*.json'"),
        ("    result = dict(background_result_glob=pattern, paths=[str(p.relative_to(run)) for p in result_paths],\n        results=[json.loads(p.read_text(encoding='utf-8')) for p in result_paths])\n", "    parsed_results = []\n    for path in result_paths:\n        try:\n            parsed_results.append(json.loads(path.read_text(encoding='utf-8')))\n        except (ValueError, UnicodeError) as error:\n            parsed_results.append(dict(path=str(path.relative_to(run)), parse_error=type(error).__name__,\n                note='负结果可含半写JSON；原字节已通过seal并完整保存，不推定负载成功'))\n    result = dict(background_result_glob=pattern, paths=[str(p.relative_to(run)) for p in result_paths],\n        results=parsed_results)\n"),
        ("exit_code=(run / 'exit-code').read_text().strip(), result=result)", "exit_code=(run / 'exit-code').read_text().strip(), result=result,\n        cpu_events=json.loads((run / 'resume-cpu-events.json').read_text(encoding='utf-8')),\n        owner_process_group=json.loads((run / 'owner-process-group.json').read_text(encoding='utf-8')))")
    ])
    receipt = dict(sealer=sealer, importer=importer, source_count=447,
        tree='cd50086ea3dd618c890533bc37e6637888b6dbf5', run_id_pending=True,
        original_tests_reexecuted=False, ssh_or_gpu=False, raw_read=False)
    (HERE / 'preparation.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(receipt, ensure_ascii=True, indent=2))


if __name__ == '__main__':
    main()
