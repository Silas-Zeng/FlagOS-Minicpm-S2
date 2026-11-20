"""GPU组件用的候选描述器；本模块不import torch，不主动访问设备。

未GPU验证，只给已有owner中的worker显式调用。不能独立安装生产环境。
"""
from span_layout import plan_span


def backing_view(cache):
    if str(cache.dtype) != "torch.bfloat16" or cache.device.type != "cuda":
        raise ValueError("only existing BI-V150 BF16 cache is supported")
    shape, strides = tuple(cache.shape), tuple(cache.stride())
    plan = plan_span(shape, strides, cache.storage_offset(),
                     cache.untyped_storage().nbytes() // cache.element_size())
    view = cache.as_strided(plan["size"], plan["stride"], plan["storage_offset"])
    assert view.data_ptr() == cache.data_ptr()
    assert view.untyped_storage().data_ptr() == cache.untyped_storage().data_ptr()
    assert view.is_contiguous()
    return view, plan["row_strides"]


def prepare_launch_kwargs(original):
    """Only K/V pointer descriptors and stride units change. Caller retains views.

    Baseline receives the original dict; candidate receives this new dictionary.
    The original reducer/scratch/grid and all other parameters stay unchanged.
    """
    kwargs = dict(original)
    keepalive = []
    for family, pointer in (("k", "key_cache_ptr"), ("v", "value_cache_ptr")):
        view, row_strides = backing_view(kwargs[pointer])
        kwargs[pointer] = view
        keepalive.append(view)
        for field, row_stride in zip(("block", "slot", "head"), row_strides):
            previous = kwargs.pop(f"{family}_stride_{field}")
            assert previous == row_stride * 128
            kwargs[f"{family}_row_stride_{field}"] = row_stride
    return kwargs, keepalive
