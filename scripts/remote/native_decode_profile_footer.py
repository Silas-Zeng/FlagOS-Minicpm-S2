# Diagnostic-only footer, appended to an isolated retained ModelRunnerFL source.
# Capture five eligible decode iterations through native CoreX ixsys. No model
# math, scheduling choice, server argument or sampling parameter is changed.
import functools as _native_functools
import json as _native_json
import os as _native_os
from pathlib import Path as _NativePath


def _native_event(event, **values):
    path = _native_os.environ.get('MINICPM_NATIVE_PROFILE_EVENTS')
    if path:
        with _NativePath(path).open('a') as handle:
            handle.write(_native_json.dumps(dict(
                event=event, pid=_native_os.getpid(), source=__file__, **values,
            )) + '\n')


_native_event('module_loaded')

_native_execute_original = ModelRunnerFL.execute_model
_native_shutdown_original = ModelRunnerFL.shutdown


@_native_functools.wraps(_native_execute_original)
def _native_profile_execute(self, scheduler_output, *args, **kwargs):
    scheduled = scheduler_output.num_scheduled_tokens
    shape = [len(scheduled), sum(scheduled.values()),
             max(scheduled.values(), default=0)]
    if not getattr(self, '_native_first_execute', False):
        self._native_first_execute = True
        _native_event('first_execute', shape=shape)
    if getattr(self, '_native_profile_active', False):
        self._native_window_shapes.append(shape)
    eligible = len(scheduled) >= 16 and all(value == 1 for value in scheduled.values())
    if eligible:
        seen = getattr(self, '_native_decode_seen', 0) + 1
        self._native_decode_seen = seen
        if seen == 3:
            torch.cuda.synchronize()
            _native_event('start', shape=shape)
            result = int(torch.cuda.cudart().cudaProfilerStart())
            if result:
                raise RuntimeError('cudaProfilerStart failed: ' + str(result))
            self._native_profile_active = True
            self._native_window_shapes = [shape]
            print('NATIVE_PROFILE_START batch=' + str(len(scheduled)), flush=True)
        elif seen == 8:
            torch.cuda.synchronize()
            result = int(torch.cuda.cudart().cudaProfilerStop())
            self._native_profile_active = False
            # The final recorded shape belongs to the not-yet-executed stop step.
            _native_event('stop', result=result,
                          executed_shapes=self._native_window_shapes[:-1])
            if result:
                raise RuntimeError('cudaProfilerStop failed: ' + str(result))
            print('NATIVE_PROFILE_STOP five_decode_iterations', flush=True)
    return _native_execute_original(self, scheduler_output, *args, **kwargs)


def _native_profile_shutdown(self):
    if getattr(self, '_native_profile_active', False):
        torch.cuda.synchronize()
        torch.cuda.cudart().cudaProfilerStop()
        self._native_profile_active = False
        _native_event('shutdown_incomplete')
        print('NATIVE_PROFILE_STOP shutdown_before_window_completed', flush=True)
    return _native_shutdown_original(self)


ModelRunnerFL.execute_model = _native_profile_execute
ModelRunnerFL.shutdown = _native_profile_shutdown
