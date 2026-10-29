from __future__ import annotations
import csv, hashlib, importlib.util, io, json, subprocess, sys
from pathlib import Path

HERE=Path(__file__).resolve()
REPO=HERE.parents[1]
ROOT=REPO.parents[1]
ARCHIVE=ROOT/'archive/prefill-i32-offset-20261029'
EXPECTED_HEAD='b3c869cdb4034b03499a8d5d4720a67eec10084a'
SPECS=[
 {'batch':'batch-000654-cpu-identity-failed','manifest_sha256':'685a2d443c0ce080bb0adff7b8377494137d277c939a80258c90d7ed3cd35cf6','count':29,
  'run_id':'20261029T000655051332Z-prefill-i32-offset-v5-cpu-identity-failed',
  'utc_start':'2026-10-29T00:06:55.051332+00:00','status':'prefill_i32_v5_normal_identity_mismatch',
  'conclusion':'i32-offset v5 CPU-only正常编译后，A normal身份仍未匹配171100目标，按原门拒绝；无GPU、准确率或性能结果。'},
 {'batch':'batch-001204-cpu-mechanism','manifest_sha256':'35d386923c2178f4a2f73a1b6eea190eb29dbd6a0a2538c44445a1d26b9c59c6','count':50,
  'run_id':'20261029T001204223339Z-prefill-i32-offset-v6-cpu-mechanism-diagnostic',
  'utc_start':'2026-10-29T00:12:04.223339+00:00','status':'prefill_i32_v6_cpu_mechanism_diagnostic',
  'conclusion':'i32-offset v6 CPU机制诊断完成：两臂normal与Q-fragment编译及proof通过；A生产selected hash仍不匹配，故明确不授生产/GPU/官方资格。资源记录见原件；无数值或吞吐结果。'}]

def load_stager():
 p=REPO/'scripts/stage_pr105_232613_prefill_i32_20261029.py'
 spec=importlib.util.spec_from_file_location('stage_prev',p)
 m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
 for i,s in enumerate(SPECS,5):
  key=f'i32_v{i}'
  m.SOURCES[key]={'path':f'prefill-i32-offset-20261029/{s["batch"]}',
   'sha256':s['manifest_sha256'],'run':f'prefill-i32-offset-v{i}-20261029T{("000654Z" if i==5 else "001204Z")}',
   'count':s['count']}
 return m

def main():
 st=load_stager()
 head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip()
 if head!=EXPECTED_HEAD: raise RuntimeError(f'checkout moved: {head}')
 reg=REPO/'experiments/registry.csv'; old=reg.read_bytes()
 rows=list(csv.DictReader(io.StringIO(old.decode('utf-8-sig'))))
 if len(rows)!=473: raise RuntimeError(f'expected 473 registry rows, got {len(rows)}')
 old_ids={r['run_id'] for r in rows}
 if any(s['run_id'] in old_ids for s in SPECS): raise RuntimeError('new run id already registered')
 staged=[]
 for idx,s in enumerate(SPECS,5):
  key=f'i32_v{idx}'
  d,m_path,m,manifest_sha=st.load_manifest(key)
  total=st.verify_files(key,d,m)
  expected_run=f'prefill-i32-offset-v{idx}-20261029T{("000654Z" if idx==5 else "001204Z")}'
  if m.get('run')!=expected_run: raise RuntimeError(f'manifest run mismatch {key}: {m.get("run")}')
  packed=st.pack_run(s['run_id'],key)
  work=d/'cpu-probes'/m['run']
  receipt_path=next(work.glob('runs/*/receipt.json'))
  receipt=json.loads(receipt_path.read_text(encoding='utf-8'))
  check=json.loads((work/'cpu-check-result.json').read_text(encoding='utf-8'))
  if receipt.get('cuda_api_used_by_owner') is not False or check.get('status')!='PASS':
   raise RuntimeError(f'{key}: CPU-only/guard fixture failed')
  if idx==5:
   if receipt.get('exit_code')!=1: raise RuntimeError('v5 exit code mismatch')
   compile_path=next(work.glob('runs/*/compiled/*')) if False else None
   compile_result=None
   summary={'run_id':s['run_id'],'scope':'i32 offset v5 CPU-only compile/identity attempt','status':s['status'],
    'exit_code':1,'cuda_api_used_by_owner':False,'static_guard_status':'PASS',
    'conclusion':s['conclusion']}
   result={'receipt':receipt,'static_check':check,'identity_gate':'A normal identity mismatch; original gate rejected',
    'limitation':'CPU-only compile; no GPU launch, model accuracy, throughput or production qualification.'}
   phase='cpu_compile'
  else:
   compile_result=json.loads(next(work.glob('runs/*/compiled/compile-result.json')).read_text(encoding='utf-8'))
   if receipt.get('exit_code')!=0 or compile_result.get('production_qualification') is not False or compile_result.get('gpu_or_official_qualification') is not False:
    raise RuntimeError('v6 diagnostic-only contract mismatch')
   if not compile_result.get('q_fragment_proofs_pass') or not compile_result.get('diagnostic_complete'):
    raise RuntimeError('v6 proof/diagnostic incomplete')
   if compile_result.get('A_selected_identity_match') is not False:
    raise RuntimeError('v6 must retain failed A selected identity')
   summary={'run_id':s['run_id'],'scope':'i32 offset v6 CPU mechanism diagnostic only','status':s['status'],
    'exit_code':0,'cuda_api_used_by_owner':False,'static_guard_status':'PASS',
    'normal_and_q_fragment_compile':'completed for A/B','q_fragment_proofs_pass':True,
    'A_selected_identity_match':False,'production_qualification':False,'gpu_or_official_qualification':False,
    'conclusion':s['conclusion']}
   result={'receipt':receipt,'static_check':check,'compile_result':compile_result,
    'resource_observation_from_compile_review':{'A':'SGPR104, VGPR113, spills4','B':'SGPR85, VGPR112, spills0','shared_bytes':65536},
    'limitation':'CPU compiler mechanism proof only. No numeric output, GPU timing, production qualification, or official score.'}
   phase='cpu_compile'
  row={'run_id':s['run_id'],'local_date':'2026-10-29','utc_start':s['utc_start'],'profile_id':'prefill-i32-offset',
   'phase':phase,'device':'CPU','vllm_commit':'','flaggems_commit':'','input_len':'','output_len':'','concurrency':'',
   'num_prompts':'','profiler':'','status':s['status'],'conclusion':s['conclusion']}
  st.write_bundle(packed,row,summary,result)
  staged.append((row,packed))
  print(json.dumps({'run_id':s['run_id'],'archive_manifest_sha256':manifest_sha,'files':len(m['files']),
   'source_bytes':total,'raw_sha256':packed['raw_info']['raw_tar_sha256'],'raw_bytes':packed['raw_info']['raw_tar_bytes'],
   'chunks':len(packed['raw_info']['chunks'])},ensure_ascii=False),flush=True)
 buf=io.StringIO(newline=''); writer=csv.DictWriter(buf,fieldnames=rows[0].keys(),lineterminator='\n')
 for row,_ in staged: writer.writerow({k:row.get(k,'') for k in writer.fieldnames})
 with reg.open('ab') as f: f.write(buf.getvalue().encode('utf-8'))
 if not reg.read_bytes().startswith(old): raise RuntimeError('registry existing bytes changed')
 subprocess.run([sys.executable,'scripts/build_team_view.py'],cwd=REPO,check=True)
 print(json.dumps({'prior_rows':473,'added':2,'rows':475,'unique_run_ids':len({r['run_id'] for r in csv.DictReader(reg.open(encoding='utf-8',newline=''))}),
  'team_view':'rebuilt'},ensure_ascii=False))

if __name__=='__main__': main()
