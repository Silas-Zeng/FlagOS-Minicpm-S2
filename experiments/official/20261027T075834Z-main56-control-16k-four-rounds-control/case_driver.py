"""只用官方--test-cases选择独立16K负载，原driver函数和benchmark不改。"""
import hashlib
import importlib.util
import sys
from pathlib import Path
ORIGINAL=Path('/workspace/experiments/minicpm-s2/scripts/run_official_gate.py')
ORIGINAL_SHA='79119f1548b52e9fc1767ac66754272d046cb4bee8474315e9419606037ac579'
TEST_CASES='[[16384,1024,64,128]]'
def main():
    if hashlib.sha256(ORIGINAL.read_bytes()).hexdigest()!=ORIGINAL_SHA:raise ValueError('原官方driver变化')
    sys.path.insert(0,str(ORIGINAL.parent))
    spec=importlib.util.spec_from_file_location('unchanged_official_single_case',ORIGINAL)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    module.TEST_CASES=TEST_CASES
    return module.main()
if __name__=='__main__':raise SystemExit(main())
