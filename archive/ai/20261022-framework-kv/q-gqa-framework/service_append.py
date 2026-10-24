
    # 独立服务接线：不改上方6f原代码；ctor结束后才安装私有JIT候选。
    def _biv150_bind_q_hoist_service(runner_cls):
        import functools
        import json
        import os
        import sys
        from pathlib import Path

        original_init = runner_cls.__init__
        original_execute = runner_cls.execute_model
        state = {"reported": False, "gqa_reported": False, "disabled": False, "execute_calls": 0}
        attribute = "_biv150_q_fragment_service_manager"

        def emit(marker, payload):
            try:
                print(marker, json.dumps(payload, sort_keys=True), flush=True)
            except Exception:
                pass

        def eligible(self):
            config = self.vllm_config
            model, parallel = config.model_config, config.parallel_config
            text = model.hf_text_config
            return (
                Path(str(model.model).rstrip("/\\")).name == "MiniCPM5-2B"
                and model.dtype == torch.bfloat16
                and (text.hidden_size, text.num_hidden_layers,
                     text.num_attention_heads, text.num_key_value_heads) == (2048, 42, 16, 2)
                and not model.is_encoder_decoder
                and all(getattr(parallel, name, None) == 1 for name in (
                    "tensor_parallel_size", "pipeline_parallel_size",
                    "decode_context_parallel_size", "data_parallel_size"))
                and not parallel.use_ubatching
                and config.speculative_config is None and config.lora_config is None
                and not config.cache_config.kv_sharing_fast_prefill
                and config.compilation_config.cudagraph_mode == CUDAGraphMode.FULL_DECODE_ONLY
            )

        @functools.wraps(original_init)
        def initialize(self, *args, **kwargs):
            # 原构造异常不捕获，也不在观察except内调用模型。
            result = original_init(self, *args, **kwargs)
            try:
                if eligible(self):
                    directory = Path(os.environ["BIV150_Q_FRAGMENT_SERVICE_ARTIFACT_DIR"])
                    if not directory.is_absolute():
                        raise RuntimeError("Q-hoist artifacts must use an absolute path")
                    from vllm_fl.patches.biv150_q_fragment_service import install
                    manager = install(artifact_dir=directory / str(os.getpid()))
                    setattr(self, attribute, manager)
                    emit("BIV150_Q_FRAGMENT_SERVICE_INSTALLED", {
                        "pid": os.getpid(), "installed": True,
                        "phase": "after_original_runner_constructor",
                        "actual_execute_selected": False,
                    })
            except Exception as error:
                # 资格或安装失败保原构造返回；后验不能据此认定安装/命中。
                emit("BIV150_Q_FRAGMENT_SERVICE_REJECTED", {
                    "pid": os.getpid(), "error_type": type(error).__name__,
                })
            return result

        def retire():
            state["disabled"] = True
            try:
                if runner_cls.execute_model is execute:
                    runner_cls.execute_model = original_execute
            except Exception:
                pass

        @functools.wraps(original_execute)
        def execute(self, scheduler_output, *args, **kwargs):
            before, manager, read_failed = None, None, False
            gqa_before = gqa_module = None
            try:
                if not state["disabled"]:
                    manager = getattr(self, attribute, None)
                    if manager is not None:
                        before = manager.snapshot()["selected_calls"]
                        gqa_module = sys.modules["vllm_fl.patches.biv150_gqa_decode"]
                        gqa_before = gqa_module.stats()["calls"]
                        state["execute_calls"] += 1
            except Exception:
                read_failed = True
            # 模型恰一次；原结果/异常/context不经过观察器的except。
            result = original_execute(self, scheduler_output, *args, **kwargs)
            try:
                if read_failed:
                    retire()
                elif before is not None:
                    after = manager.snapshot()["selected_calls"]
                    gqa_after = gqa_module.stats()["calls"]
                    q_delta, gqa_delta = after - before, gqa_after - gqa_before
                    if (self.input_batch.num_reqs >= 2
                            and scheduler_output.total_num_scheduled_tokens > 0):
                        common = {
                            "pid": os.getpid(), "actual_execute": True,
                            "complete_step_return": True,
                            "num_requests": self.input_batch.num_reqs,
                            "scheduled_tokens": scheduler_output.total_num_scheduled_tokens,
                            "execute_call": state["execute_calls"],
                            "selected_calls_in_execute": q_delta,
                            "selected_calls_total": after,
                            "gqa_calls_in_execute": gqa_delta,
                            "gqa_calls_total": gqa_after,
                            "gqa_python_count_excludes_graph_replay": True,
                            "not_gpu_completion_proof": True,
                            "not_all_steps_counted": True,
                        }
                        # Q与GQA可以在不同execute命中；两份原返回后证据齐才撤。
                        if q_delta > 0 and not state["reported"]:
                            print("BIV150_Q_FRAGMENT_SERVICE_FIRST_ACTUAL_EXECUTE_SELECTED",
                                  json.dumps(common, sort_keys=True), flush=True)
                            state["reported"] = True
                        if gqa_delta > 0 and not state["gqa_reported"]:
                            print("BIV150_Q_GQA_FIRST_ACTUAL_EXECUTE_SELECTED",
                                  json.dumps(common, sort_keys=True), flush=True)
                            state["gqa_reported"] = True
                        if state["reported"] and state["gqa_reported"]:
                            retire()
            except Exception:
                # 包括日志失败：只撤观察器，不吞模型异常、不重试模型。
                retire()
            return result

        runner_cls.__init__ = initialize
        runner_cls.execute_model = execute

    _biv150_bind_q_hoist_service(ModelRunnerFL)
