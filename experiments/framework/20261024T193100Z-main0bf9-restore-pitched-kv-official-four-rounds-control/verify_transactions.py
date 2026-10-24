"""完整规模 VERIFY0 多事务日志后验；独立于性能结果和完整准确率。"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

SOURCE_NAME = 'summarize_official_transactions.source.py'
SOURCE_SHA256 = 'e91e2e02314ffe06dc0749263a655763401543ab7be9cc05c5ae8328a3db759f'
SOURCE_ORIGIN = 'tmp/q-gqa-kv-official/summarize_official_transactions.py'


def original_checker():
    path = Path(__file__).with_name(SOURCE_NAME)
    if hashlib.sha256(path.read_bytes()).hexdigest() != SOURCE_SHA256:
        raise ValueError('原多事务检查器变化')
    spec = importlib.util.spec_from_file_location('original_multi_key_checker', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify_log(path, run_id):
    """复用原严格 FULL 链；没有事务可合法通过日志门，但没有方法覆盖。"""
    path = Path(path)
    if not run_id or Path(run_id).name != run_id:
        raise ValueError('run_id 必须是实际运行目录名')
    result = original_checker().summarize(path)
    result['run_id'] = run_id
    result['checker_source'] = dict(path=SOURCE_ORIGIN, preserved_file=SOURCE_NAME,
                                    sha256=SOURCE_SHA256)
    result['log_path'] = str(path)
    extra_errors, eligible = [], []
    rpc_count = 0
    for line, text in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
        if 'BIV150_KV_PROTOCOL ' not in text:
            continue
        try:
            event = json.loads(text.split('BIV150_KV_PROTOCOL ', 1)[1])
            if event['event'] == 'FIRST_CHECKED':
                eligible.append(event.get('eligible') is True)
            if event['event'] != 'RPC_ACK':
                continue
            rpc_count += 1
            reply, stage = event['worker_response'], event['command']['kind']
            forbidden = [k for k in reply if k.startswith('verification_')
                         or (k.startswith('save_verification_') and k != 'save_verification_performed')
                         or 'readback' in k]
            if forbidden:
                raise ValueError('VERIFY0 不得带回读字段: ' + ','.join(sorted(forbidden)))
            if stage != 'DROP':
                if (reply.get('diagnostic_verify_requested') is not False
                        or type(reply.get('diagnostic_extra_pinned_bytes')) is not int
                        or reply['diagnostic_extra_pinned_bytes'] != 0):
                    raise ValueError('VERIFY0 诊断开关或额外 pinned 字节不符')
            elif ('diagnostic_verify_requested' in reply and reply['diagnostic_verify_requested'] is not False
                    or 'diagnostic_extra_pinned_bytes' in reply and reply['diagnostic_extra_pinned_bytes'] != 0):
                raise ValueError('DROP 带有诊断或额外 pinned 字节')
            if stage == 'SAVE' and reply.get('save_verification_performed') is not False:
                raise ValueError('VERIFY0 SAVE 必须明确未执行源字节回读')
        except (KeyError, TypeError, ValueError) as error:
            extra_errors.append(dict(line=line, reason=str(error)))
    eligible_ok = bool(eligible) and all(eligible)
    if not eligible_ok:
        extra_errors.append(dict(line=None, reason='缺少成功 FIRST_CHECKED 或出现不适用作用域'))
    no_transactions = (result['independent_key_count'] == 0 and rpc_count == 0
                       and result['counter_totals_match_key_count']
                       and not result['unresolved_slots'] and not result['errors'])
    logged_ok = bool(result['passed_logged_chain_checks'] or no_transactions)
    result.update(verify0_errors=extra_errors, verify0_rpc_count=rpc_count,
                  eligible_scope_observed=eligible_ok,
                  no_transactions_observed=no_transactions,
                  has_full_coverage=result['complete_logged_chains'] > 0,
                  passed_verify0_checks=logged_ok and not extra_errors)
    result['method_coverage'] = ('full_chain_observed' if result['has_full_coverage']
                                 else 'not_observed')
    result['qualified_method_coverage'] = result['passed_verify0_checks'] and result['has_full_coverage']
    result['limits'] = [
        '原检查器的多 Key、跨 slot serial、42 层 FULL/ACK/consumer/host 释放门原样复用。',
        '无事务可为正常负载，不能宣称 SAVE/FULL 收益；两个档位共用日志时以整次服务至少一条完整 FULL 链作为方法覆盖。',
        'SAVE 后安全放弃等非 FULL 结局沿用原检查器记为不完整链，保留原件并单独解释，不自动当作错误数据或重跑理由。',
        'VERIFY0 无新的字节回读；本实例资格见 20261024T122225Z-pr24-kv-swap-v1-verify1-context16k-long。',
        '本后验不替代源码/DB/进程清理、性能可比性或完整准确率；安装身份不证明每请求 native 路径执行。']
    return result


def verify_run(run_dir, control=None):
    run_dir = Path(run_dir)
    control = Path(control) if control is not None else run_dir.with_name(run_dir.name + '-control')
    result = verify_log(run_dir / 'server.log', run_dir.name)
    path = control / 'environment-overrides.json'
    env = json.loads(path.read_text(encoding='utf-8'))
    valid = (env.get('BIV150_KV_VERIFY_RESTORE') == '0'
             and 'BIV150_FINITE_GROWTH_ADMISSION' not in env)
    result['environment_verify0'] = dict(path=str(path), valid=valid,
        sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    result['passed_verify0_checks'] = result['passed_verify0_checks'] and valid
    result['qualified_method_coverage'] = result['passed_verify0_checks'] and result['has_full_coverage']
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-dir', type=Path, required=True)
    parser.add_argument('--control', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = verify_run(args.run_dir, args.control)
    with args.output.open('x', encoding='utf-8') as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    raise SystemExit(0 if result['passed_verify0_checks'] else 1)
