"""只迁新source身份；保留原owner服务/DB/清理行为。"""
from pathlib import Path
import shutil
import ast
import difflib
import hashlib
import json

root=Path(__file__).resolve().parent
old=root.parent/'rope-kv-model-verify'
candidate=root.parent/'rope-kv-model-candidate-v2'
for name in ('cache_gate.py','qualification.py','lifecycle.py','base-source-manifest.json'):
    shutil.copyfile(old/name,root/name)
for name in ('source-manifest.json','source-sha256.json'):
    shutil.copyfile(candidate/name,root/name)
before=(old/'verify_service.py').read_text(encoding='utf-8')
tree=json.loads((root/'source-manifest.json').read_bytes())['tree']
after=before.replace('57bb317de9d9040e3e52b27dc3b91ecc52eaae5e',tree)
after=after.replace("stamp + '-rope-kv-model-verify'","stamp + '-rope-kv-model-verify-v2'")
(root/'verify_service.py').write_bytes(after.encode('utf-8'))
normalized=after.replace(tree,'57bb317de9d9040e3e52b27dc3b91ecc52eaae5e')
normalized=normalized.replace("stamp + '-rope-kv-model-verify-v2'","stamp + '-rope-kv-model-verify'")
assert normalized==before
ast.parse(after)
(root/'owner.diff').write_text(''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),
    fromfile='v1/verify_service.py',tofile='v2/verify_service.py')),encoding='utf-8')
report={'passed':True,'owner_only_tree_and_run_name_changed':True,'tree':tree,'source_count':528,
        'owner_sha256':hashlib.sha256((root/'verify_service.py').read_bytes()).hexdigest(),
        'graph_gate_unchanged':(root/'graph_gate.py').read_bytes()==(old/'graph_gate.py').read_bytes(),
        'device_run':False,'original_failed_evidence_unchanged':True}
assert report['graph_gate_unchanged']
(root/'binding-cpu.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report))
