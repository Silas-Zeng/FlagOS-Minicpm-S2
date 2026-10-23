"""仅读已导入的固定短服务原件；不是性能pair或新准确率。"""
import hashlib
import json
from pathlib import Path
import re

HERE=Path(__file__).resolve().parent
RUN='20261023T140324Z-current-main-baseline-context16k'


def main():
    roots=[p for p in HERE.parents if (p/'experiments/registry.csv').is_file() and (p/'AGENTS.md').is_file()]
    if len(roots)!=1:raise ValueError('非唯一项目根')
    root=roots[0];run=root/'experiments/framework'/RUN;control=run.with_name(RUN+'-control')
    purpose=json.loads((control/'purpose.json').read_text(encoding='utf-8'))
    post=json.loads((run/'postflight-full.json').read_text(encoding='utf-8'))
    paths=sorted((run/'context-16k/results').glob('*.json'))
    results=[json.loads(path.read_text(encoding='utf-8')) for path in paths]
    log=(run/'server.log').read_text(encoding='utf-8',errors='replace')
    database={}
    for label in ('before','after'):
        value=json.loads((control/('db-'+label)/'manifest.json').read_text(encoding='utf-8'))
        database[label]={key:value[key] for key in ('table_count','row_count','schema_sha256','logical_content_sha256','snapshot_sha256')}
    summary=dict(run_id=RUN,kind='当前main短服务基线；非新准确率/性能pair',exit_code=(run/'exit-code').read_text().strip(),
        commit=purpose['commit'],tree=purpose['tree'],source_count=post['source_count'],
        normalization_markers=[line for line in log.splitlines() if 'BIV150_PREFILL_NORMALIZATION_' in line],
        kv_capacity_tokens=re.findall(r'GPU KV cache size: ([\d,]+) tokens',log),
        result_paths=[str(path.relative_to(root)) for path in paths],results=results,database=database,
        postflight=post,accuracy_reused='PR16既有完整105题102/105及原官方4K/16K；本轮未重跑',
        limits=['安装/selected日志不证明每层或全程覆盖','仅提供后续对照基线，不自行计算或宣称收益'])
    output=HERE/'140324-summary.json'
    with output.open('x',encoding='utf-8') as stream:json.dump(summary,stream,ensure_ascii=False,indent=2);stream.write('\n')
    print(json.dumps({'summary':str(output),'sha256':hashlib.sha256(output.read_bytes()).hexdigest()},ensure_ascii=False))


if __name__=='__main__':main()
