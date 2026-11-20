"""仅复核已回收的选定输出，CPU FP64；不运行 GPU 或修改原件。"""
from pathlib import Path
import json
import os
os.environ.setdefault('KMP_DUPLICATE_LIB_OK', 'TRUE')
import torch

root = Path.cwd()
run = '20261030T011120000584Z-q32-key-scale-component'
raw = root / 'archive/q32-key-scale-20261030/component-011120/cpu-probes' / run
summary = json.loads((raw / 'summary.json').read_text())
rows = []
for path in sorted((raw / 'numerical').glob('*.pt')):
    data = torch.load(path, map_location='cpu', weights_only=True)
    assert data['selected_only']
    a, b = (data['outputs'][arm] for arm in ['A', 'B'])
    diff = (a.double() - b.double()).abs()
    limit = .005 + .005 * a.double().abs()
    rows.append({'file': path.name, 'selected_only': True, 'elements': a.numel(),
                 'bitwise_equal': torch.equal(a.view(torch.uint8), b.view(torch.uint8)),
                 'nonzero_difference_elements': int((diff > 0).sum()),
                 'max_abs_difference_cpu': float(diff.max()),
                 'pointwise_violations_cpu': int((diff > limit).sum())})
out = {'run': run, 'status': 'selected_cpu_posthoc_only', 'rows': rows,
       'full_output_gate': '待确认；本轮device FP64统计与bitwise/CPU选定输出存在矛盾，不授全量数值资格。',
       'gpu_run_repeated': False, 'original_evidence_modified': False}
(Path(__file__).parent / 'selected-cpu-check.json').write_text(json.dumps(out, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(json.dumps(out, ensure_ascii=False))
