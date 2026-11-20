"""使用已核vLLM API建立并清理真实world1/TP1；不伪造全局组。"""
from datetime import timedelta
import hashlib,json
from pathlib import Path
import traceback

_attempted=False
_state={}
_dist=None

def save(run):
    (Path(run)/'distributed.json').write_text(json.dumps(_state,indent=2)+'\n')

def initialize(config,run):
    global _attempted,_dist
    import torch
    from vllm.distributed import parallel_state as dist
    from vllm.platforms import current_platform
    if hashlib.sha256(Path(dist.__file__).read_bytes()).hexdigest()!='1feda9ac98c1dd14cbad60a9205194d224ad7d75656c6e94cffbe3bdbcbf4003':
        raise RuntimeError('distributed API changed')
    _dist=dist
    if torch.distributed.is_initialized() or dist.model_parallel_is_initialized():
        raise RuntimeError('child inherited a distributed group')
    pc=config.parallel_config
    if any(getattr(pc,k)!=1 for k in ('world_size','nnodes','data_parallel_size','tensor_parallel_size','pipeline_parallel_size','prefill_context_parallel_size','decode_context_parallel_size')) or pc.enable_elastic_ep:
        raise RuntimeError('requires actual single rank configuration')
    backend=current_platform.dist_backend
    if not torch.distributed.is_backend_available(backend):
        raise RuntimeError('platform backend unavailable')
    rendezvous=Path(run)/'world1-rendezvous'
    if rendezvous.exists():raise RuntimeError('requires fresh rendezvous')
    _state.update(backend=backend,world_size=1,rank=0,local_rank=0,init_method=rendezvous.resolve().as_uri())
    _attempted=True
    save(run)
    dist.init_distributed_environment(world_size=1,rank=0,distributed_init_method=rendezvous.resolve().as_uri(),local_rank=0,backend=backend,timeout=timedelta(seconds=90))
    dist.ensure_model_parallel_initialized(tensor_model_parallel_size=1,pipeline_model_parallel_size=1,prefill_context_model_parallel_size=1,decode_context_model_parallel_size=1)
    if torch.distributed.get_world_size()!=1 or dist.get_tensor_model_parallel_rank()!=0 or dist.get_tensor_model_parallel_world_size()!=1:
        raise RuntimeError('real TP/WORLD identity mismatch')
    _state['initialized']=True
    save(run)

def execute(call,run):
    try:
        return call()
    finally:
        if _attempted:
            import torch
            errors=[]
            try:
                torch.cuda.synchronize()
            except BaseException:
                _state['device_unsettled']=traceback.format_exc()
                save(run)
                raise
            for cleanup in (_dist.destroy_model_parallel,_dist.destroy_distributed_environment):
                try:cleanup()
                except BaseException:errors.append(traceback.format_exc())
            _state.update(cleanup_errors=errors,torch_initialized_after=torch.distributed.is_initialized(),model_parallel_initialized_after=_dist.model_parallel_is_initialized())
            save(run)
            if errors or _state['torch_initialized_after'] or _state['model_parallel_initialized_after']:
                raise RuntimeError('distributed cleanup failed')
