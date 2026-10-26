"""从 *.storage.json 还原大原件；逐块及整体核 SHA256，不覆盖已有不同文件。"""
import argparse,hashlib,json
from pathlib import Path

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest',type=Path)
    args=parser.parse_args()
    root=Path(__file__).resolve().parent.parent
    record=json.loads(args.manifest.read_bytes())
    assert record['format']=='sha256-chunks-v1'
    target=(root/record['original_path']).resolve()
    assert target.is_relative_to(root)
    data=bytearray()
    for part in record['parts']:
        path=(root/part['path']).resolve()
        assert path.is_relative_to(root)
        block=path.read_bytes()
        assert len(block)==part['bytes'] and hashlib.sha256(block).hexdigest()==part['sha256']
        data.extend(block)
    assert len(data)==record['original_bytes'] and hashlib.sha256(data).hexdigest()==record['original_sha256']
    if target.exists():assert target.read_bytes()==data,'已有文件不同，拒绝覆盖'
    else:target.write_bytes(data)
    print(target)

if __name__=='__main__':main()
