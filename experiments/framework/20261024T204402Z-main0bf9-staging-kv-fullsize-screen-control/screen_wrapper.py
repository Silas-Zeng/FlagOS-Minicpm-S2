"""原782两轮driver的ready只读图门；不改原测量/请求/服务参数。"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = Path('/workspace/experiments/minicpm-s2')
DRIVER_SHA = '7828274129777a5d2fd98bdff082752e2a0c1a3fc8a63c09472646b9c97e6d26'
COMMON_SHA = '35d30dfa4fc4d583c7fc62db1f18c992a7fd6a7e54fab95749710759b5df6a54'

def load(name, path, pin):
    if path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest() != pin:
        raise ValueError('复用源身份变化: ' + str(path))
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('run_dir', type=Path)
    parser.add_argument('--source-dir', type=Path, required=True)
    parser.add_argument('--role', choices=('kv',), required=True)
    parser.add_argument('--verification-control', type=Path, required=True)
    parser.add_argument('--database', type=Path, required=True)
    args = parser.parse_args()
    if args.database != Path('/root/.flaggems/config_cache/TunedConfig_iluvatar_triton_3_6.db'):
        raise ValueError('共同DB路径不同')
    pins = json.loads((HERE/'asset-pins.json').read_bytes())
    common = load('screen_owned_common', ROOT/'scripts/run_accuracy_gate.py', COMMON_SHA)
    driver = load('unchanged_two_round_driver', HERE/'driver.py', DRIVER_SHA)
    gate = load('screen_actual_graph_gate', HERE/'graph_gate.py', pins['graph_gate.py'])
    original_load, original_ready = driver.load, common.wait_ready
    def shared_common(path, pin, name):
        if path == driver.COMMON and pin == COMMON_SHA:
            return common
        return original_load(path, pin, name)
    def checked_ready(server, marker, run):
        original_ready(server, marker, run)
        gate.capture(run, args.source_dir.resolve(strict=True), args.role,
                     args.verification_control.resolve(strict=True), common.child_environment(args.source_dir))
    driver.load, common.wait_ready = shared_common, checked_ready
    try:
        return driver.main([str(args.run_dir), '--source-dir', str(args.source_dir), '--role', args.role])
    finally:
        driver.load, common.wait_ready = original_load, original_ready

if __name__ == '__main__':
    raise SystemExit(main())
