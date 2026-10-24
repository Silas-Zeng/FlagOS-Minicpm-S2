"""仅CPU编译CUDA源；由root显式安排，不导入Torch、不初始化设备。"""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,subprocess
HERE=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    pins=json.loads((HERE/'asset-pins.json').read_bytes())
    for name,pin in pins.items():
        if sha(HERE/name)!=pin: raise ValueError('输入源发生变化: '+name)
    build=HERE/'build';build.mkdir(exist_ok=False)
    compiler=Path('/usr/local/corex/bin/clang++')
    source=HERE/'staging.cu';obj=build/'staging.o';lib=build/'staging.so'
    commands=[
        [str(compiler),'-O3','-std=c++17','-fPIC','-x','ivcore','--cuda-gpu-arch=ivcore11',
         '--cuda-path=/usr/local/corex','-D__ILUVATAR__','-c',str(source),'-o',str(obj)],
        ['c++','-shared',str(obj),'-L/usr/local/corex/lib64','-Wl,-rpath,/usr/local/corex/lib64','-lcudart','-o',str(lib)]]
    result=dict(started_utc=datetime.now(timezone.utc).isoformat(),source_sha256=sha(source),
                builder_sha256=sha(__file__),commands=commands,library=str(lib),compiled=False,
                compiler=str(compiler.resolve()),compiler_sha256=sha(compiler))
    with (build/'build.log').open('x') as log:
        try:
            subprocess.run([str(compiler),'--version'],stdout=log,stderr=subprocess.STDOUT,check=True,timeout=10)
            for command in commands:
                subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
            subprocess.run(['ldd',str(lib)],stdout=log,stderr=subprocess.STDOUT,check=True,timeout=10)
            result.update(compiled=True,library_sha256=sha(lib))
        except BaseException as error: result['error']=repr(error)
    result['build_log_sha256']=sha(build/'build.log')
    result['finished_utc']=datetime.now(timezone.utc).isoformat()
    (build/'manifest.json').write_text(json.dumps(result,indent=2)+'\n')
    if not result['compiled']: raise RuntimeError('编译失败，保留原件；不自动改flags重试')
    print(json.dumps(result),flush=True)
if __name__=='__main__':main()
