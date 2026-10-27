"""CPU-only compiler text checks; original numeric/reducer doors remain required."""
from pathlib import Path
import hashlib,json,re,sys
p=Path(sys.argv[1]);ll=(p/'gqa.ll').read_text();asm=(p/'gqa.s').read_text()
kernels=[m for m in re.finditer(r'^define[^\n]*@([^\s(]+)\([^\n]*\)[^{]*\{(.*?)^\}',ll,re.M|re.S) if 'corex_native_gqa_producer_draft' in m.group(1)]
assert len(kernels)==1 and kernels[0].group(2).strip(),'missing/empty/multiple producer kernel'
assert 'ILj4EE' in kernels[0].group(1),'not template Segments4'
body=kernels[0].group(2)
count=lambda pattern,text:len(re.findall(pattern,text,re.M))
counts=dict(mma_llvm=count(r'\bcall\b[^\n]*@llvm\.bi\.matrix\.mad\.f32x4\.bf16x4',body),sme_llvm=count(r'\bcall\b[^\n]*@llvm\.bi\.sme\.load\.',body),wait8=count(r'@llvm\.bi\.sl\.waitcnt\(i64 8\)',body),exp2=count(r'@llvm\.nvvm\.ex2\.approx(?:\.ftz)?\.f32\(',body),mma_asm=count(r'^\s*ml_matrix_mad',asm),sme_asm=count(r'^\s*sl_sme_load_',asm),sum_fma_asm=count(r'^\s*ml_fma_f32',asm))
number=lambda key:int(re.search(r'^\s*'+re.escape(key)+r'\s*=\s*(\d+)',asm,re.M).group(1))
yaml_number=lambda key:int(re.search(r'^\s*\.'+re.escape(key)+r':\s*(\d+)',asm,re.M).group(1))
resources=dict(shared_bytes=number('workgroup_group_segment_byte_size'),private_bytes=number('workitem_private_segment_byte_size'),SGPR=number('warp_sgpr_count'),VGPR=number('workitem_vgpr_count'),sgpr_spill_count=yaml_number('sgpr_spill_count'),vgpr_spill_count=yaml_number('vgpr_spill_count'))
checks=dict(real_kernel=bool(kernels),SME_present=counts['sme_llvm']>=8 and counts['sme_asm']>=8,MMA_present=counts['mma_llvm']>=16 and counts['mma_asm']>=16,waits_present=counts['wait8']>=2,exp2_machine_present=counts['exp2']>=4 and count(r'^\s*ml_exp_f32',asm)>=4,original_L_sum_FMA=counts['sum_fma_asm']>=2,single_8KiB_shared=resources['shared_bytes']==8192,same_float_mode=number('float_mode')==12)
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
r=dict(kernel=kernels[0].group(1),checks=checks,counts=counts,resources=resources,passed=all(checks.values()),files={f.name:sha(f) for f in [p/'gqa.ll',p/'gqa.s']},variant='synchronous_0',scope='full-loop compiler only; tail may duplicate static instruction bodies, no fixed sixteen-MMA assertion',gpu_executed=False,numeric_qualified=False,performance_qualified=False)
(p/'compile-check.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
assert r['passed'],'inspect compiler delta; not a numeric verdict'
