"""538 VERIFY0多事务staging提交几何；调用前仍须原c147事务验收。"""
import hashlib
import importlib.util
import json
from pathlib import Path

VERIFIER_SHA = '30af9dca6f71f8b8393d2357416210a0ba0ea16651506f8371f781b525e07044'

def require(ok, message):
    if not ok:
        raise ValueError(message)

def validate(run, control):
    run, control = Path(run), Path(control)
    verifier = Path(__file__).with_name('staging_verify1.py')
    require(not verifier.is_symlink() and hashlib.sha256(verifier.read_bytes()).hexdigest() == VERIFIER_SHA,
            'staging VERIFY1原后验身份变化')
    spec = importlib.util.spec_from_file_location('staging_geometry_verifier', verifier)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    sources = json.loads((control/'source-sha256.json').read_bytes())
    rows = []
    for number, line in enumerate((run/'server.log').read_text(encoding='utf-8').splitlines(), 1):
        if 'BIV150_KV_PROTOCOL ' not in line:
            continue
        event = json.loads(line.split('BIV150_KV_PROTOCOL ', 1)[1])
        if event['event'] != 'RPC_ACK' or event['command']['kind'] not in ('SAVE','RESTORE_FULL'):
            continue
        command, reply = event['command'], event['worker_response']
        direction = 'save' if command['kind'] == 'SAVE' else 'restore'
        ids = command['pages']; pages = len(ids); nbytes = pages*16384*42
        require(pages > 0 and len(set(ids)) == pages and all(type(x) is int and x > 0 for x in ids)
                and (direction == 'save' or ids == sorted(ids)), 'staging源逻辑页/目的私有页合同不符')
        require(command['prefix_tokens'] == pages*16 and command['nbytes'] == nbytes
                and reply.get('successful') is True and reply.get('completed') is True
                and reply.get('error') is None
                and reply['transferred_bytes'] == nbytes
                and all(reply.get(k) == command[k] for k in ('kind','key','operation_serial','pages','prefix_tokens','nbytes')),
                'staging完成ACK映射/完整字节不符')
        forbidden = [k for k in reply if k.startswith('verification_')
                     or (k.startswith('save_verification_') and k != 'save_verification_performed')
                     or 'readback' in k]
        require(not forbidden and reply.get('diagnostic_verify_requested') is False
                and type(reply.get('diagnostic_extra_pinned_bytes')) is int
                and reply['diagnostic_extra_pinned_bytes'] == 0
                and (direction != 'save' or reply.get('save_verification_performed') is False),
                'VERIFY0存在回读或额外诊断buffer')
        geometry = module._verify_staging_submission(control, sources, reply,
                                                      {'pages':pages,'nbytes':nbytes}, direction)
        rows.append(dict(line=number,pid=event['pid'],key=command['key'],direction=direction,
                         pages=pages,nbytes=nbytes,geometry=geometry))
    full = sum(r['direction']=='restore' for r in rows)
    return dict(valid=True,full_count=full,save_count=len(rows)-full,has_full_coverage=bool(full),
                transactions=rows,total_copy_calls=sum(r['geometry']['copy_calls'] for r in rows),
                total_kernels=sum(r['geometry']['kernels'] for r in rows),
                total_bytes=sum(r['nbytes'] for r in rows),
                total_index_bytes=sum(r['geometry']['index_bytes'] for r in rows),gain_calculated=False,
                limits=['须先通过原c147事务验收，并由owner核full_count等于complete_logged_chains。',
                        '零事务合法但没有方法覆盖；VERIFY0不新增字节回读，不能从调用数推收益。',
                        'staging_temporary_released只断言完成后引用释放，不证明allocator reserved归还。'])
