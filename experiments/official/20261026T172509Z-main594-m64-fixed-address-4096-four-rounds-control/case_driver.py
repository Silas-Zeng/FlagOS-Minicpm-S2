"""只用官方--test-cases分别选4K或16K；服务、benchmark、验证函数不改。"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
ORIGINAL=Path('/workspace/experiments/minicpm-s2/scripts/run_official_gate.py')
ORIGINAL_SHA='79119f1548b52e9fc1767ac66754272d046cb4bee8474315e9419606037ac579'
def main():
    parser=argparse.ArgumentParser(add_help=False)
    parser.add_argument('--prefill',type=int,choices=(4096,16384),required=True)
    args,remaining=parser.parse_known_args()
    if hashlib.sha256(ORIGINAL.read_bytes()).hexdigest()!=ORIGINAL_SHA:raise ValueError('原官方driver变化')
    sys.path.insert(0,str(ORIGINAL.parent))
    spec=importlib.util.spec_from_file_location('unchanged_official_split_case',ORIGINAL)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    module.TEST_CASES=json.dumps([[args.prefill,1024,64,256 if args.prefill==4096 else 128]],separators=(',',':'))
    return module.main(remaining)
if __name__=='__main__':raise SystemExit(main())
