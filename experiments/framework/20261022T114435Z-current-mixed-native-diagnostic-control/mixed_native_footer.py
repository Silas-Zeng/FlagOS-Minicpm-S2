# 只用于精确6f的短native诊断；不改数学、调度、服务参数，不作为性能成绩。
import functools as _native_functools
import json as _native_json
import os as _native_os
from pathlib import Path as _NativePath


def _native_event(event, **values):
    path = _native_os.environ.get('MINICPM_NATIVE_PROFILE_EVENTS')
    if path:
        with _NativePath(path).open('a', encoding='utf-8') as handle:
            handle.write(_native_json.dumps(dict(
                event=event, pid=_native_os.getpid(), source=__file__, **values,
            )) + '\n')


_native_event('module_loaded', kind='three_consecutive_natural_mixed_steps')
_native_execute_original = ModelRunnerFL.execute_model
_native_shutdown_original = ModelRunnerFL.shutdown


def _native_stop(self, complete):
    torch.cuda.synchronize()
    result = int(torch.cuda.cudart().cudaProfilerStop())
    self._native_profile_active = False
    self._native_profile_done = True
    _native_event('stop' if complete else 'shutdown_incomplete', result=result,
                  executed_shapes=self._native_window_shapes,
                  executed_scheduled_tokens=self._native_window_lengths)
    if result:
        raise RuntimeError('cudaProfilerStop failed: ' + str(result))
    print('NATIVE_MIXED_PROFILE_STOP complete=' + str(complete), flush=True)


@_native_functools.wraps(_native_execute_original)
def _native_profile_execute(self, scheduler_output, *args, **kwargs):
    # sample_tokens在execute_model之外；下一步入口才停止，保留第三步完整sampler。
    if (getattr(self, '_native_profile_active', False)
            and len(self._native_window_shapes) == 3):
        _native_stop(self, True)
        if ModelRunnerFL.execute_model is _native_profile_execute:
            ModelRunnerFL.execute_model = _native_execute_original
    if getattr(self, '_native_profile_done', False):
        return _native_execute_original(self, scheduler_output, *args, **kwargs)
    values = list(scheduler_output.num_scheduled_tokens.values())
    shape = [len(values), sum(values), max(values, default=0)]
    eligible = len(values) >= 2 and 1 in values and max(values) > 1 and all(v > 0 for v in values)
    if not getattr(self, '_native_profile_active', False) and eligible:
        self._native_mixed_seen = getattr(self, '_native_mixed_seen', 0) + 1
        if self._native_mixed_seen == 3:
            torch.cuda.synchronize()
            _native_event('start', shape=shape, scheduled_tokens=values,
                          single_query_count=values.count(1), eligible_mixed_seen=3)
            result = int(torch.cuda.cudart().cudaProfilerStart())
            if result:
                raise RuntimeError('cudaProfilerStart failed: ' + str(result))
            self._native_profile_active = True
            self._native_window_shapes, self._native_window_lengths = [], []
            print('NATIVE_MIXED_PROFILE_START batch=' + str(len(values)), flush=True)
    # 原调用恰一次；异常不冒充完整profile窗口，交原shutdown停止采集。
    result = _native_execute_original(self, scheduler_output, *args, **kwargs)
    if getattr(self, '_native_profile_active', False):
        self._native_window_shapes.append(shape)
        self._native_window_lengths.append(values)
    return result


def _native_profile_shutdown(self):
    if getattr(self, '_native_profile_active', False):
        _native_stop(self, False)
    return _native_shutdown_original(self)


ModelRunnerFL.execute_model = _native_profile_execute
ModelRunnerFL.shutdown = _native_profile_shutdown
print('BIV150_CURRENT_MIXED_NATIVE_ARMED diagnostics_only=1', flush=True)
