
    # 仅观察真实 execute 内的新增 prepare_inputs 命中，不把 dummy 计数当成命中。
    def _biv150_observe_decode_gather_execute(runner_cls):
        import functools
        original_execute = runner_cls.execute_model
        observation = {"execute_calls": 0, "reported": False}

        @functools.wraps(original_execute)
        def execute_model(self, scheduler_output, *args, **kwargs):
            if observation["reported"]:
                return original_execute(self, scheduler_output, *args, **kwargs)
            before = getattr(self, "_biv150_decode_cpu_gather", {}).get("selected", 0)
            observation["execute_calls"] += 1
            result = original_execute(self, scheduler_output, *args, **kwargs)
            after = getattr(self, "_biv150_decode_cpu_gather", {}).get("selected", 0)
            num_reqs = self.input_batch.num_reqs
            # 原 driver 的单请求 smoke 不能冒充多请求短筛命中；只收紧观察，不改方法。
            if after > before and scheduler_output.total_num_scheduled_tokens > 0 and num_reqs >= 2:
                import json
                import os
                payload = {
                    "pid": os.getpid(),
                    "execute_call": observation["execute_calls"],
                    "selected_prepare_inputs_calls_in_execute": after - before,
                    "selected_prepare_inputs_calls_total": after,
                    "scheduled_tokens": scheduler_output.total_num_scheduled_tokens,
                    "num_requests": num_reqs,
                    "actual_execute": True,
                    "complete_step_return": True,
                    "not_all_steps_counted": True,
                }
                print("BIV150_DECODE_CPU_GATHER_FIRST_ACTUAL_EXECUTE_SELECTED",
                      json.dumps(payload, sort_keys=True), flush=True)
                observation["reported"] = True
                if runner_cls.execute_model is execute_model:
                    runner_cls.execute_model = original_execute
            return result

        runner_cls.execute_model = execute_model
        return {"installed": True, "scope": "strict pure decode; original GPU input preparation retained"}

    print("BIV150_DECODE_CPU_GATHER_INSTALLED",
          _biv150_observe_decode_gather_execute(ModelRunnerFL), flush=True)
