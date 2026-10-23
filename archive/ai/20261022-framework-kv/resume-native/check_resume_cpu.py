"""唯一新增触发合同：CPU stub，不执行torch/profiler或模型。"""
import ast
import hashlib
import json
import os
from pathlib import Path
import runpy
import sys
import tempfile
from types import SimpleNamespace as NS

HERE = Path(__file__).resolve().parent
checks, calls = [], []


def need(value, name):
    assert value, name
    checks.append(name)


class Runner:
    def __init__(self):
        self.requests = {"victim": NS(num_computed_tokens=16680, prompt_token_ids=[0]*16384,
                                     output_token_ids=[0]*320, num_tokens=16704)}
        self.calls = 0
        self.error = None
        self.result = object()

    def execute_model(self, output):
        self.calls += 1
        calls.append("forward")
        if self.error:
            raise self.error
        return self.result

    def shutdown(self):
        calls.append("shutdown")


def output(q, *, preempt=False, computed=None, rid="victim"):
    counts = {rid:q} if q else {"other": 2048}
    return NS(num_scheduled_tokens=counts, preempted_req_ids={"victim"} if preempt else set(),
              finished_req_ids=set(), scheduled_new_reqs=(
                  [NS(req_id=rid, num_computed_tokens=computed)] if computed is not None else []),
              scheduled_cached_reqs=NS(req_ids=[], num_computed_tokens=[]))


def main():
    old = os.environ.get("MINICPM_NATIVE_PROFILE_EVENTS")
    original_execute, original_shutdown = Runner.execute_model, Runner.shutdown
    fake_cuda = NS(synchronize=lambda:calls.append("sync"),
                   cudart=lambda:NS(cudaProfilerStart=lambda:(calls.append("start") or 0),
                                    cudaProfilerStop=lambda:(calls.append("stop") or 0)))
    try:
        with tempfile.TemporaryDirectory() as folder:
            event_path = Path(folder)/"events.jsonl"
            os.environ["MINICPM_NATIVE_PROFILE_EVENTS"] = str(event_path)
            raw = (HERE/"resume_native_footer.py").read_bytes()
            exec(compile(raw, "resume-footer-stub", "exec"),
                 {"ModelRunnerFL":Runner, "torch":NS(cuda=fake_cuda), "__file__":str(HERE/"resume_native_footer.py")})
            runner = Runner()
            def run(data):
                need(runner.execute_model(data) is runner.result, "original_result_identity")
                calls.append("sampler")
            run(output(2048,rid="other",computed=0))
            run(output(0,preempt=True))
            run(output(2048,rid="other",computed=0))
            need("start" not in calls, "other_request_prefill_cannot_trigger")
            run(output(1,computed=2944))
            need("start" not in calls, "same_request_singleton_cannot_trigger")
            start_calls=runner.calls
            for index in range(7):
                run(output(2048,computed=2944+2048*index))
            need(calls.count("start")==1 and calls.count("stop")==0,
                 "one_start_and_no_stop_before_final_sampler")
            run(output(1,computed=17280))
            need(calls.count("stop")==1 and calls[calls.index("stop")-2]=="sampler"
                 and calls[calls.index("stop")+1]=="forward", "next_entry_stop_contains_sampler")
            need(runner.calls==start_calls+8, "one_original_call_per_window_and_next_entry")
            runner.shutdown()
            need(Runner.execute_model is original_execute and Runner.shutdown is original_shutdown,
                 "original_bindings_restored_at_shutdown")
            events=[json.loads(line) for line in event_path.read_text().splitlines()]
            start=next(e for e in events if e['event']=='start')
            stop=next(e for e in events if e['event']=='stop')
            need(start['target_request_id']=='victim' and start['target_q']==2048
                 and len(stop['executed_steps'])==7, "bound_actual_victim_window_dynamic_length")
            need(start['preempt_observation']['gpu_completed_floor'] is None
                 and start['confirmed_floor_observed'] is False, "no_cpu_optimism_as_completed_floor")
            need(any(e['event']=='decode_histogram_partial' for e in events),
                 "histogram_available_before_shutdown")
            # 原错误不由观察except捕获，不重复执行。
            exec(compile(raw, "resume-footer-stub", "exec"),
                 {"ModelRunnerFL":Runner, "torch":NS(cuda=fake_cuda), "__file__":str(HERE/"resume_native_footer.py")})
            runner=Runner();error=RuntimeError("original error");runner.error=error
            try:
                runner.execute_model(output(1,computed=0))
            except RuntimeError as caught:
                need(caught is error and caught.__context__ is None and runner.calls==1,
                     "original_exception_identity_context_no_retry")
            else:
                raise AssertionError("original error swallowed")
            Runner.execute_model,Runner.shutdown=original_execute,original_shutdown
            base=Path('docs/pr-preparation/combination-artifacts/resolved/vllm_fl/worker/model_runner.py').read_bytes()
            prep=runpy.run_path(str(HERE/'prepare_resume_native.py'))
            changed=prep['transform'](base)
            need(changed[:len(base)]==base, "exact_6f_prefix_preserved")
            a=ast.parse(Path('tmp/current-mixed-native/run_mixed_native_screen.py').read_bytes())
            b=ast.parse((HERE/'run_resume_native_screen.py').read_bytes())
            def assignments(tree,name):
                return [ast.dump(n.value,include_attributes=False) for n in ast.walk(tree)
                        if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in n.targets)]
            need(assignments(a,'SERVER')==assignments(b,'SERVER') and
                 assignments(a,'cases')==assignments(b,'cases'), "original_SERVER_and_workload_cases_unchanged")
            need(not any(x in sys.modules for x in ('torch','triton','vllm')), "no_framework_or_device_import")
            receipt={'passed':True,'checks':checks,
                'footer_sha256':hashlib.sha256(raw).hexdigest(),
                'candidate_runner_sha256':hashlib.sha256(changed).hexdigest(),
                'limit':'CPU stub only; no profiler/GPU, no completion-floor proof, no full source copy'}
            (HERE/'cpu-check.json').write_text(json.dumps(receipt,indent=2)+'\n')
            print(json.dumps(receipt))
    finally:
        Runner.execute_model,Runner.shutdown=original_execute,original_shutdown
        if old is None:os.environ.pop('MINICPM_NATIVE_PROFILE_EVENTS',None)
        else:os.environ['MINICPM_NATIVE_PROFILE_EVENTS']=old


if __name__=='__main__':main()
