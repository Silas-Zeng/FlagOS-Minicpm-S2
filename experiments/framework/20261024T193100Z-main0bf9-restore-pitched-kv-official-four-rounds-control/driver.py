"""仅在原official driver ready后读取实际图；不改benchmark或新增请求。"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
ROOT=Path('/workspace/experiments/minicpm-s2')
OFFICIAL_SHA='79119f1548b52e9fc1767ac66754272d046cb4bee8474315e9419606037ac579'
COMMON_SHA='35d30dfa4fc4d583c7fc62db1f18c992a7fd6a7e54fab95749710759b5df6a54'
def load(name,path,pin):
    if hashlib.sha256(path.read_bytes()).hexdigest()!=pin:
        raise ValueError('复用源身份变化: '+str(path))
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module
    spec.loader.exec_module(module)
    return module
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('run_dir',type=Path)
    parser.add_argument('--source-dir',required=True,type=Path)
    parser.add_argument('--role',required=True,choices=('main','kv'))
    parser.add_argument('--verification-control',required=True,type=Path)
    parser.add_argument('--database',required=True,type=Path)
    args=parser.parse_args()
    pins=json.loads((HERE/'asset-pins.json').read_bytes())
    common=load('run_accuracy_gate',ROOT/'scripts/run_accuracy_gate.py',COMMON_SHA)
    official=load('unchanged_official_driver',HERE/'official-driver.source.py',OFFICIAL_SHA)
    gate=load('current_official_graph_gate',HERE/'graph_gate.py',pins['graph_gate.py'])
    ready=common.wait_ready
    def checked_ready(server,marker,run):
        ready(server,marker,run)
        gate.capture(run,args.source_dir.resolve(strict=True),args.role,
                     args.verification_control.resolve(strict=True),common.child_environment(args.source_dir))
    common.wait_ready=checked_ready
    try:
        return official.main([str(args.run_dir),'--source-dir',str(args.source_dir),
            '--require-log-marker','BIV150_KV_PROTOCOL_INSTALLED' if args.role=='kv' else 'BIV150_NATIVE_W8A8_INSTALL',
            '--database',str(args.database)])
    finally:
        common.wait_ready=ready
if __name__=='__main__':
    raise SystemExit(main())
