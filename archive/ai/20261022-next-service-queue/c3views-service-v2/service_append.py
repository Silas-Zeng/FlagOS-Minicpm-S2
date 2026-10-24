

# 下列仅为真实服务接线；上方已测 Manager 实现逐字节保留。
_SERVICE = None
_FIRST_EXECUTE_MARKER = "BIV150_C3_VIEWS_FIRST_ACTUAL_EXECUTE_SELECTED"


def _bind_first_actual_execute(runner_cls, manager):
    """只观察真实 execute_model 返回后的累计增量，首次命中后撤掉观察包装。"""
    original_execute = runner_cls.execute_model
    state = {"observed_execute_calls": 0, "reported": False, "disabled": False}

    @functools.wraps(original_execute)
    def execute_model(self, scheduler_output, *args, **kwargs):
        before, observation_failed = None, False
        try:
            if not state["reported"] and not state["disabled"]:
                before = manager.counts["selected_calls"]
                state["observed_execute_calls"] += 1
        except Exception:
            observation_failed = True
        # 模型执行只发生一次，且位于观察异常处理之外；原异常直接传播。
        result = original_execute(self, scheduler_output, *args, **kwargs)
        try:
            if observation_failed:
                state["disabled"] = True
            elif before is not None:
                delta = manager.counts["selected_calls"] - before
                if delta > 0 and scheduler_output.total_num_scheduled_tokens > 0:
                    import json
                    import os
                    payload = {
                        "pid": os.getpid(),
                        "execute_call": state["observed_execute_calls"],
                        "selected_forward_calls_in_execute": delta,
                        "selected_forward_calls_total": manager.counts["selected_calls"],
                        "scheduled_tokens": scheduler_output.total_num_scheduled_tokens,
                        "actual_execute": True,
                        "complete_step_return": True,
                        "not_all_steps_counted": True,
                    }
                    print(_FIRST_EXECUTE_MARKER, json.dumps(payload, sort_keys=True), flush=True)
                    state["reported"] = True
        except Exception:
            # 计数、序列化或日志失败只停止观察，不改变成功结果或重试模型。
            state["disabled"] = True
        try:
            if state["reported"] or state["disabled"]:
                # 不覆盖外部随后安装的包装；缓存的 bound method 也不重试日志。
                if runner_cls.execute_model is execute_model:
                    runner_cls.execute_model = original_execute
        except Exception:
            pass
        return result

    runner_cls.execute_model = execute_model
    return state


def install_service(runner_cls):
    """在 SQL→C2→C3 之后安装；无设备操作，不改变服务参数或执行顺序。"""
    global _SERVICE
    if _SERVICE is not None:
        if _SERVICE["runner_cls"] is not runner_cls:
            raise RuntimeError("C3views 已绑定其他 runner")
        return {"installed": True, "scope": "original C3 eligible mixed BF16 MiniCPM only"}
    import importlib
    backend = importlib.import_module("vllm.v1.attention.backends.triton_attn")
    attention = importlib.import_module("vllm.v1.attention.ops.triton_unified_attention")
    helpers = importlib.import_module("vllm.v1.attention.ops.triton_attention_helpers")
    manager = create(attention, helpers, backend)
    manager.install()
    try:
        observation = _bind_first_actual_execute(runner_cls, manager)
    except BaseException:
        manager.restore()
        raise
    _SERVICE = {"manager": manager, "runner_cls": runner_cls, "observation": observation}
    return {"installed": True, "scope": "original C3 eligible mixed BF16 MiniCPM only"}
