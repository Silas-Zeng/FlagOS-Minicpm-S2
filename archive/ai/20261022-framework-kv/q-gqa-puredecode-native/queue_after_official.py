"""当前官方任务结束并封存后，只接一项已审短诊断；不是设备owner。"""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import time
import traceback

ROOT = Path('/workspace/experiments/minicpm-s2')
RUN = ROOT / 'official/20261022T231746Z-q-gqa-kv-swap-official'
SEALER = ROOT / 'scripts/q-gqa-kv-official-20261022/seal_q_gqa_kv_official.py'
SEALER_SHA = 'd9a363ee14e4f5172b7df23c7e055f277ad76a1e272ee624def8e98e6dc773d8'
PINS = {
    'biv150_puredecode_native.py': '637550a0a3b850422127700d7ea6ce5983678984078f636cae079f8f7bed772b',
    'init-footer.py': '0af6919cf0343785b3b8c7607362251157f455cd4be695e954e976f36115f1fc',
    'prepare_puredecode_native.py': 'f88182a215ab66e90c5fd44b332d582084220466e1c28e082767964fb026ab10',
    'run_puredecode_native_screen.py': '4fc1ae7e9f76cf1e63b4ab2560e0059b55df5b5dccf754a2655f79531058fd6b',
    'launch_puredecode_native.sh': 'a634ea7d2861ebf997005ec7cb7756d99cb66e149e0d117b07034343cbf4cbe8',
    'base-source-sha256.json': '82514a24cebdb3ae8ce8eb1562049168fa158894364d1dd87ae4b4a724f66136',
}


def main():
    assets = Path(__file__).resolve().parent
    queue = Path(sys.argv[1]).resolve()
    assert queue.is_relative_to(ROOT / 'queues') and queue.is_dir()
    with (queue / 'started-once').open('x') as stream:
        stream.write(str(time.time()) + '\n')

    def state(phase, **fields):
        target = queue / 'state.json'
        temporary = queue / 'state.tmp'
        temporary.write_text(json.dumps(dict(phase=phase, utc_epoch=time.time(),
            official=str(RUN), **fields), ensure_ascii=False, indent=2) + '\n')
        temporary.replace(target)

    def check_assets():
        assert hashlib.sha256(SEALER.read_bytes()).hexdigest() == SEALER_SHA
        for name, pin in PINS.items():
            assert hashlib.sha256((assets / name).read_bytes()).hexdigest() == pin, name

    def invoke(command, name):
        with (queue / (name + '.stdout')).open('xb') as out, (queue / (name + '.stderr')).open('xb') as err:
            completed = subprocess.run(command, stdout=out, stderr=err)
        with (queue / (name + '.result.json')).open('x') as handle:
            json.dump({'command': command, 'exit_code': completed.returncode}, handle, indent=2)
        if completed.returncode:
            raise RuntimeError(name + ' failed: ' + str(completed.returncode))

    try:
        check_assets()
        state('waiting_official', next_action='seal_then_one_diagnostic', gpu_owner='existing_official_driver')
        deadline = time.monotonic() + 21600
        while not (RUN / 'exit-code').is_file():
            if time.monotonic() >= deadline:
                raise TimeoutError('等待当前官方任务超过6小时；不启动后继')
            time.sleep(30)
        assert (RUN / 'exit-code').read_text().strip() == '0', '官方任务未成功'
        # owner先写exit-code再返回；仅等待其退出，不重试封存或启动。
        state('waiting_official_owner_exit', owner_pid=382479)
        owner_deadline = time.monotonic() + 60
        while True:
            try:
                owner_state = Path('/proc/382479/stat').read_text().rsplit(')', 1)[1].split()[0]
            except FileNotFoundError:
                break
            if owner_state == 'Z':
                break
            if time.monotonic() >= owner_deadline:
                raise TimeoutError('官方owner在exit0后60秒仍未退出；不启动后继')
            time.sleep(1)
        check_assets()
        state('sealing_official', gpu_owner=None)
        # 原sealer核原CSV/source/DB及所有owned PID、双栈端口、设备空闲。
        invoke(['python3', str(SEALER), RUN.name], 'official-seal')
        state('launching_diagnostic', gpu_owner='next_original_native_driver')
        # 原launcher再次即时核idle，原native driver仍独占设备锁/进程/清理。
        invoke(['bash', str(assets / 'launch_puredecode_native.sh')], 'diagnostic-launch')
        receipt = (queue / 'diagnostic-launch.stdout').read_text()
        state('diagnostic_dispatched', launch_receipt=receipt,
            gpu_owner='native_driver_in_launch_receipt', no_automatic_retry=True)
    except BaseException as error:
        state('failed', error=type(error).__name__ + ': ' + str(error), traceback=traceback.format_exc(),
            no_automatic_retry=True)
        raise


if __name__ == '__main__':
    main()
