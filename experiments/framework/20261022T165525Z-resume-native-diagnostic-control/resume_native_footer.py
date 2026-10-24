# 精确6f原路径：首次实际抢占请求恢复窗口；只诊断，不改调度/数值。
import functools as _native_functools
import json as _native_json
import os as _native_os
import time as _native_time
from pathlib import Path as _NativePath


def _native_event(event, **values):
    path = _native_os.environ.get('MINICPM_NATIVE_PROFILE_EVENTS')
    if path:
        with _NativePath(path).open('a', encoding='utf-8') as handle:
            handle.write(_native_json.dumps(dict(event=event, pid=_native_os.getpid(), monotonic_ns=_native_time.monotonic_ns(),
                source=__file__, **values)) + '\n')


def _native_cpu_request(self, rid):
    state = self.requests.get(rid)
    if state is None:
        return {'worker_cached_state_observed': False}
    return {
        'worker_cached_state_observed': True,
        'worker_computed_observed': int(state.num_computed_tokens),
        'prompt_length_observed': len(state.prompt_token_ids) if state.prompt_token_ids is not None else None,
        'output_length_observed': len(state.output_token_ids),
        'known_length_observed': int(state.num_tokens),
        'gpu_completed_floor': None,
        'limit': 'CPU cached state can lag or be optimistic; not GPU completion',
    }


def _native_payload_computed(output, rid):
    for row in output.scheduled_new_reqs:
        if row.req_id == rid:
            return int(row.num_computed_tokens), 'new_request_payload'
    cached = output.scheduled_cached_reqs
    for index, item in enumerate(cached.req_ids):
        if item == rid:
            return int(cached.num_computed_tokens[index]), 'cached_request_payload'
    return None, 'unobserved'


_native_event('module_loaded', kind='first_preempted_request_resume_up_to_eight_steps')
_native_execute_original = ModelRunnerFL.execute_model
_native_shutdown_original = ModelRunnerFL.shutdown


def _native_stop(self, complete, reason):
    # 下一execute入口才stop，包含上一个execute外部的sample_tokens。
    torch.cuda.synchronize()
    result = int(torch.cuda.cudart().cudaProfilerStop())
    self._native_profile_active = False
    self._native_profile_done = True
    _native_event('stop' if complete else 'shutdown_incomplete', result=result,
        reason=reason, target_request_id=self._native_preemption_target,
        executed_steps=self._native_resume_steps,
        decode_histogram_partial=getattr(self, '_native_decode_histogram', {}),
        limit='window kernels include all co-batched requests; not per-request causal cost')
    if result:
        raise RuntimeError('cudaProfilerStop failed: ' + str(result))


@_native_functools.wraps(_native_execute_original)
def _native_profile_execute(self, scheduler_output, *args, **kwargs):
    # CPU形状累计包括driver单请求smoke；无逐步I/O或设备读取。
    values = list(scheduler_output.num_scheduled_tokens.values())
    histogram = getattr(self, '_native_decode_histogram', None)
    if histogram is None:
        histogram = self._native_decode_histogram = {}
    if values and all(value == 1 for value in values):
        n = len(values)
        histogram[n] = histogram.get(n, 0) + 1
        total = getattr(self, '_native_decode_steps', 0) + 1
        self._native_decode_steps = total
        changed = getattr(self, '_native_last_decode_n', None) != n
        self._native_last_decode_n = n
        change_records = getattr(self, '_native_hist_change_records', 0)
        if total & (total - 1) == 0 or (changed and change_records < 64):
            self._native_hist_change_records = change_records + int(changed)
            try:
                _native_event('decode_histogram_partial', histogram=dict(histogram),
                    observed_pure_decode_steps=total, includes_driver_smoke=True,
                    workload_complete=False)
            except Exception:
                pass  # 稀疏CPU观察失败不改变原执行；不逐步flush。

    if getattr(self, '_native_profile_active', False) and self._native_stop_next:
        _native_stop(self, True, self._native_stop_next)
    if getattr(self, '_native_profile_done', False):
        return _native_execute_original(self, scheduler_output, *args, **kwargs)

    if not getattr(self, '_native_preemption_target', None) and scheduler_output.preempted_req_ids:
        # 只绑定首个真实preempt事件；ID只作关联，不作为优化策略。
        rid = sorted(scheduler_output.preempted_req_ids)[0]
        self._native_preemption_target = rid
        self._native_preempt_observation = _native_cpu_request(self, rid)
        self._native_preempt_request_object = self.requests.get(rid)
        _native_event('preempt_observed', target_request_id=rid,
            preempted_request_count=len(scheduler_output.preempted_req_ids),
            observation=self._native_preempt_observation,
            confirmed_floor_observed=False, future_or_device_values_read=False)

    rid = getattr(self, '_native_preemption_target', None)
    if rid and (rid in scheduler_output.finished_req_ids or
                (self._native_preempt_request_object is not None and
                 self.requests.get(rid) is not self._native_preempt_request_object)):
        if getattr(self, '_native_profile_active', False):
            _native_stop(self, True, 'target_lifecycle_ended_or_changed')
        else:
            self._native_profile_done = True
        _native_event('target_lifecycle_ended_or_changed', target_request_id=rid)
        return _native_execute_original(self, scheduler_output, *args, **kwargs)
    q = scheduler_output.num_scheduled_tokens.get(rid, 0) if rid else 0
    computed, source = _native_payload_computed(scheduler_output, rid) if rid else (None, 'unobserved')
    if (rid and q > 1 and computed is not None and not getattr(self, '_native_profile_active', False)):
        torch.cuda.synchronize()
        result = int(torch.cuda.cudart().cudaProfilerStart())
        if result:
            raise RuntimeError('cudaProfilerStart failed: ' + str(result))
        self._native_profile_active = True
        self._native_resume_steps = []
        self._native_stop_next = None
        _native_event('start', result=result, target_request_id=rid, target_q=q,
            payload_computed=computed, computed_source=source,
            preempt_observation=self._native_preempt_observation,
            confirmed_floor_observed=False, max_consecutive_execute_steps=8)

    # 原调用恰一次，且没有位于捕获原模型异常的except内。
    submit_start = _native_time.monotonic_ns() if getattr(self, '_native_profile_active', False) else None
    result = _native_execute_original(self, scheduler_output, *args, **kwargs)
    if getattr(self, '_native_profile_active', False):
        row = {'execute_submit_start_ns': submit_start,
               'execute_return_ns': _native_time.monotonic_ns(), 'N': len(values), 'M': sum(values), 'max_q': max(values, default=0),
               'scheduled_q': values, 'target_request_id': rid, 'target_q': q,
               'payload_computed': computed, 'computed_source': source,
               'optimistic_after_schedule': computed + q if computed is not None else None,
               'execute_returned': True, 'gpu_completed_at_return_not_asserted': True}
        self._native_resume_steps.append(row)
        target = self._native_preempt_observation.get('known_length_observed')
        if (q > 0 and computed is not None and target is not None and computed + q >= target):
            self._native_stop_next = 'reached_preempt_CPU_known_length_not_completion_floor'
        elif len(self._native_resume_steps) >= 8:
            self._native_stop_next = 'eight_consecutive_execute_limit'
    return result


@_native_functools.wraps(_native_shutdown_original)
def _native_profile_shutdown(self):
    try:
        if getattr(self, '_native_profile_active', False):
            _native_stop(self, False, 'shutdown_before_next_execute')
        _native_event('decode_histogram', histogram=getattr(self, '_native_decode_histogram', {}),
            includes_driver_smoke=True, workload_complete_not_asserted=True,
            limit='N counts only; graph padding and critical path not inferred')
    finally:
        if ModelRunnerFL.execute_model is _native_profile_execute:
            ModelRunnerFL.execute_model = _native_execute_original
        if ModelRunnerFL.shutdown is _native_profile_shutdown:
            ModelRunnerFL.shutdown = _native_shutdown_original
    return _native_shutdown_original(self)


ModelRunnerFL.execute_model = _native_profile_execute
ModelRunnerFL.shutdown = _native_profile_shutdown
print('BIV150_RESUME_NATIVE_ARMED diagnostics_only=1', flush=True)
