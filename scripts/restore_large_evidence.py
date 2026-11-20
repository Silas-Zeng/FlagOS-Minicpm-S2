"""从 *.storage.json 还原大原件；逐块及整体核 SHA256，不覆盖已有不同文件。"""
import argparse,contextlib,gzip,hashlib,json,tempfile
from pathlib import Path

def file_sha(path):
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):h.update(block)
    return h.hexdigest()

@contextlib.contextmanager
def gzip_input(root,item):
    compressed=(root/item['compressed_path']).resolve()
    assert compressed.is_relative_to(root)
    if not item.get('gzip_parts'):
        assert compressed.stat().st_size==item['compressed_bytes'] and file_sha(compressed)==item['compressed_sha256']
        yield compressed
        return
    temporary=None
    try:
        with tempfile.NamedTemporaryFile(delete=False) as output:
            temporary=Path(output.name);h=hashlib.sha256();size=0
            for part in item['gzip_parts']:
                path=(root/part['path']).resolve();assert path.is_relative_to(root)
                block=path.read_bytes()
                assert len(block)==part['bytes'] and hashlib.sha256(block).hexdigest()==part['sha256']
                output.write(block);h.update(block);size+=len(block)
        assert size==item['compressed_bytes'] and h.hexdigest()==item['compressed_sha256'],'gzip分块拼接SHA不符'
        yield temporary
    finally:
        if temporary is not None:temporary.unlink()

def restore_gzip(root,record):
    for item in record['files']:
        target=(root/item['original_path']).resolve()
        assert target.is_relative_to(root)
        if target.exists():
            with gzip_input(root,item):pass
            assert target.stat().st_size==item['original_bytes'] and file_sha(target)==item['original_sha256'],'已有文件不同，拒绝覆盖'
            print(target)
            continue
        temporary=None
        try:
            with tempfile.NamedTemporaryFile(dir=target.parent,delete=False) as output:
                temporary=Path(output.name);h=hashlib.sha256();size=0
                with gzip_input(root,item) as compressed:
                    with gzip.open(compressed,'rb') as stream:
                        for block in iter(lambda:stream.read(1024*1024),b''):
                            output.write(block);h.update(block);size+=len(block)
            assert size==item['original_bytes'] and h.hexdigest()==item['original_sha256'],'gzip还原SHA不符'
            assert not target.exists(),'目标在还原期间出现，拒绝覆盖'
            temporary.replace(target);temporary=None
            print(target)
        finally:
            if temporary is not None:temporary.unlink()

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest',type=Path)
    args=parser.parse_args()
    root=Path(__file__).resolve().parent.parent
    record=json.loads(args.manifest.read_bytes())
    if record['format']=='gzip-sha256-v1':
        restore_gzip(root,record)
        return
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
