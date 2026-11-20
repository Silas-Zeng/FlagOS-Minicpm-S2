"""复用原driver完整服务/清理，仅将客户端约束为两次原run_once；不是四轮成绩。"""
import hashlib,importlib.util,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
ORIGINAL=Path('/workspace/experiments/minicpm-s2/scripts/run_official_gate.py')
ORIGINAL_SHA='79119f1548b52e9fc1767ac66754272d046cb4bee8474315e9419606037ac579'
TEST_CASES='[[4096,1024,64,256]]'
def main():
    if hashlib.sha256(ORIGINAL.read_bytes()).hexdigest()!=ORIGINAL_SHA:raise ValueError('原driver变化')
    sys.path.insert(0,str(ORIGINAL.parent))
    spec=importlib.util.spec_from_file_location('unchanged_owned_driver_diagnostic',ORIGINAL)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    import diagnostic_client
    module.TEST_CASES=TEST_CASES
    original_command=module.benchmark_command
    def command():
        value=original_command()
        if value[1]!=str(diagnostic_client.BENCHMARK):raise ValueError('原benchmark命令变化')
        return [value[0],str(HERE/'diagnostic_client.py'),*value[2:]]
    module.benchmark_command=command
    module.validate_outputs=diagnostic_client.validate_outputs
    # 原main/finally逐字使用；check_benchmark_source仍核原文件SHA及RUNS=4。
    return module.main()
if __name__=='__main__':raise SystemExit(main())
