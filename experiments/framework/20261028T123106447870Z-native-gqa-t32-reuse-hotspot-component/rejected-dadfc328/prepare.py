"""继承T32完整九门；只换8KiB复用核/符号/身份，不新增测试矩阵。"""
from pathlib import Path
import difflib,json,shutil
H=Path(__file__).resolve().parent
BASE=H.parent/'native-gqa-t32-component-20261028'
SRC=H.parent/'native-gqa-t32-reuse-compile-20261028'
def save(n,t):(H/n).write_text(t,encoding='utf-8',newline='\n')
for n in ['base-source-manifest.json','dispatch_bootstrap.py','distributed_bootstrap.py','legacy_gate.py','monitor_gpu.sh','validate_block_table_candidate.py','validate_hidden_row_gather.py','validate_mixed_decode.py','fp_reference.py','macro1-build-receipt.json','source_identity.py']:
 shutil.copyfile(BASE/n,H/n)
shutil.copyfile(SRC/'native_gqa_t32_reuse.cu',H/'native_gqa_t32_reuse.cu')
entry=(BASE/'entry.py').read_text(encoding='utf-8').replace('-native-gqa-t32-','-native-gqa-t32-reuse-')
save('entry.py',entry)
bridge=(BASE/'bridge.cpp').read_text(encoding='utf-8').replace('t32','t32_reuse')
save('bridge.cpp',bridge)
w=(BASE/'worker.py').read_text(encoding='utf-8').replace('t32','t32_reuse').replace('f2975861','7db363d4').replace('逻辑T32','8KiB T32原位复用')
w=w.replace('T32 saves normalization/rescale groups, has no numerical/performance qualification.','T32 reuse8KiB keeps parent math and changes shared lifetime; all nine GPU gates rerun, no new performance qualification.')
w=w.replace('T32 compiler proof is separate; old double-slot negative retained','121814 reuse compiler proof is separate; old16KiB T32 negative retained')
save('worker.py',w)
for n in ['entry.py','worker.py','bridge.cpp']:
 save(n+'.diff',''.join(difflib.unified_diff((BASE/n).read_text(encoding='utf-8').splitlines(True),(H/n).read_text(encoding='utf-8').splitlines(True),fromfile='baa8-T32/'+n,tofile='T32-reuse/'+n)))
print('prepared',H)
