"""准备纯 CPU 资产；不导入 Torch，不接触设备。"""
import difflib
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent
old = ROOT.parent/'final-ffn-row-prune-logger-v2/run_component.py'
text = old.read_text(encoding='utf-8')
text = text.replace('末层FFN选行独立组件owner', '末层selected-Q独立组件owner')
text = text.replace("'exact_suffix.py'", "'query_candidate.py', 'source_identity.py', 'base-source-manifest.json'")
text = text.replace('def worker(run_dir):', 'def worker(run_dir, plugin_source, native_library):')
text = text.replace("'final_ffn_row_component'", "'final_query_row_component'")
text = text.replace("component.run(Path(run_dir), Path('/workspace/MiniCPM5-2B'))", "component.run(Path(run_dir), Path('/workspace/MiniCPM5-2B'), Path(plugin_source), Path(native_library))")
text = text.replace("    parser.add_argument('--worker'", "    parser.add_argument('--plugin-source', type=Path, required=True)\n    parser.add_argument('--native-library', type=Path, required=True)\n    parser.add_argument('--worker'")
text = text.replace('return worker(args.run_dir)', 'return worker(args.run_dir, args.plugin_source, args.native_library)')
text = text.replace("    common = module(common_path, 'final_ffn_common')", "    common = module(common_path, 'final_query_common')\n    identity = module(HERE / 'source_identity.py', 'selected_query_source_identity')")
text = text.replace("        state['preflight'] = common.preflight()", "        source = args.plugin_source.resolve(strict=True)\n        library = args.native_library.resolve(strict=True)\n        require(source.is_relative_to(ROOT / 'code') and not args.plugin_source.is_symlink(), '只接受独立code目录')\n        state['framework_source_before'] = identity.check(source, library)\n        state['plugin_source'] = str(source)\n        state['native_library'] = str(library)\n        state['preflight'] = common.preflight()")
text = text.replace("        env['PYTHONUNBUFFERED'] = '1'", "        env['PYTHONUNBUFFERED'] = '1'\n        env['PYTHONPATH'] = str(source)\n        env['VLLM_PLUGINS'] = 'fl'\n        env['BIV150_NATIVE_W8A8_LIBRARY'] = str(library)")
text = text.replace("'--run-dir', str(run), '--worker']", "'--run-dir', str(run), '--plugin-source', str(source), '--native-library', str(library), '--worker']")
text = text.replace("            state['source_unchanged'] = check_assets() == state.get('assets')", "            state['framework_source_after'] = identity.check(args.plugin_source, args.native_library)\n            state['framework_unchanged'] = state['framework_source_after'] == state.get('framework_source_before')\n            state['source_unchanged'] = check_assets() == state.get('assets') and state['framework_unchanged']")
(ROOT/'run_component.py').write_bytes(text.encode())
(ROOT/'owner.diff').write_bytes(''.join(difflib.unified_diff(old.read_text().splitlines(True),text.splitlines(True),fromfile='f72e/run_component.py',tofile='selected-Q/run_component.py')).encode())
shutil.copyfile(ROOT.parent/'main-0bf9-kv-candidate/base-source-manifest.json', ROOT/'base-source-manifest.json')
shutil.copyfile(ROOT.parent/'final-query-row-model-candidate/files/vllm_fl/patches/biv150_final_query_rows.py', ROOT/'query_candidate.py')
print('owner接线与固定526清单/7d40候选已复制；未执行设备代码')
