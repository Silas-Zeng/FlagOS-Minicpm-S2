"""原607d导入器只运行一次，直接保留其stdout字节与退出码，防工具输出截断。"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'experiments/registry.csv').is_file() and (p/'AGENTS.md').is_file())
RUN='20261023T144620Z-current-main-compute-order-official'

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive_bytes',type=int)
    parser.add_argument('archive_sha256')
    parser.add_argument('sealed_files',type=int)
    parser.add_argument('--receipt',type=Path,required=True)
    args=parser.parse_args()
    if args.archive_bytes<=0 or args.sealed_files<=0 or not re.fullmatch('[0-9a-f]{64}',args.archive_sha256):
        raise ValueError('需要实际封存输出的size/SHA/count')
    receipt=args.receipt if args.receipt.is_absolute() else ROOT/args.receipt
    exit_path=Path(str(receipt)+'.exit-code')
    error_path=Path(str(receipt)+'.stderr.log')
    if any(p.exists() for p in (receipt,exit_path,error_path)):
        raise FileExistsError('保留已有导入回执；不自动重跑或覆盖')
    if not receipt.parent.is_dir():raise FileNotFoundError(receipt.parent)
    if hashlib.sha256((HERE/'import_combined_official.py').read_bytes()).hexdigest()!='607d1e211d2c56b4eca6bb9996c7f498aca43aefd0ecc45214ee825f609cb619':
        raise ValueError('原607d导入器字节变化')
    command=[sys.executable,'-B','-X','utf8',str(HERE/'import_combined_official.py'),RUN,
        str(args.archive_bytes),args.archive_sha256,str(args.sealed_files)]
    with receipt.open('xb') as stream:
        result=subprocess.run(command,cwd=ROOT,stdout=stream,stderr=subprocess.PIPE)
    with exit_path.open('x',encoding='ascii') as stream:stream.write(str(result.returncode)+'\n')
    if result.stderr:
        with error_path.open('xb') as stream:stream.write(result.stderr)
    if result.returncode:
        print(json.dumps(dict(status='import_failed_preserved',returncode=result.returncode,receipt=str(receipt))))
        raise SystemExit(result.returncode)
    value=json.loads(receipt.read_text(encoding='utf-8'))
    print(json.dumps(dict(status='imported',run=value['run'],sealed_files=value['sealed_files'],
        added=value['added'],matched_existing=value['matched_existing'],receipt=str(receipt)),ensure_ascii=False))

if __name__=='__main__':main()
