"""只读已编LLVM/ASM，补原checker未识别的CoreX barrier名字。"""
from pathlib import Path
import hashlib,json,re
R=Path(__file__).resolve().parents[2]
D=R/'archive/hotspot-layout-20261026/batch-160904-native-q32-transfer-fragments/cpu-probes/20261027T160904Z-native-q32-transfer-fragments'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(D/'probe.ll')=='4dbcf9285faea6999be466e10f3fbfba0df8a873df3a8c63f282389dc6c175c2'
assert sha(D/'probe.s')=='64907647f15bd30c7bb1ad0680dda6330a8ff5b66a157d47d6c32bd8c5239456'
original=(D/'compile-check.json').read_bytes();j=json.loads(original)
assert j['passed'] is False and [k for k,v in j['checks'].items() if not v]==['phase_barriers_present']
ll=(D/'probe.ll').read_text().splitlines();asm=(D/'probe.s').read_text().splitlines()
indices=lambda lines,pattern:[i+1 for i,l in enumerate(lines) if re.search(pattern,l)]
lb=indices(ll,r'\bcall\b.*@llvm\.bi\.sl\.barrier\(\)')
ab=indices(asm,r'^\s*sl_barrier\s*$')
assert lb==[132,222,336,716,762] and ab==[143,178,305,525,547]
ls=indices(ll,r'\bcall\b.*@llvm\.bi\.sme\.load\.')
ss=indices(asm,r'^\s*sl_sme_load_')
lw=indices(ll,r'\bcall\b.*@llvm\.bi\.sl\.waitcnt\(i64 8\)')
sw=indices(asm,r'^\s*sl_wait g2scnt\(0\)')
lm=indices(ll,r'\bcall\b.*@llvm\.bi\.matrix\.mad\.f32x4\.bf16x4')
sm=indices(asm,r'^\s*ml_matrix_mad')
assert len(ls)==len(ss)==32 and len(lm)==len(sm)==64
assert lb[1]<min(ls)<=max(ls)<lw[0]<lb[2]<min(lm)<lm[31]<lb[3]<lb[4]<lm[32]
assert ab[1]<min(ss)<=max(ss)<sw[0]<ab[2]<min(sm)<sm[31]<ab[3]<ab[4]<sm[32]
assert 'br i1 %180, label %181, label %255' in '\n'.join(ll)
assert '%180 = icmp eq i32 %24, 0' in '\n'.join(ll)
# Exact local spans already inspected with their shared pointers/offsets:
# Q loads 136..216 -> barrier222 -> warp0 copies -> wait -> merge255/barrier336.
# All QK K reads+32MMA finish before716; P writes724..761 then762; PV V base32768.
assert all('addrspace(3)' in ll[n-1] for n in [136,139,213,216,724,728,735,739,746,750,757,761,766,769,773,776])
assert 'i32 32768' in ll[771] and 'i32 32768' in ll[341]
result=dict(source='160904 existing compiler outputs; no recompile',
 inputs={n:sha(D/n) for n in ['probe.ll','probe.s','compile-check.json','compile-check.log']},
 original_passed=False,original_barrier_count=0,original_error_preserved=True,
 correction='checker searched llvm.nvvm.barrier.cta.sync.aligned.all; actual CoreX uses llvm.bi.sl.barrier',
 CoreX_barriers_LLVM_lines=lb,barriers_ASM_lines=ab,SME_LLVM_lines=[min(ls),max(ls)],SME_ASM_lines=[min(ss),max(ss)],
 wait_LLVM=lw,wait_ASM=sw,QK_MMA_ASM=[sm[0],sm[31]],PV_MMA_ASM=[sm[32],sm[-1]],
 machine_phase_order_verified=True,issuing_warp=0,all_warps_merge_before_consumers=True,
 shared_lifetimes={'Q':[0,65536],'K':[0,16384],'V':[32768,49152],'P':[0,32768],
  'order':'Q loads/barrier2 -> SME(wait warp0)/barrier3 -> all K QK reads/barrier4 -> P stores/barrier5 -> P+V PV'},
 resources=j['resources'],compiler_only_acceptance=True,numerical_qualified=False,performance_qualified=False,GPU_executed=False,
 limits=['machine synchronization/alias order only; not a numerical M16 mapping proof',
 'native A-word and C-component matrix coordinates remain a separate non-symmetric device gate'])
assert (D/'compile-check.json').read_bytes()==original
P=Path(__file__).resolve().parent/'compile-backend-barrier-review.json'
P.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
