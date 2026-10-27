"""单page原生布局/矩阵数值诊断；不计时，不运行历史loop或替换生产。"""
from pathlib import Path
import hashlib,importlib.util,json,os,subprocess,traceback
HERE=Path(__file__).resolve().parent
SOURCE_SHA='2596cc09caf9b5b38b49755ae9af41ebdcf59a1d5ad889fc8e9319d1584438d1'
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def worker(run,model):
 run=Path(run);result=dict(status='started',cases=[],timings=[],kind='native_single_page_numeric',performance_qualified=False,official_qualified=False,model_accuracy_qualified=False)
 try:
  import torch,numpy as np
  from torch.utils.cpp_extension import load as build
  import layout,fp_reference,exp2_reference
  result['cpu_layout']=layout.check_symbolic()
  assert hashlib.sha256((HERE/'baseline.py').read_bytes()).hexdigest()==SOURCE_SHA
  baseline=load('current_main56_gqa_page_reference',HERE/'baseline.py')
  os.environ['MAX_JOBS']='1';os.environ['TORCH_CUDA_ARCH_LIST']='7.1'
  builddir=run/'native-build';builddir.mkdir()
  cuda_flags=['-O3','-std=c++17','-D__ILUVATAR__','-D__MR__','-x','ivcore','--cuda-gpu-arch=ivcore11','--cuda-path=/usr/local/corex']
  lib=build(name='corex_native_page16_probe',sources=[str(HERE/'bridge.cpp'),str(HERE/'page16.cu')],build_directory=str(builddir),extra_cflags=['-O3','-std=c++17'],extra_cuda_cflags=cuda_flags,is_python_module=False,verbose=True)
  result['library_sha256']=hashlib.sha256(Path(lib).read_bytes()).hexdigest()
  commands=subprocess.check_output(['ninja','-t','commands'],cwd=builddir,text=True)
  (run/'native-build-commands.txt').write_text(commands)
  cu_commands=[line for line in commands.splitlines() if str(HERE/'page16.cu') in line]
  assert len(cu_commands)==1 and all(flag in cu_commands[0] for flag in cuda_flags),'实际extension命令未保持已审target/宏/优化级别'
  assert not any(flag in cu_commands[0] for flag in ['-ffast-math','--use_fast_math']), '不允许全kernel fast-math'
  result['actual_cuda_command']=cu_commands[0];result['cuda_compile_flags_match']=True
  torch.manual_seed(5631)
  q=(torch.randn((1,16,128),dtype=torch.float32)*.25).bfloat16().cuda()
  cache=(torch.randn((4,2,16,2,128),dtype=torch.float32)*.25).bfloat16().cuda()
  table=torch.tensor([[2]],device='cuda',dtype=torch.int32);lens=torch.tensor([16],device='cuda',dtype=torch.int32)
  scale=(128**-.5)*1.4426950408889634
  out=torch.empty((1,16,1,128),dtype=torch.float32,device='cuda');maximum=torch.empty((1,16,1),dtype=torch.float32,device='cuda');summation=torch.empty_like(maximum)
  def reference():
   return baseline._gqa_decode_attention[(1,2,1)](segm_output_ptr=out,segm_max_ptr=maximum,segm_expsum_ptr=summation,query_ptr=q,key_cache_ptr=cache[:,0],value_cache_ptr=cache[:,1],seq_lens_ptr=lens,block_table_ptr=table,softmax_scale_log2e=scale,queries_per_kv=8,block_table_stride=1,query_stride_token=2048,query_stride_head=128,k_stride_block=8192,k_stride_slot=256,k_stride_head=128,v_stride_block=8192,v_stride_slot=256,v_stride_head=128,segment_stride_token=2048,segment_stride_head=128,segment_stride_segment=128,max_stride_token=16,max_stride_head=1,HEAD_SIZE=128,PAGE_SIZE=16,ROWS=8,SEGMENTS=1,num_warps=1,num_stages=1,num_ctas=1)
  def native():return torch.ops.corex_native_page16_probe.page16(q,cache,table,scale)
  def bits(a,b):return a.dtype==b.dtype and torch.equal(a.contiguous().view(torch.uint8),b.contiguous().view(torch.uint8))
  def expected_raw():
   c=cache.cpu().view(torch.int16).numpy().view(np.uint16)
   return layout.expected_shared(c,int(table.cpu()[0,0]),np)
  def check(label,outputs=None):
   qb,cb,tb=q.clone(),cache.clone(),table.clone();cpu_rng=torch.get_rng_state().clone();gpu_rng=torch.cuda.get_rng_state().clone()
   reference();b=native() if outputs is None else outputs;torch.cuda.synchronize()
   actual=b[6].cpu().numpy().view(np.uint16).reshape(2,4096)
   expected=expected_raw();shared_equal=bool(np.array_equal(actual,expected))
   result['last_raw_shared']=dict(label=label,passed=shared_equal,mismatched_bf16=int(np.count_nonzero(actual!=expected)))
   save(run/'result.json',result)
   if not shared_equal:
    np.savez(run/(label+'-shared-mismatch.npz'),actual=actual,expected=expected)
   # Stop at the format boundary: do not blame or tune softmax for wrong layout.
   assert shared_equal,'SME shared swizzle/inverse gate failed'
   pref=torch.empty_like(b[4]);pbref=torch.empty_like(b[5])
   exp_kernel=exp2_reference.probability_reference[(16,)](b[3],pref,pbref,num_warps=1,num_stages=1)
   exp_ir=exp_kernel.asm['llir']
   exp_asm=exp_kernel.asm.get('asm',exp_kernel.asm.get('ptx',''))
   assert '@llvm.nvvm.ex2.approx.ftz.f32(' in exp_ir,'独立P原语未保持原tl.exp2路径'
   (run/'exp2-reference.ll').write_text(exp_ir)
   (run/'exp2-reference.s').write_text(exp_asm)
   passed=dict(label=label,raw_shared_bitwise=shared_equal,probability_fp32_bitwise=bits(pref,b[4]),probability_bf16_bitwise=bits(pbref,b[5]),partial_acc_bitwise=bits(out[:,:,0],b[0]),max_natural_bitwise=bits(maximum[:,:,0],b[1]),sum_bitwise=bits(summation[:,:,0],b[2]),finite=all(bool(torch.isfinite(x).all()) for x in b[:5]),query_unchanged=bits(q,qb),cache_unchanged=bits(cache,cb),table_unchanged=bits(table,tb),cpu_rng_unchanged=bits(torch.get_rng_state(),cpu_rng),gpu_rng_unchanged=bits(torch.cuda.get_rng_state(),gpu_rng))
   if label=='underflow_P':
    score64=b[3].double().cpu().numpy();exact_p=np.exp2(score64-score64.max(axis=1,keepdims=True))
    coverage=dict(normal=bool(np.any(exact_p>=np.finfo(np.float32).tiny)),subnormal=bool(np.any((exact_p>0)&(exact_p<np.finfo(np.float32).tiny))),below_smallest_subnormal=bool(np.any(exact_p<float(np.nextafter(np.float32(0),np.float32(1)))*.5)))
    result['underflow_input_coverage']=coverage
    passed['underflow_input_covered']=all(coverage.values())
   result['cases'].append(passed);save(run/'result.json',result)
   if not all(v for k,v in passed.items() if k!='label'):
    np.savez(run/(label+'-partial-mismatch.npz'),original_acc=out[:,:,0].cpu().numpy(),native_acc=b[0].cpu().numpy(),original_max=maximum[:,:,0].cpu().numpy(),native_max=b[1].cpu().numpy(),original_sum=summation[:,:,0].cpu().numpy(),native_sum=b[2].cpu().numpy(),native_score=b[3].cpu().numpy(),native_probability=b[4].cpu().numpy(),tl_exp2_probability=pref.cpu().numpy())
    raise AssertionError('原partial数值/只读/RNG门失败，停止不改容差')
   # Independent original CPU-FP64 contract; no new tolerance is introduced.
   normalized={'original':(out[:,:,0]/summation[:,:,0,None]).bfloat16(),'native':(b[0]/b[2][:,:,None]).bfloat16()}
   oracle=fp_reference.sampled_reference(torch,run,label,q,cache,lens,table,normalized,1)
   result.setdefault('fp64',[]).append(oracle);save(run/'result.json',result)
   assert all(x['passed'] for x in oracle['arms'].values()),'原独立FP64门失败'
   return b
  check('normal_page2')
  q.neg_();cache.copy_(cache.flip(2));table.fill_(1);check('changed_Q_KV_page1')
  q.zero_();check('zero_Q')
  q[:,:,0]=1;cache[:,0].zero_()
  underflow=torch.tensor([0,-496,-960,-984,-988,-992,-996,-1000,-1016,-1100,-1152,-1160,-1168,-1176,-1200,-2048],device='cuda',dtype=torch.bfloat16)
  cache[:,0,:,:,0]=underflow[None,:,None]
  check('underflow_P')
  cache.normal_(0,.25)
  q.normal_(0,.25);check('before_graph')
  # Diagnostic Graph retains every stage output. No graph time is measured.
  graph=torch.cuda.CUDAGraph();native();torch.cuda.synchronize()
  with torch.cuda.graph(graph):graph_outputs=native()
  q.neg_();cache.neg_();table.fill_(3)
  for x in graph_outputs:
   if x.dtype.is_floating_point:x.fill_(float('nan'))
   else:x.fill_(12345)
  graph.replay();check('changed_poisoned_graph',graph_outputs)
  del graph,graph_outputs
  side=torch.cuda.Stream();side.wait_stream(torch.cuda.current_stream())
  with torch.cuda.stream(side):check('side_stream')
  torch.cuda.current_stream().wait_stream(side);torch.cuda.synchronize()
  result.update(status='single_page_numeric_passed',scope='page16/D128/8Q per KV head only; no historical state/tail/empty/reducer/model/performance coverage')
  save(run/'result.json',result);return 0
 except BaseException:
  result.update(status='failed_stop',error=traceback.format_exc());save(run/'result.json',result);traceback.print_exc();return 1
