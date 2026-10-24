from pathlib import Path
import base64
import hashlib
import subprocess
import sys

kind = sys.argv[1]
destination = '/workspace/experiments/minicpm-s2/scripts/'
source = '/workspace/experiments/minicpm-s2/code/cpu-combination-baseline-20261022T070004Z'
method_arg = ''
if kind == 'hot-v2':
    base = Path('tmp/hot-key-v2')
    assets = [('biv150_attention_key_recipe.py', 'biv150_attention_key_recipe_v2.py'), ('validate_attention_hot_launch.py', 'validate_attention_hot_launch_v2.py'), ('launch_attention_key_recipe_v2_gate.sh', 'launch_attention_key_recipe_v2_gate.sh')]
elif kind == 'c3-views':
    base = Path('tmp/next-c3-views')
    assets = [(s, s) for s in ('biv150_c3_view_reuse.py', 'validate_c3_views.py', 'launch_c3_views_gate.sh')]
elif kind in ('input-prep-combined', 'input-prep-combined-long'):
    base = Path('tmp/input-prep-timing-combined')
    assets = [(s, s) for s in ('prepare_input_prep_timing.py', 'biv150_input_prep_timing.py', 'launch_input_prep_timing.sh')]
    if kind.endswith('-long'):
        assets[-1] = ('launch_input_prep_timing_long.sh', 'launch_input_prep_timing_long.sh')
    destination += 'input-prep-timing-combined-20261022/'
    source = '/workspace/experiments/minicpm-s2/code/cpu-combination-combined-20261022T100830Z'
elif kind in ('small-hot', 'small-c3'):
    base = Path('tmp/small-input-gates')
    assets = [(s, s) for s in ('validate_small_hot_key.py', 'validate_small_c3_views.py', 'biv150_attention_key_recipe.py', 'biv150_c3_view_reuse.py', 'launch_small_input_gate.sh')]
    destination += 'small-input-gates-20261022/'
    method_arg = 'hot-key-v2 ' if kind == 'small-hot' else 'c3views '
elif kind == 'decode-gather':
    base = Path('tmp/next-decode-gather')
    assets = [(s, s) for s in ('validate_decode_gather.py', 'biv150_decode_cpu_gather.py', 'launch_decode_gather_gate.sh')]
    destination += 'next-decode-gather-20261022/'
    source = '/workspace/experiments/minicpm-s2/code/cpu-combination-combined-20261022T100830Z'
elif kind in ('c3-service-baseline', 'c3-service-candidate'):
    base = Path('tmp/c3views-service-v2') if kind.endswith('-candidate') else Path('tmp/c3views-service')
    assets = [(s, s) for s in ('prepare_c3views_service.py', 'biv150_c3_view_reuse.py', 'service_append.py', 'check_actual_selection.py', 'launch_c3views_service.sh')]
    destination += 'c3views-service-v2-20261022/' if kind.endswith('-candidate') else 'c3views-service-20261022/'
    source = '/workspace/experiments/minicpm-s2/code/cpu-combination-combined-20261022T100830Z'
    method_arg = 'baseline ' if kind.endswith('-baseline') else 'candidate '
elif kind == 'gather-service-candidate':
    base = Path('tmp/decode-gather-service')
    assets = [(s, s) for s in ('prepare_decode_gather_service.py', 'biv150_decode_cpu_gather.py', 'service_append.py', 'check_actual_selection.py', 'launch_decode_gather_service.sh')]
    destination += 'decode-gather-service-20261022/'
    source = '/workspace/experiments/minicpm-s2/code/cpu-combination-combined-20261022T100830Z'
    method_arg = 'candidate '
elif kind == 'current-mixed-native':
    base = Path('tmp/current-mixed-native')
    assets = [(s, s) for s in ('prepare_mixed_native.py', 'mixed_native_footer.py', 'run_mixed_native_screen.py', 'launch_current_mixed_native.sh')]
    destination += 'current-mixed-native-20261022/'
    source = ''
elif kind == 'resume-native':
    base = Path('tmp/framework-kv-next')
    assets = [(s, s) for s in ('base-source-sha256.json', 'prepare_resume_native.py', 'resume_native_footer.py', 'run_resume_native_screen.py', 'launch_resume_native.sh')]
    destination += 'resume-native-20261022/'
    source = ''
elif kind == 'prefill-w16':
    base = Path('tmp/next-prefill-w16')
    assets = [(s, s) for s in ('biv150_prefill_w16.py', 'validate_prefill_w16.py', 'launch_prefill_w16_gate.sh')]
    destination += 'prefill-w16-20261022/'
    source = '/workspace/experiments/minicpm-s2/code/cpu-combination-combined-20261022T100830Z'
elif kind in ('prefill-v-late-cache', 'prefill-v-late-cache-v2'):
    base = Path('tmp/next-v-late-cache-v2' if kind.endswith('-v2') else 'tmp/next-v-late-cache')
    assets = [(s, s) for s in ('biv150_prefill_v_late.py', 'cache_experiment.py', 'cache_bridge.c', 'validate_prefill_v_late_cache.py', 'launch_prefill_v_late_cache_gate.sh')]
    destination += 'prefill-v-late-cache-v2-20261022/' if kind.endswith('-v2') else 'prefill-v-late-cache-20261022/'
    source = '/workspace/experiments/minicpm-s2/code/cpu-combination-combined-20261022T100830Z'
elif kind == 'prefill-v-late':
    base = Path('tmp/next-prefill-v-late')
    assets = [(s, s) for s in ('biv150_prefill_v_late.py', 'validate_prefill_v_late.py', 'launch_prefill_v_late_gate.sh')]
    destination += 'prefill-v-late-20261022/'
    source = '/workspace/experiments/minicpm-s2/code/cpu-combination-combined-20261022T100830Z'
elif kind == 'q-service-baseline':
    base = Path('scripts/remote')
    assets = [('launch_cpu_combination_screen.sh', 'launch_cpu_combination_screen.sh')]
    destination += 'q-service-baseline-20261022/'
    source = ''
    method_arg = 'combined '
elif kind == 'q-hoist-accuracy':
    base = Path('tmp/q-hoist-service')
    assets = [('launch_q_hoist_accuracy.sh', 'launch_q_hoist_accuracy.sh')]
    destination += 'q-hoist-accuracy-20261022/'
    source = ''
elif kind == 'q-hoist-service':
    base = Path('tmp/q-hoist-service')
    assets = [(s, s) for s in ('biv150_q_fragment_service.py', 'service_append.py', 'base-source-sha256.json', 'prepare_q_hoist_service.py', 'launch_q_hoist_service.sh')]
    destination += 'q-hoist-service-20261022/'
    source = '/workspace/experiments/minicpm-s2/code/cpu-combination-combined-20261022T100830Z'
elif kind in ('q-fragment-hoist', 'q-fragment-hoist-4k'):
    base = Path('tmp/q-fragment-hoist-4k' if kind.endswith('-4k') else 'tmp/next-q-fragment-hoist')
    assets = [(s, s) for s in ('biv150_q_fragment_hoist.py', 'validate_q_fragment_hoist.py', 'launch_q_fragment_hoist_gate.sh')]
    destination += 'q-fragment-hoist-4k-20261022/' if kind.endswith('-4k') else 'q-fragment-hoist-20261022/'
    source = '/workspace/experiments/minicpm-s2/code/cpu-combination-combined-20261022T100830Z'
elif kind in ('q-shared-diagnostic', 'q-shared-diagnostic-v2'):
    base = Path('tmp/next-q-shared-diagnostic-v2' if kind.endswith('-v2') else 'tmp/next-q-shared-diagnostic')
    assets = [(s, s) for s in ('worker.py', 'fixture.py', 'asset-pins.json', 'diagnose_q_shared.py', 'launch_q_shared_diagnostic.sh')]
    destination += 'q-shared-diagnostic-v2-20261022/' if kind.endswith('-v2') else 'q-shared-diagnostic-20261022/'
    source = '/workspace/experiments/minicpm-s2/code/cpu-combination-combined-20261022T100830Z'
elif kind == 'last-layer-tail-v2':
    base = Path('tmp/next-last-layer-tail-v2')
    assets = [(s, s) for s in ('last_layer_tail.py', 'validate_last_layer_tail_v2.py', 'launch_last_layer_tail_v2_gate.py', 'launch_last_layer_tail_v2_gate.sh')]
    source = ''
elif kind == 'last-layer-tail':
    base = Path('tmp/next-last-layer-tail')
    assets = [(s, s) for s in ('last_layer_tail.py', 'validate_last_layer_tail.py', 'launch_last_layer_tail_gate.py', 'launch_last_layer_tail_gate.sh')]
    source = ''
elif kind == 'current-long-baseline':
    base = Path('tmp/long-current-baseline')
    assets = [('launch_current_long_baseline.sh', 'launch_current_long_baseline.sh')]
    destination += 'current-long-baseline-20261022/'
    method_arg = 'combined '
    source = ''
else:
    raise ValueError(kind)
lines = ['set -euo pipefail', "python3 - <<'PY'", 'import socket,subprocess', 'for family,addr in ((socket.AF_INET,("127.0.0.1",9031)),(socket.AF_INET6,("::1",9031))):', ' s=socket.socket(family); s.settimeout(1); code=s.connect_ex(addr); s.close(); assert code != 0, "9031 is busy"', 'print(subprocess.check_output(["/usr/local/corex/bin/ixsmi"],text=True))', 'PY']
lines += ['mkdir -p ' + destination]
for local, remote in assets:
    data = (base / local).read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    path = destination + remote
    lines += ["printf '%s' '" + base64.b64encode(data).decode() + "' | base64 -d > '" + path + "'", "printf '%s\\n' '" + sha + '  ' + path + "' | sha256sum -c -"]
launcher = destination + assets[-1][1]
lines += ['bash -n ' + launcher, 'bash ' + launcher + ' ' + method_arg + source]
args = ['ssh', '-F', 'NUL', '-i', 'C:/Users/Administrator/.ssh/id_ed25519_flagos_s2', '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=yes', '-o', 'ConnectTimeout=12', '-p', '2224', 'lab_inst_01M5D0Q7BQXT15N94DYK2V99EF@ssh.flagos.io', 'bash']
result = subprocess.run(args, input=('\n'.join(lines) + '\n').encode('utf-8'), capture_output=True, timeout=45)
sys.stdout.buffer.write(result.stdout)
sys.stderr.buffer.write(result.stderr)
raise SystemExit(result.returncode)
