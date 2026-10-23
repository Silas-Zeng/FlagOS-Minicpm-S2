"""原bc51的独立辅助答案owner：仅新CLI约束和唯一负载命令变化。"""
import difflib
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ORIGINAL_SHA = 'bc51ac2d9daf90205bde362f8384b1ac34238e7be932e9a6df7fc618d7350be9'
CLIENT_SHA = '6dafbfbee4e3f91343ce28ecfefd55a48202e701d718184d8036556dff722c12'


def main():
    raw = (ROOT / 'scripts/remote/run_framework_screen.py').read_bytes()
    if hashlib.sha256(raw).hexdigest() != ORIGINAL_SHA:
        raise ValueError('原bc51变化')
    client = HERE / 'run_answer_load.py'
    if CLIENT_SHA is None or hashlib.sha256(client.read_bytes()).hexdigest() != CLIENT_SHA:
        raise ValueError('client未冻结')
    text, edits = raw.decode(), []
    def edit(old, new):
        nonlocal text
        if text.count(old) != 1:
            raise ValueError('原owner切口不唯一')
        text = text.replace(old, new, 1)
        edits.append((old, new))
    edit('    args = parser.parse_args()\n',
         "    parser.add_argument('--answer-requests', required=True, type=Path)\n"
         "    parser.add_argument('--answer-variant', required=True, choices=('baseline', 'candidate'))\n"
         '    args = parser.parse_args()\n'
         '    if not args.context_screen or args.native_profile or args.host_profile or args.smoke_only or args.decode_screen or args.context_long_screen:\n'
         "        parser.error('辅助答案门只接受原context-screen形状，不启profiler')\n"
         "    answer_client = Path(__file__).with_name('run_answer_load.py')\n"
         f"    if hashlib.sha256(answer_client.read_bytes()).hexdigest() != '{CLIENT_SHA}':\n"
         "        raise ValueError('辅助client身份变化')\n")
    edit("            command = ['bash', str(ROOT / 'scripts/run_diagnostic_load.sh'),\n"
         "                       str(run / label), label, str(length), str(output),\n"
         "                       str(concurrency), str(prompts), str(args.seed + offset)]\n",
         "            command = ['python3', str(answer_client), '--requests', str(args.answer_requests.resolve()),\n"
         "                       '--run-dir', str(run / label), '--variant', args.answer_variant,\n"
         "                       '--server-log', str(run / 'server.log')]\n")
    inverse = text
    for old, new in reversed(edits):
        if inverse.count(new) != 1:
            raise ValueError('owner逆回不唯一')
        inverse = inverse.replace(new, old, 1)
    if inverse.encode() != raw:
        raise ValueError('非精确逆回原owner')
    compile(text, 'run_answer_gate.py', 'exec')
    output = HERE / 'run_answer_gate.py'
    with output.open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(text)
    (HERE / 'owner.diff').write_text(''.join(difflib.unified_diff(raw.decode().splitlines(keepends=True),
        text.splitlines(keepends=True), fromfile='bc51/run_framework_screen.py', tofile='answer/run_answer_gate.py')), encoding='utf-8')
    (HERE / 'owner-check.json').write_text(json.dumps(dict(original_sha256=ORIGINAL_SHA,
        client_sha256=CLIENT_SHA, owner_sha256=hashlib.sha256(output.read_bytes()).hexdigest(),
        edits=len(edits), inverse_exact=True, compiled=True, executed=False), indent=2) + '\n')


if __name__ == '__main__':
    main()
