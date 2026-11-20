"""CPU 封包；复制既有 owner/数据/计时原件，不运行设备。"""
import ast
import hashlib
import json
from pathlib import Path
import shutil
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
OLD = ROOT / "experiments/framework/20261022T135941Z-q-fragment-hoist-gate/source"
copies = {name: OLD / name for name in ("validate_hidden_row_gather.py", "validate_mixed_decode.py",
    "validate_block_table_candidate.py", "monitor_gpu.sh")}
copies.update({"prototype.py": ROOT / "tmp/attention-affine-pages-20261025/prototype.py",
    "distributed_bootstrap.py": ROOT / "tmp/final-query-row-component-v3/distributed_bootstrap.py",
    "source_identity.py": ROOT / "tmp/final-query-row-component-v3/source_identity.py",
    "base-source-manifest.json": ROOT / "tmp/final-query-row-component-v3/base-source-manifest.json",
    "legacy_gate.py": ROOT / "tmp/next-q-fragment-hoist/validate_q_fragment_hoist.py",
    "base-source-sha256.json": ROOT / "tmp/main-0bf9-kv-staging/base-source-sha256.json"})
for name, source in copies.items():
    shutil.copyfile(source, HERE / name)
# 只提取成功 v3 已使用的函数和常量，不复制其组件框架。
v3 = (ROOT / "tmp/final-query-row-component-v3/component.py").read_text(encoding="utf-8")
selected = []
for node in ast.parse(v3).body:
    if (isinstance(node, ast.FunctionDef) and node.name in ("require", "sha", "enable_dispatch")) or (
        isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "INDEX_SHA" for t in node.targets)):
        selected.append(ast.get_source_segment(v3, node))
if len(selected) != 4:
    raise RuntimeError("成功 v3 dispatch 提取锚点变化")
helper = '"""原样提取成功 v3 的 FlagGems 实际注册函数；仅补必要 imports。"""\n'
helper += "import hashlib\nimport inspect\nimport os\nfrom pathlib import Path\n\n"
helper += "\n\n".join(selected) + "\n"
(HERE / "dispatch_bootstrap.py").write_text(helper, encoding="utf-8")
for file in HERE.glob("*.py"):
    ast.parse(file.read_text(encoding="utf-8"), filename=str(file))
names = [*copies, "entry.py", "worker.py", "prepare.py", "dispatch_bootstrap.py", "README.md"]
hashes = {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest() for name in names}
(HERE / "asset-pins.json").write_text(json.dumps(hashes, indent=2) + "\n", encoding="utf-8")
with tarfile.open(HERE / "entry.tar.gz", "w:gz") as archive:
    for name in [*names, "asset-pins.json"]:
        archive.add(HERE / name, arcname=name)
print(json.dumps(dict(status="CPU_SYNTAX_AND_PACKAGE_ONLY", files=len(names),
    archive_sha256=hashlib.sha256((HERE / "entry.tar.gz").read_bytes()).hexdigest())))
