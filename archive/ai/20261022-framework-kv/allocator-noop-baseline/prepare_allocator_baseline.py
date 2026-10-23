from pathlib import Path
import hashlib, json
root=Path(__file__).resolve().parents[1]
old=root/'tmp/q-gqa-kv-swap/launch_q_gqa_kv_swap_verify0.sh'
text=old.read_text(encoding='utf-8')
assert hashlib.sha256(old.read_bytes()).hexdigest()=='f5ea8719d6d3fe50b4695a3024307bd0689763e3614a4c3a20ed3d737fa9f817'
changes=[
('test "$#" -eq 1\nvariant=$1\n[[ "$variant" == baseline || "$variant" == candidate ]]', 'test "$#" -eq 0\nvariant=baseline'),
('''case "$variant" in
  baseline)
    source_dir="$root/code/q-gqa-service-candidate-20261022T184141Z"
    reference="$root/framework/20261022T184141Z-q-gqa-service-candidate-context16k-long-control"
    marker=BIV150_Q_FRAGMENT_SERVICE_INSTALLED ;;
  candidate)
    source_dir="$root/code/q-gqa-kv-swap-20261022T213134Z"
    reference="$root/framework/20261022T213134Z-q-gqa-kv-swap-verify1-context16k-long-control"
    marker=BIV150_KV_PROTOCOL_INSTALLED ;;
esac''', '''source_dir="$root/code/q-gqa-kv-swap-20261022T213134Z"
reference="$root/framework/20261022T213134Z-q-gqa-kv-swap-verify1-context16k-long-control"
marker=BIV150_KV_PROTOCOL_INSTALLED'''),
('$stamp-q-gqa-kv-swap-verify0-$variant-context16k-long', '$stamp-allocator-noop-baseline-decode4k'),
("(control/('base-source-sha256.json' if variant=='baseline' else 'expected-source-sha256.json'))", "(control/'expected-source-sha256.json')"),
("len(expected)!=(414 if variant=='baseline' else 422)", 'len(expected)!=422'),
("QGQA414 vs累计原FULL/pitched-SAVE VERIFY0单侧；root验收VERIFY1后手动", '当前422的allocator无状态快返候选基线；原decode4k，未安装新候选'),
('--context-long-screen --seed 721201', '--decode-screen --seed 721201'),
]
for before,after in changes:
    assert text.count(before)==1, before
    text=text.replace(before,after)
out=root/'tmp/allocator-noop-baseline';out.mkdir(exist_ok=False)
p=out/'launch.sh';p.write_text(text,encoding='utf-8',newline='\n')
for name in ('base-source-sha256.json','expected-source-sha256.json'):
    (out/name).write_bytes((old.parent/name).read_bytes())
check={'original_sha256':hashlib.sha256(old.read_bytes()).hexdigest(), 'launcher_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
       'changes':len(changes),'unchanged_owner':'原bc51、DB工具、source完整锁、双栈即时idle、独立输出、nohup PID归属全部复用',
       'load':'原decode4k，4K输入/128输出/c64/64请求，seed721201；无profiler',
       'source':'原422/82514a24，未叠425或97f H2D'}
(out/'preparation.json').write_text(json.dumps(check,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(check,ensure_ascii=False))
