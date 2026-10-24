
    # sample_tokens在execute之外；只记录真实sample原返回后的新增命中。
    def _biv150_observe_async_bookkeeping(runner_cls):
        import functools
        import json
        import os
        original = runner_cls.sample_tokens
        state = {'disabled':False}

        def retire():
            state['disabled'] = True
            try:
                if runner_cls.sample_tokens is sample:
                    runner_cls.sample_tokens = original
            except Exception:
                pass

        @functools.wraps(original)
        def sample(self, *args, **kwargs):
            before = phase = None
            try:
                if not state['disabled'] and self.execute_model_state is not None:
                    phase = self.execute_model_state.scheduler_output
                    before = getattr(self, '_biv150_async_bookkeeping', {}).get('selected', 0)
            except Exception:
                retire()
            result = original(self, *args, **kwargs)
            try:
                after = getattr(self, '_biv150_async_bookkeeping', {}).get('selected', 0)
                if before is not None and after > before and self.input_batch.num_reqs >= 16:
                    print('BIV150_ASYNC_BOOKKEEPING_FIRST_ACTUAL_SAMPLE_SELECTED', json.dumps({
                        'pid':os.getpid(), 'actual_sample_tokens_returned':True,
                        'num_requests':self.input_batch.num_reqs,
                        'scheduled_tokens':phase.total_num_scheduled_tokens,
                        'selected_delta':after-before, 'selected_total':after,
                        'gpu_completed_at_return_not_asserted':True,
                        'whole_workload_coverage_not_asserted':True,
                    }, sort_keys=True), flush=True)
                    retire()
            except Exception:
                retire()
            return result
        runner_cls.sample_tokens = sample

    _biv150_observe_async_bookkeeping(ModelRunnerFL)
    print('BIV150_ASYNC_BOOKKEEPING_INSTALLED', flush=True)
