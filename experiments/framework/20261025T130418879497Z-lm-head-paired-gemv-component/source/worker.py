"""固定 M2 paired-GEMV：随机 BF16 组件、CPU FP64 参考、一次 ABBA。"""
import hashlib
import importlib
import inspect
import json
from pathlib import Path
import statistics
import traceback

from reused_helpers import timed_batch

LINEAR_SHA = 'd431a4fa144ed67dc3deab46dd5beace3612858075f85c39e602447ba3bf768a'
CONFIG = dict(BLOCK_M=2, BLOCK_N=128, BLOCK_K=32, GROUP_M=8,
              SPLIT_K=1, EVEN_K=True, BIAS=False, num_warps=8, num_stages=2)


def write(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2,
                                   allow_nan=False) + '\n', encoding='utf-8')


def dump(compiled, directory):
    directory.mkdir()
    for key, value in compiled.asm.items():
        if isinstance(value, (bytes, str)):
            (directory / (key + ('.bin' if isinstance(value, bytes) else '.txt'))).write_bytes(
                value if isinstance(value, bytes) else value.encode())
    return dict(n_regs=getattr(compiled, 'n_regs', None),
                n_spills=getattr(compiled, 'n_spills', None),
                metadata=str(getattr(compiled, 'metadata', None)))


def metrics(torch, output, reference):
    actual = output.detach().cpu().double()
    rounded = reference.to(torch.bfloat16).double()
    finite = bool(torch.isfinite(actual).all())
    if not finite:
        return dict(finite=False, passed=False)
    error = (actual-reference).abs()
    rounded_error = (actual-rounded).abs()
    return dict(finite=True, max_abs_vs_fp64=float(error.max()),
        max_abs_vs_rounded_fp64=float(rounded_error.max()),
        relative_l2=float(error.norm() / reference.norm()),
        rounded_equal_fraction=float((actual == rounded).double().mean()),
        argmax_matches_fp64=actual.argmax(-1).tolist() == reference.argmax(-1).tolist(),
        passed=bool(torch.allclose(actual, rounded, rtol=0.01, atol=0.001)))


def worker(run, model):
    result = dict(status='started', scope='随机权重/激活的单 M2 组件；不授予模型或官方资格',
        candidate='BN32/BK256/8warps paired-GEMV；唯一配置', baseline=CONFIG,
        shape=[2, 130560, 2048], seed=20261025, cases=[],
        limitations=['CPU FP64 归约参考与原 tl.dot 的归约顺序不同。',
                    '预分配输出；计时包含全部词表输出写入，不含分配、参考或模型其余部分。',
                    '未接模型、未修改官方采样；随机组件通过不代表模型准确率通过。'])
    try:
        import torch
        import triton
        import flag_gems
        import candidate
        require = lambda ok, msg: None if ok else (_ for _ in ()).throw(RuntimeError(msg))
        config = json.loads((model/'config.json').read_text())
        require((config['hidden_size'], config['vocab_size'], config['num_hidden_layers'])
                == (2048, 130560, 42), '模型 config 不符')
        require(flag_gems.current_work_registrar is None, '参考不得经过 FlagGems 全局覆盖')
        module = importlib.import_module('flag_gems.runtime.backend._iluvatar.ops.linear')
        source = Path(inspect.getsourcefile(module.linear))
        require(hashlib.sha256(source.read_bytes()).hexdigest() == LINEAR_SHA, '原 linear 源改变')
        (run/'source'/'installed-linear.py').write_bytes(source.read_bytes())
        jit = module.linear_kernel
        chain = []
        while not isinstance(jit, triton.runtime.JITFunction):
            chain.append(type(jit).__name__)
            jit = jit.fn
        result['baseline_source'] = dict(path=str(source), sha256=LINEAR_SHA, unwrapped=chain,
            explanation='原 JIT 数学与已有 DB 固定 config；组件绕过调参装饰器，不改 DB')
        result['environment'] = dict(torch=torch.__version__, triton=triton.__version__,
            flag_gems=getattr(flag_gems, '__version__', None), device=torch.cuda.get_device_name(),
            cpu_threads=torch.get_num_threads())
        require('BI-V150' in result['environment']['device'], '不是 BI-V150')
        # FP64 参考完全在 CPU；不受 CUDA mm/FlagGems/native dispatch 影响。
        generator = torch.Generator(device='cpu').manual_seed(result['seed'])
        x_cpu = torch.randn((2, 2048), generator=generator, dtype=torch.bfloat16)
        w_cpu = torch.randn((130560, 2048), generator=generator, dtype=torch.bfloat16)
        reference = torch.empty((2, 130560), dtype=torch.float64)
        for start in range(0, 130560, 4096):
            end = min(start+4096, 130560)
            reference[:, start:end] = x_cpu.double() @ w_cpu[start:end].double().T
        x, weight = x_cpu.cuda(), w_cpu.cuda()
        x2, weight2 = x_cpu.flip(0).contiguous().cuda(), w_cpu.flip(0).contiguous().cuda()
        reference2 = reference.flip((0, 1))
        del w_cpu
        require(x.data_ptr() != x2.data_ptr() and weight.data_ptr() != weight2.data_ptr(), '变指针失败')
        buffers = [torch.full((2*130560+64,), 123.0, device='cuda', dtype=torch.bfloat16) for _ in range(2)]
        a, b = [buffer[32:-32].view(2, 130560) for buffer in buffers]
        def baseline(inp, w, out):
            return jit[(1020, 1)](inp, w, w, out, 2, 130560, 2048,
                2048, 1, 2048, 1, 130560, 1, 0, **CONFIG)
        torch.cuda.synchronize()
        cpu_rng = torch.get_rng_state().clone()
        gpu_rng = torch.cuda.get_rng_state().clone()
        compiled = (baseline(x, weight, a), candidate.launch(x, weight, b))
        torch.cuda.synchronize()
        result['resources'] = [dump(kernel, run/('ir-'+label)) for label,kernel in zip(('baseline','candidate'),compiled)]
        result['pointers'] = dict(x=x.data_ptr(), weight=weight.data_ptr(), x2=x2.data_ptr(), weight2=weight2.data_ptr())
        result['strides'] = dict(x=list(x.stride()), weight=list(weight.stride()), output=list(a.stride()))
        saved = {}
        for label, inp, w, ref in (('original',x,weight,reference), ('changed-pointers-and-content',x2,weight2,reference2)):
            baseline(inp,w,a)
            candidate.launch(inp,w,b)
            torch.cuda.synchronize()
            am,bm = metrics(torch,a,ref),metrics(torch,b,ref)
            both = (a.float()-b.float()).abs().max().item() if am['finite'] and bm['finite'] else None
            guard = all(bool((buf[:32] == 123).all() and (buf[-32:] == 123).all()) for buf in buffers)
            record = dict(name=label,baseline=am,candidate=bm,max_abs_between=both,guard=guard)
            result['cases'].append(record)
            saved[label] = dict(baseline=a.cpu(),candidate=b.cpu(),reference_fp64=ref)
            torch.save(saved, run/'outputs.pt')
            write(run/'result.json',result)
            require(am['passed'] and bm['passed'] and guard, '组件数值/guard失败，停止计时')
        require(torch.equal(cpu_rng,torch.get_rng_state()) and torch.equal(gpu_rng,torch.cuda.get_rng_state()), 'RNG变化')
        result['rng_unchanged'] = True
        callbacks = {'A':lambda:baseline(x,weight,a),'B':lambda:candidate.launch(x,weight,b)}
        for _ in range(5):
            callbacks['A']();callbacks['B']()
        pairs=[(torch.cuda.Event(enable_timing=True),torch.cuda.Event(enable_timing=True)) for _ in range(4)]
        for pair in pairs:
            for event in pair:event.record()
        torch.cuda.synchronize()
        result['timings'] = [dict(arm=arm,**timed_batch(torch,callbacks[arm],pair,32))
            for arm,pair in zip('ABBA',pairs)]
        result['post_timing'] = dict(baseline=metrics(torch,a,reference),
            candidate=metrics(torch,b,reference), rng_unchanged=
                torch.equal(cpu_rng,torch.get_rng_state()) and torch.equal(gpu_rng,torch.cuda.get_rng_state()),
            guard=all(bool((buf[:32] == 123).all() and (buf[-32:] == 123).all()) for buf in buffers))
        post=result['post_timing']
        require(post['baseline']['passed'] and post['candidate']['passed'] and post['guard']
                and post['rng_unchanged'], '重复执行后数值/guard/RNG失败')
        means={arm:statistics.mean(r['event_per_call_ms'] for r in result['timings'] if r['arm']==arm) for arm in 'AB'}
        wall={arm:statistics.mean(r['wall_per_call_ms'] for r in result['timings'] if r['arm']==arm) for arm in 'AB'}
        result['event_mean_ms']=means
        result['wall_mean_ms']=wall
        result['event_gain_percent']=(1-means['B']/means['A'])*100
        result['decision']='组件正向，待主线决定模型验证；未确认端到端收益' if means['B']<means['A'] and wall['B']<wall['A'] else '无组件净收益，停止此方案'
        result['status']='completed'
    except BaseException:
        result['status']='failed'
        result['error']=traceback.format_exc()
        traceback.print_exc()
    finally:
        write(run/'result.json',result)
    return 0 if result['status']=='completed' else 1
