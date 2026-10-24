"""真实服务输入准备的累计 CPU 计时；只用于诊断，不增加设备同步。"""
import atexit
import json
import os
from pathlib import Path


class InputPrepTiming:
    def __init__(self):
        directory = os.environ.get("BIV150_INPUT_PREP_TIMING_OUTPUT_DIR")
        if not directory:
            raise RuntimeError("诊断源码需要 BIV150_INPUT_PREP_TIMING_OUTPUT_DIR")
        self.path = Path(directory) / ("input-prep-timing-%d.json" % os.getpid())
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.data = {
            "kind": "input_preparation_cost_diagnostic_not_performance",
            "pid": os.getpid(), "calls": 0, "failed_waits": 0,
            "wait_total_ns": 0, "wait_max_ns": 0,
            "preprocess_total_ns": 0, "preprocess_max_ns": 0,
            "preprocess_includes_wait_and_existing_event_record": True,
            "snapshot_not_guaranteed_to_cover_all_requests": True,
        }
        self.next_snapshot = 64
        self.write_error = None
        atexit.register(self.flush, True)

    def add(self, wait_ns, preprocess_ns, failed_wait=False):
        d = self.data
        d["calls"] += 1
        d["failed_waits"] += int(failed_wait)
        d["wait_total_ns"] += wait_ns
        d["wait_max_ns"] = max(d["wait_max_ns"], wait_ns)
        d["preprocess_total_ns"] += preprocess_ns
        d["preprocess_max_ns"] = max(d["preprocess_max_ns"], preprocess_ns)
        if d["calls"] == self.next_snapshot:
            self.flush(False)
            self.next_snapshot *= 2

    def flush(self, final=False):
        try:
            data = dict(self.data, normal_exit_final=bool(final),
                        previous_write_error=self.write_error)
            temporary = self.path.with_suffix(".tmp")
            temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                                 encoding="utf-8")
            os.replace(temporary, self.path)
        except Exception as exc:
            # 诊断输出失败不覆盖模型原异常；下一快照/正常退出保留错误。
            self.write_error = type(exc).__name__ + ": " + str(exc)


def get_recorder(runner):
    recorder = getattr(runner, "_biv150_input_prep_timing", None)
    if recorder is None:
        recorder = InputPrepTiming()
        runner._biv150_input_prep_timing = recorder
    return recorder
