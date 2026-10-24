"""仅生成本轮封存/导入副本，精确逆回原脚本；不运行它们。"""
import difflib
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUN = '20261023T125330Z-compute-order-math4-event'
SOURCES = {
    'seal': ('scripts/remote/seal_framework_screen.py', 'eab7f787b321e2755f8f511622de440e6c15e73dbac6b280fa69e815f385dca9'),
    'import': ('tmp/import_math4_longpath.py', 'aa00fc798e22ce39c2487b59efc9cff07f7d2ceb8418fdec2a86c9e6e1c5dc24'),
}


def generate(kind, destination, changes):
    source, pin = SOURCES[kind]
    raw = (ROOT / source).read_bytes()
    if hashlib.sha256(raw).hexdigest() != pin:
        raise ValueError('冻结原脚本变化：' + source)
    original = raw.decode('utf-8')
    text = original
    for old, new in changes:
        if text.count(old) != 1:
            raise ValueError('切口不唯一：' + old[:80])
        text = text.replace(old, new, 1)
    inverse = text
    for old, new in reversed(changes):
        if inverse.count(new) != 1:
            raise ValueError('逆回切口不唯一')
        inverse = inverse.replace(new, old, 1)
    if inverse.encode('utf-8') != raw:
        raise ValueError('未精确逆回原字节')
    compile(text, destination, 'exec')
    with (HERE / destination).open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(text)
    (HERE / (destination + '.diff')).write_text(''.join(difflib.unified_diff(
        original.splitlines(keepends=True), text.splitlines(keepends=True),
        fromfile=source, tofile=destination)), encoding='utf-8')
    return dict(source=source, source_sha256=pin, destination=destination,
        sha256=hashlib.sha256((HERE / destination).read_bytes()).hexdigest(),
        edits=len(changes), inverse_exact=True, syntax_compiled=True, executed=False)


def main():
    terminal = f'''if name != {RUN!r}:raise RuntimeError('not this fixed math4 event run')
exit_code=(run/'exit-code').read_text().strip()
if exit_code not in ('0','1') or not (run/'finished-at.txt').is_file():raise RuntimeError('not terminal exit0/1')
summary_path=run/'context-16k/math4-event-load-summary.json'
summary=json.loads(summary_path.read_text(encoding='utf-8')) if summary_path.is_file() else None
if summary is not None and (type(summary) is not dict or summary.get('exit_code') != int(exit_code)):
    raise RuntimeError('owner/load exit status mismatch')
if exit_code == '0' and (summary is None or summary.get('status') != 'processes_completed_requires_report_review'):
    raise RuntimeError('exit0 lacks completed original load summary')
client_jobs=summary.get('jobs',{{}}) if summary is not None else {{}}
if type(client_jobs) is not dict or not set(client_jobs) <= {{'math4','background'}}:
    raise RuntimeError('invalid client jobs manifest')
if exit_code == '0' and (set(client_jobs) != {{'math4','background'}} or summary.get('cleanup_errors')
        or any(job.get('returncode') != 0 for job in client_jobs.values())):
    raise RuntimeError('exit0 client outcome/cleanup inconsistent')
client_pids=[]
for label,job in client_jobs.items():
    pid=job.get('pid')
    if type(pid) is not int or pid <= 0:raise RuntimeError('invalid owned client PID')
    client_pids.append(pid)
if len(set(client_pids)) != len(client_pids):raise RuntimeError('duplicate owned client PID')
load_outcome={{'summary_path':str(summary_path),'summary_present':summary is not None,
    'status':summary.get('status') if summary is not None else None,
    'exit_code':int(exit_code),'jobs':client_jobs,
    'cleanup_errors':summary.get('cleanup_errors') if summary is not None else None,
    'summary_missing_reason':None if summary is not None else 'summary_not_created; cause not inferred; preserve owner/client logs',
    'client_cleanup_proof':'known_jobs_pid_and_pgid' if client_jobs else 'unavailable_no_jobs_manifest',
    'quality_pass_claimed':False}}
'''
    groups = '''pids.update(client_pids)
client_groups={str(pid):[] for pid in client_pids}
group_scan_errors=[]
for entry in Path('/proc').iterdir():
    if not entry.name.isdecimal():continue
    try:
        # comm may contain spaces or ')'; fields after the final ')' start with state.
        fields=(entry/'stat').read_text().rsplit(')',1)[1].split()
        pgid=int(fields[2])
        if str(pgid) in client_groups:
            client_groups[str(pgid)].append({'pid':int(entry.name),'state':fields[0],'ppid':int(fields[1]),'pgid':pgid})
    except (FileNotFoundError,ProcessLookupError):
        pass
    except (OSError,ValueError,IndexError) as error:
        group_scan_errors.append({'pid':entry.name,'error':repr(error)})
'''
    checks = '''if group_scan_errors or any(member['state'] != 'Z' for members in client_groups.values() for member in members):
    raise RuntimeError('owned client process group alive or unreadable process status')
'''
    seal_changes = [
        ("if (run/'exit-code').read_text().strip()!='0':raise RuntimeError('screen did not pass')\n", terminal),
        ("processes={}\n", groups + "processes={}\n"),
        ("'source_count':len(expected),'source_failures':failures}",
         "'source_count':len(expected),'source_failures':failures,'load_outcome':load_outcome,'client_group_members':client_groups,'client_group_scan_errors':group_scan_errors}"),
        ("attention=Path('/usr/local/lib/python3.12/site-packages/vllm/v1/attention/ops/triton_unified_attention.py')\n",
         checks + "attention=Path('/usr/local/lib/python3.12/site-packages/vllm/v1/attention/ops/triton_unified_attention.py')\n"),
        ("'status':'sealed','run':str(run),'source_count':len(expected),'gpu':query",
         "'status':'evidence_sealed_not_quality_pass','run':str(run),'exit_code':int(exit_code),'load_status':load_outcome['status'],'source_count':len(expected),'gpu':query"),
    ]
    importer = (ROOT / SOURCES['import'][0]).read_text(encoding='utf-8')
    old_tail = importer[importer.index('run = parent / name\n'):]
    new_tail = f'''run = parent / name
assert name == {RUN!r}
pattern = 'context-16k/background/results/*.json'
results = sorted(run.glob(pattern))
summary_path = run/'context-16k/math4-event-load-summary.json'
summary = json.loads(summary_path.read_text(encoding='utf-8')) if summary_path.is_file() else None
print(json.dumps({{'run': name, 'sealed_files': len(actual), 'added': added,
                  'matched_existing': existing, 'exit_code': (run/'exit-code').read_text().strip(),
                  'background_result_glob': str(run/pattern),
                  'background_result_paths': [str(p.relative_to(run)) for p in results],
                  'background_results': [json.loads(p.read_text(encoding='utf-8')) for p in results],
                  'load_summary_path': str(summary_path), 'load_summary_present': summary is not None,
                  'load_summary': summary, 'result_missing_is_not_success': not bool(results)}}, ensure_ascii=False))
'''
    receipt = dict(run=RUN, device_used=False, recovery_scripts_executed=False,
        sealer=generate('seal', 'seal_math4_event.py', seal_changes),
        importer=generate('import', 'import_math4_event_longpath.py', [
            ("root = Path(__file__).resolve().parents[1]\n", "root = Path(__file__).resolve().parents[2]\n"),
            (old_tail, new_tail)]))
    (HERE / 'preparation.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(receipt, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
