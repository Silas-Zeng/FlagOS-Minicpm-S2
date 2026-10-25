"""团队 main0915 全量603身份；未变native/图资格复用原main526。"""
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('team_main_prior_qualification', HERE/'base_qualification.py')
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
ROOT = base.ROOT
COMMIT = '0915f01d5efc2b31af65182ddb87e2d2f62bab0c'
TREE = '766b668b94e105ef9add5d3f7b6a22e45b7c201c'
read, sha, require = base.read, base.sha, base.require
assets, check_environment, check_reference = base.assets, base.check_environment, base.check_reference


def qualify(control, lifecycle, origin):
    old_identity, native, reference = base.qualify(control, lifecycle)
    _, old_blobs, _, _ = old_identity
    origin = Path(origin)
    require(origin.is_absolute() and not origin.is_symlink(), '团队源码须为实际绝对目录')
    origin = origin.resolve(strict=True)
    require(origin.is_relative_to(ROOT/'code') and origin != ROOT/'code', '团队源码不在实验code目录')
    manifest = read(HERE/'source-manifest.json')
    require(manifest['commit'] == COMMIT and manifest['tree'] == TREE and manifest['source_count'] == 603,
            '团队main603 manifest不符')
    blobs = {p:dict(mode=v['mode'],sha=v['git_sha']) for p,v in manifest['files'].items()}
    hashes = {p:v['sha256'] for p,v in manifest['files'].items()}
    require(len(blobs) == 603 and lifecycle.source_maps(origin) == (blobs,hashes), '团队main完整源码不符')
    changed = sorted(p for p in old_blobs.keys() | blobs.keys() if old_blobs.get(p) != blobs.get(p))
    require(changed and all(p.startswith(('tools/','docs/')) for p in changed),
            '团队main相对原受测版本存在生产代码差异，不能复用其模型路径资格')
    reference['files'][str(HERE/'source-manifest.json')] = sha(HERE/'source-manifest.json')
    reference.update(commit=COMMIT,tree=TREE,source_count=len(blobs),
                     original_qualification_commit=base.COMMIT,production_diff_empty=True,
                     docs_tools_changes=changed)
    return (origin,blobs,hashes,TREE), native, reference
