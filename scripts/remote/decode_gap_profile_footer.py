# MINICPM_DECODE_GAP_DIAGNOSTIC_FOOTER_V1
"""Append only to the isolated retained runner; never use for a score.

Requires MINICPM_DECODE_GAP_RUN_DIR under ROOT/profiles/<unique run>.
Observe CPU wall time and cProfile for eight contiguous pure-decode steps
after skipping two eligible steps. No tensor reads, CUDA calls or RNG work
are added. Existing waits remain inside their original methods.
"""

import cProfile as _gap_cprofile
import functools as _gap_functools
import hashlib as _gap_hashlib
import io as _gap_io
import json as _gap_json
import os as _gap_os
from pathlib import Path as _GapPath
import pstats as _gap_pstats
import sys as _gap_sys
import threading as _gap_threading
import time as _gap_time


_GAP_ROOT = _GapPath("/workspace/experiments/minicpm-s2")
_GAP_BASE_SHA = "446f12c0653131c9a4f5ff7783e52e1a3882d2b20cdd50a6899d218a2dc0bd64"
_GAP_SOURCE_MARKER = b"# MINICPM_DECODE_GAP_DIAGNOSTIC_FOOTER_V1"
_GAP_STAGE_NAMES = (
    "_update_states", "_update_states_after_model_execute", "_prepare_inputs",
    "_prepare_input_ids", "_build_attention_metadata",
    "_determine_batch_execution_and_padding", "_preprocess", "_model_forward",
    "_sample", "_bookkeeping_sync",
)


def _gap_check_source(path, expected=_GAP_BASE_SHA):
    raw = _GapPath(path).read_bytes()
    position = raw.find(_GAP_SOURCE_MARKER)
    if position < 0:
        raise RuntimeError("diagnostic footer marker missing")
    prefix = raw[:position]
    # Allow the single separator newline used when appending this footer.
    if not any(_gap_hashlib.sha256(value).hexdigest() == expected
               for value in (prefix, prefix[:-1] if prefix.endswith(b"\n") else prefix)):
        raise RuntimeError("decode-gap footer requires the exact isolated retained runner")


def _gap_run_dir():
    value = _gap_os.environ.get("MINICPM_DECODE_GAP_RUN_DIR")
    if not value:
        raise RuntimeError("diagnostic footer needs MINICPM_DECODE_GAP_RUN_DIR; never use for score")
    path, profiles = _GapPath(value).resolve(), (_GAP_ROOT / "profiles").resolve()
    if path == profiles or not path.is_relative_to(profiles) or not path.is_dir():
        raise RuntimeError("decode-gap artifacts must be in an existing unique ROOT/profiles run")
    return path


def _gap_clock():
    return dict(wall_ns=_gap_time.perf_counter_ns(),
                process_cpu_ns=_gap_time.process_time_ns(),
                thread_cpu_ns=_gap_time.thread_time_ns(),
                thread_id=_gap_threading.get_ident())


class _GapState:
    def __init__(self, directory, *, skip=2, steps=8, min_reqs=16):
        self.directory, self.skip, self.steps, self.min_reqs = directory, skip, steps, min_reqs
        self.log = (directory / "host-walltime.jsonl").open("x", buffering=1, encoding="utf-8")
        self.active = self.done = False
        self.profile = None
        self.runner = None
        self.eligible_seen = self.step_id = self.selected = 0
        self.current = None
        self.shape_counts, self.window = {}, []
        self.emit("installed", kind="diagnostic_only_not_score", pid=_gap_os.getpid(),
                  source=__file__, skip=skip, steps=steps, min_reqs=min_reqs)

    def emit(self, event, **fields):
        self.log.write(_gap_json.dumps(dict(event=event, **_gap_clock(), **fields)) + "\n")

    def enter_execute(self, runner, scheduler_output):
        if self.done:
            return False
        scheduled = scheduler_output.num_scheduled_tokens
        shape = (len(scheduled), sum(scheduled.values()), max(scheduled.values(), default=0))
        eligible = shape[0] >= self.min_reqs and shape[1] == shape[0] and shape[2] == 1
        if self.active and (self.selected >= self.steps or not eligible or runner is not self.runner):
            self.stop("complete" if self.selected == self.steps else "interrupted")
            return False
        self.step_id += 1
        occurrence = self.shape_counts.get(shape, 0) + 1
        self.shape_counts[shape] = occurrence
        if eligible:
            self.eligible_seen += 1
        if not self.active and eligible and self.eligible_seen == self.skip + 1:
            if _gap_sys.getprofile() is not None:
                raise RuntimeError("decode-gap cProfile refuses to replace an existing profile hook")
            self.profile = _gap_cprofile.Profile()
            self.owner_thread = _gap_threading.get_ident()
            self.runner, self.started = runner, _gap_clock()
            self.active = True
            self.emit("window_start", shape=shape, step=self.step_id)
            self.profile.enable()
        if not self.active:
            return False
        self.selected += 1
        self.current = dict(step=self.step_id, shape=shape, shape_occurrence=occurrence,
                            first_shape_in_observed_requests=occurrence == 1)
        self.window.append(dict(self.current))
        return True

    def stop(self, reason):
        if not self.active:
            return
        self.profile.disable()
        self.active, self.done = False, True
        ended = _gap_clock()
        self.profile.dump_stats(str(self.directory / "host-window.pstats"))
        stream = _gap_io.StringIO()
        stats = _gap_pstats.Stats(self.profile, stream=stream)
        stats.sort_stats("cumulative").print_stats(80)
        (self.directory / "host-top-cumulative.txt").write_text(stream.getvalue(), encoding="utf-8")
        summary = dict(kind="diagnostic_only_not_score", reason=reason,
                       complete=reason == "complete" and self.selected == self.steps,
                       profiled_steps=self.selected, requested_steps=self.steps,
                       owner_thread=self.owner_thread, shapes=self.window,
                       wall_ns=ended["wall_ns"] - self.started["wall_ns"],
                       process_cpu_ns=ended["process_cpu_ns"] - self.started["process_cpu_ns"],
                       thread_cpu_ns=ended["thread_cpu_ns"] - self.started["thread_cpu_ns"],
                       limitations=["cProfile covers only the enabling thread; wall spans include thread IDs.",
                                    "Method durations can include existing GPU waits; no new waits were added.",
                                    "Nested spans and overlapping async output spans must not be summed.",
                                    "First shape means first during real execute_model calls, not process-cold JIT.",
                                    "Late get_output spans may arrive after this summary is written."])
        (self.directory / "host-window-summary.json").write_text(
            _gap_json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        self.emit("window_stop", reason=reason, profiled_steps=self.selected)
        self.log.flush()


def _gap_install(runner_class, output_class, state):
    """Install wrappers once; arguments and returned objects pass through."""
    if getattr(runner_class.execute_model, "_decode_gap_diagnostic", False):
        raise RuntimeError("decode-gap diagnostic footer already installed")
    original_execute = runner_class.execute_model
    original_sample = runner_class.sample_tokens
    original_output = output_class.get_output

    def stage_wrapper(name, original):
        @_gap_functools.wraps(original)
        def stage(self, *args, **kwargs):
            if not state.active or self is not state.runner:
                return original(self, *args, **kwargs)
            context = dict(state.current)
            state.emit("begin", stage=name, **context)
            status, extra = "ok", {}
            try:
                result = original(self, *args, **kwargs)
                if name == "_determine_batch_execution_and_padding":
                    mode, descriptor = result[:2]
                    extra = dict(graph_mode=str(mode), padded_tokens=descriptor.num_tokens,
                                 padded_reqs=descriptor.num_reqs)
                return result
            except BaseException as error:
                status = type(error).__name__
                raise
            finally:
                state.emit("end", stage=name, status=status, **context, **extra)
        return stage

    @_gap_functools.wraps(original_execute)
    def execute(self, scheduler_output, *args, **kwargs):
        selected = state.enter_execute(self, scheduler_output)
        if not selected:
            return original_execute(self, scheduler_output, *args, **kwargs)
        context = dict(state.current)
        state.emit("begin", stage="execute_model", **context)
        status, extra = "ok", {}
        try:
            result = original_execute(self, scheduler_output, *args, **kwargs)
            ephemeral = getattr(self, "execute_model_state", None)
            logits = getattr(ephemeral, "logits", None)
            extra["logits_shape"] = list(logits.shape) if logits is not None else None
            return result
        except BaseException as error:
            status = type(error).__name__
            raise
        finally:
            state.emit("end", stage="execute_model", status=status, **context, **extra)
            if status != "ok":
                state.stop("execute_error")

    @_gap_functools.wraps(original_sample)
    def sample(self, *args, **kwargs):
        if not state.active or self is not state.runner:
            return original_sample(self, *args, **kwargs)
        context = dict(state.current)
        state.emit("begin", stage="sample_tokens", **context)
        status = "ok"
        try:
            result = original_sample(self, *args, **kwargs)
            if isinstance(result, output_class):
                result._decode_gap_context = context
            return result
        except BaseException as error:
            status = type(error).__name__
            raise
        finally:
            state.emit("end", stage="sample_tokens", status=status, **context)
            if status != "ok":
                state.stop("sample_error")

    @_gap_functools.wraps(original_output)
    def get_output(self, *args, **kwargs):
        context = getattr(self, "_decode_gap_context", None)
        if context is None:
            return original_output(self, *args, **kwargs)
        state.emit("begin", stage="async_get_output", **context)
        status = "ok"
        try:
            return original_output(self, *args, **kwargs)
        except BaseException as error:
            status = type(error).__name__
            raise
        finally:
            state.emit("end", stage="async_get_output", status=status, **context)

    # Validate all names before any mutation, including the deferred correction.
    stages = [(name, getattr(runner_class, name)) for name in _GAP_STAGE_NAMES]
    for name, original in stages:
        setattr(runner_class, name, stage_wrapper(name, original))
    execute._decode_gap_diagnostic = True
    runner_class.execute_model = execute
    runner_class.sample_tokens = sample
    output_class.get_output = get_output
    print("MINICPM_DECODE_GAP_INSTALLED", flush=True)


if "ModelRunnerFL" in globals():
    _gap_check_source(__file__)
    _gap_state = _GapState(_gap_run_dir())
    _gap_install(ModelRunnerFL, AsyncGPUModelRunnerOutput, _gap_state)
