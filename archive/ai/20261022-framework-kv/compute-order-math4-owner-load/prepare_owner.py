"""原bc51两切口：独立math4 CLI与唯一load命令；原SERVER/owner/清理逐字节保留。"""
import difflib
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ORIGINAL_SHA = 'bc51ac2d9daf90205bde362f8384b1ac34238e7be932e9a6df7fc618d7350be9'
LOAD_SHA = '03a0c9027063b239dad66b8d15d87bb867d6e93a1ccf0286882284140d9030e6'


def main():
    raw = (ROOT / 'scripts/remote/run_framework_screen.py').read_bytes()
    load = HERE / 'run_math4_load.py'
    if hashlib.sha256(raw).hexdigest() != ORIGINAL_SHA or LOAD_SHA is None or hashlib.sha256(load.read_bytes()).hexdigest() != LOAD_SHA:
        raise ValueError('原bc51或math4 load尚未冻结/变化')
    text, edits = raw.decode(), []
    def edit(old, new):
        nonlocal text
        if text.count(old) != 1:
            raise ValueError('原owner切口不唯一')
        text = text.replace(old, new, 1)
        edits.append((old, new))
    edit('    args = parser.parse_args()\n',
        "    parser.add_argument('--math4-capture', required=True, type=Path)\n"
        "    parser.add_argument('--math4-capture-output', required=True, type=Path)\n"
        '    args = parser.parse_args()\n'
        '    if not args.context_screen or args.native_profile or args.host_profile or args.smoke_only or args.decode_screen or args.context_long_screen or args.seed != 721201:\n'
        "        parser.error('math4只接受原context-screen与seed721201，不启profiler')\n"
        "    math4_load = Path(__file__).with_name('run_math4_load.py')\n"
        f"    if hashlib.sha256(math4_load.read_bytes()).hexdigest() != '{LOAD_SHA}':\n"
        "        raise ValueError('math4负载身份变化')\n")
    edit("            command = ['bash', str(ROOT / 'scripts/run_diagnostic_load.sh'),\n"
        "                       str(run / label), label, str(length), str(output),\n"
        "                       str(concurrency), str(prompts), str(args.seed + offset)]\n",
        "            command = ['python3', str(math4_load), '--run-dir', str(run / label),\n"
        "                       '--capture', str(args.math4_capture.resolve()),\n"
        "                       '--capture-output', str(args.math4_capture_output.resolve()),\n"
        "                       '--seed', str(args.seed)]\n")
    inverse = text
    for old, new in reversed(edits):
        if inverse.count(new) != 1:
            raise ValueError('owner逆回不唯一')
        inverse = inverse.replace(new, old, 1)
    if inverse.encode() != raw:
        raise ValueError('非精确逆回原bc51')
    compile(text, 'run_math4_gate.py', 'exec')
    output = HERE / 'run_math4_gate.py'
    with output.open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(text)
    (HERE / 'owner.diff').write_text(''.join(difflib.unified_diff(raw.decode().splitlines(keepends=True),
        text.splitlines(keepends=True), fromfile='bc51/run_framework_screen.py', tofile='math4/run_math4_gate.py')), encoding='utf-8')
    (HERE / 'owner-check.json').write_text(json.dumps(dict(original_sha256=ORIGINAL_SHA,
        load_sha256=LOAD_SHA, owner_sha256=hashlib.sha256(output.read_bytes()).hexdigest(),
        edits=len(edits), inverse_exact=True, syntax_compiled=True, owner_executed=False), indent=2) + '\n')


if __name__ == '__main__':
    main()
