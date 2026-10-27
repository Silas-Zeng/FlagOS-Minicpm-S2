"""仅后置读取PR59安装回执和本轮已绑定compiled artifact，不执行模型。"""
import ast
import base64
import hashlib
import io
import json
from pathlib import Path
import pickletools
import re
import zipfile
import zlib

LINEAR_SHA='d431a4fa144ed67dc3deab46dd5beace3612858075f85c39e602447ba3bf768a'
LIBENTRY_SHA='414e8a3f74e2522e40659e7fccd84e301f4517220837a87af0311f050bbf3025'

class _ByteReader:
    def __init__(self,data):
        if len(data)<4 or int.from_bytes(data[:4],'big')!=(zlib.crc32(data[4:])&0xffffffff):
            raise ValueError('CacheCompiledArtifact CRC32不符')
        self.data=data[4:];self.position=0
    def u64(self):
        if self.position+8>len(self.data):raise ValueError('CacheCompiledArtifact整数不完整')
        value=int.from_bytes(self.data[self.position:self.position+8],'big');self.position+=8;return value
    def bytes(self):
        count=self.u64()
        if count>len(self.data)-self.position:raise ValueError('CacheCompiledArtifact字段越界')
        value=self.data[self.position:self.position+count];self.position+=count;return value
    def string(self):return base64.b64decode(self.bytes(),validate=True).decode('utf-8')
    def remaining(self):return len(self.data)-self.position

def cache_artifacts(data):
    """PyTorch已核v1封装；仅crc/长度/base64拆包，不反序列化对象。"""
    header=b'CacheCompiledArtifact'
    if data[12:12+len(header)]!=header:return
    outer=_ByteReader(data)
    if outer.bytes()!=header:raise ValueError('CacheCompiledArtifact头不符')
    outer.bytes()  # torch_key只保留原始字节，不执行其内容。
    cache_key=outer.string();inner_data=outer.bytes()
    if outer.remaining():raise ValueError('CacheCompiledArtifact外层尾部多余字段')
    inner=_ByteReader(inner_data);version=inner.u64()
    if version!=1:raise ValueError('未核CacheCompiledArtifact encoding version: '+str(version))
    while inner.remaining():
        kind=inner.string();count=inner.u64()
        if count>inner.remaining()//16:raise ValueError('CacheCompiledArtifact条目数越界')
        for _ in range(count):
            key=inner.string();content=inner.bytes()
            yield 'cachecompiled-v1/'+cache_key+'/'+kind+'/'+key,content

def artifact_sources(data):
    """只读已绑定artifact中的源码字符串；禁止unpickle/import/运行其中代码。"""
    for prefix,content in cache_artifacts(data):
        for member,source in artifact_sources(content):yield prefix+'/'+member,source
    try:
        yield 'utf8',data.decode('utf-8')
    except UnicodeDecodeError:
        pass
    stream=io.BytesIO(data)
    if zipfile.is_zipfile(stream):
        with zipfile.ZipFile(stream) as archive:
            for name in archive.namelist():
                if name.endswith('.py'):
                    yield name,archive.read(name).decode('utf-8')
    try:
        for op,arg,pos in pickletools.genops(data):
            if isinstance(arg,str) and 'biv150_small_linear_out' in arg:
                yield 'pickle-string-'+str(pos),arg
    except (ValueError,UnicodeDecodeError):
        pass

def capture(run,graph):
    text=re.sub(r'\x1b\[[0-9;]*m','',(run/'server.log').read_text(errors='replace'))
    records=[];errors=[]
    marker='BIV150_SMALL_OUT_LOWERING_INSTALL '
    for number,line in enumerate(text.splitlines(),1):
        if marker not in line:continue
        try:
            item=ast.literal_eval(line.split(marker,1)[1])
            if not isinstance(item,dict):raise ValueError('回执不是dict')
            provenance=item.get('provider_provenance') or {}
            valid=(item.get('installed') is True and item.get('large_linear') is True
                and provenance.get('linear_sha256')==LINEAR_SHA
                and provenance.get('libentry_sha256')==LIBENTRY_SHA
                and provenance.get('bias') is False and provenance.get('group_m')==8
                and provenance.get('split_k')==1 and provenance.get('sdk_mutated') is False)
            records.append(dict(line=number,value=item,valid=valid))
        except (ValueError,SyntaxError) as error:
            errors.append(dict(line=number,error=repr(error)))
    generated=[]
    for handle in graph['compiled_handles']:
        path=Path(handle['graph_handle'][1]);data=path.read_bytes()
        for member,source in artifact_sources(data):
            if 'biv150_small_linear_out' not in source:continue
            try:tree=ast.parse(source)
            except SyntaxError:continue
            count=sum(isinstance(node,ast.Call) and ast.unparse(node.func)=='extern_kernels.biv150_small_linear_out' for node in ast.walk(tree))
            if count:
                generated.append(dict(artifact=str(path),artifact_sha256=hashlib.sha256(data).hexdigest(),member=member,
                    source_sha256=hashlib.sha256(source.encode()).hexdigest(),out_calls=count))
                target=run/'model-path'/'provider-generated';target.mkdir(exist_ok=True)
                (target/(hashlib.sha256(source.encode()).hexdigest()+'.py')).write_text(source,encoding='utf-8')
    installed=bool(records) and all(item['valid'] for item in records) and not errors
    result=dict(valid=bool(installed and generated),installed_valid=installed,records=records,parse_errors=errors,
        generated_out_modules=generated,
        limitation='只证明本轮绑定artifact内真实out callback和安装SDK身份；不把M64 provider日志缺失解释成未执行，也不声称逐step调用计数。缺可读artifact源码标资格未完整，不修改成绩或放宽门。')
    (run/'model-path/provider-evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return result
