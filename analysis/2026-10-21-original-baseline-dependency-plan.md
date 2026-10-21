# 原13eb正式baseline的依赖恢复前置

2026-10-21，本文作者CPU-only设计/审计，无SSH或设备操作。**root已在12:26:07Z实际成功恢复54c→bab2，随后启动original官方baseline122607/runner166637；完整恢复原件现已独立审通过。** 实际record为`/workspace/experiments/minicpm-s2/dependency-restores/20261021T122607Z-original-baseline`，本地镜像及`independent-restore-review.json`在`experiments/dependency-restores/`同名目录：3备份+helper SHA、逐byte反变换、双idle及post均68/0/closed/无进程、manifest posthash bab2均核实。root12:29Z另读live installed与official manifest均bab2，benchmark167244/server166651、4K1/4且无BIVmarkers。禁止任何retained/C3 import或再次恢复操作。下方为此前设计模板，实际argv以本次record为准。

## 已证实的身份与影响范围

retained `biv150_runtime.py` SHA `a0c09c51826e0b9e0e5c4f320e68451359db44001d56fd68e1e78de8dda2c9b4` 的 `_patch_generic_attention()` 实际向installed `triton_unified_attention.py`写字节（line120），并删除同目录整个`__pycache__`（line123）。top-p只替换进程内函数；完整审该模块与retained patches没有第二个显式site-packages源码写入。普通Triton JIT/调优缓存仍可能由真实执行更新，不据此声称缓存相同。

该函数经retained `iluvatar.py`的`patch_biv150_minicpm_runtime()`在module-level line258调用，不限GPU ModelRunner初始化。因此原baseline期间，也不能在别的进程import retained平台模块而误写回全局依赖。

| 对象 | 实际字节数 | SHA256 |
|---|---:|---|
| retained installed Attention | 41796 | 54c495dcea404582a1526a96ae7e472965cbd03c8fa0931c71ef72223bf04e1f |
| a4独立保存`.orig` | **41176** | bab2c0b9f9a7793ca411796b48ebb4734433160e7e99eabf46ddb7f1c30cb6e0 |
| 仅反变换两block+末marker | 41176 | bab2c0b9f9a7793ca411796b48ebb4734433160e7e99eabf46ddb7f1c30cb6e0 |

独立抽取已哈希runtime的5个literal，不执行它；两tuned block和marker各唯一、marker必须是exact EOF suffix。结果不仅hash一致，且与a4 `.orig`**逐byte相同**。原回执41166是长度转录差，实际为41176。证据见同目录`2026-10-21-original-baseline-dependency-review.json`。

所有d60/SQL/C2/C3既有短pair本来均在retained54c基础上；这个发现本身不撤销它们，既有DB/KV/单轮等比较边界仍在。092944候选两档绝对官方结果仍有效。091033原13eb隔离source本身不足以代表原始环境；root现已先恢复bab2再启动完整原13eb对照，尚无完成结果或整体增益。

## 最小helper与边界

`scripts/remote/prepare_original_attention.py` SHA **8b3337e06e4dc083b5f99cafd785c6d5a49b64c86a10d721d47c76c304c8eda6**。默认inspect仅读文件/AST并打印JSON，本地archived字节与py_compile通过，framework owner全文独立终审无阻断。root已在Linux实际成功apply，本文作者现已独立复核完整record和脚本身份。本文作者没有运行apply/SSH；不追加suite或重复恢复。

显式`--apply`限定Linux和exact regular installed路径，取得现有`framework-device.lock`非阻塞独占锁，拒绝IPv4/6的9031连接、要求ixsmi恰一张卡/<=68MiB/0%且完整进程表含`No running processes found`。三份backup（当前源码、独立orig、a0c runtime）先fsync/readback；再复查idle+源码，写同目录新临时文件、保mode/uid/gid/fsync，原子`os.replace`，核bab2/逐byte及postflight。命令、before/after hash与尺寸、脚本副本、元数据、原始ixsmi与失败状态均在新record-dir。**不删除pycache，不触碰SQLite或Tritoncache，不改任何serve/benchmark参数。** 两版源长度不同也使CPython正常size校验拒绝旧`.pyc`，无需清整个pycache。

未知hash、非唯一block、非EOF marker、reference不匹配、busy锁/端口/设备、已有record-dir等都拒绝；已是bab2时不再当54c自动重写。失败不自动切回54c或删除证据，先读manifest与实际文件状态。此helper只做依赖准备，不启动模型或交接设备所有权。

## root执行流程设计（保留模板；本次实际执行见record）

本模板前置是唯一GPU任务结束、封存并实测完整postflight；root本次已完成恢复并进入官方baseline，**现在不得重跑模板**。此前设计用现有staging机制将exact helper及本地a4 `.orig`放到下列路径并记录hash，不从网络下载相似文件。以下runtime只作为AST输入，不可import：

```bash
set -euo pipefail
root=/workspace/experiments/minicpm-s2
task_stamp=$(date -u +%Y%m%dT%H%M%SZ)
source_dir="$root/code/official-base-20261021T091033Z"
attention=/usr/local/lib/python3.12/site-packages/vllm/v1/attention/ops/triton_unified_attention.py
runtime="$root/code/sql-mixed-20261021T080656Z/vllm_fl/patches/biv150_runtime.py"
reference="$root/reference/triton_unified_attention.bab2.orig"
record="$root/dependency-restores/${task_stamp}-before-original13eb"

test "$(cat "$source_dir/base-revision.txt")" = 13eb9be69ecc5b5ca4f79c44e9ee40081eaa1bf0
test ! -e "$source_dir/vllm_fl/patches/biv150_runtime.py"
if rg -n 'biv150_runtime|apply_biv150_runtime_patches|patch_biv150_minicpm_runtime' "$source_dir/vllm_fl"; then
    echo 'retained hook in supposed original source' >&2
    exit 2
fi
sha256sum "$root/scripts/prepare_original_attention.py" "$reference" "$runtime"
python3 "$root/scripts/prepare_original_attention.py" \
    --attention "$attention" --runtime "$runtime" --original-reference "$reference"
python3 "$root/scripts/prepare_original_attention.py" \
    --attention "$attention" --runtime "$runtime" --original-reference "$reference" \
    --apply --record-dir "$record"

python3 "$root/scripts/run_official_gate.py" \
    "$root/official/${task_stamp}-original13eb-official" \
    --source-dir "$source_dir" \
    --database /root/.flaggems/config_cache/TunedConfig_iluvatar_triton_3_6.db
```

root须把完整命令/launcher文件及source13eb全树指纹留档；source必须和已确认13eb原树相同，`base-revision.txt`只是附加provenance，不能替代全树身份。helper结束会释放锁；**official driver随后重新取得同一锁**。不要持helper锁直接嵌套启动原driver，否则第二次非阻塞flock会失败。root单卡串行所有权须覆盖这个交接空档，期间不调其他candidate/不import retained模块。

正式driver在锁内重新preflight并archive源码；验收必须确认archive中installed Attention=bab2、插件original13eb无retained。原13eb不会写回54c；启动后、原CSV封存后再只读hash核bab2。若root补充一次启动后/benchmark前expected-hash断言，应由root在其owned独立driver中做，保持原官方benchmark字节/argv不变；本agent未改driver。任何hash不符均不能当original baseline。原四轮/丢首轮/两case/tokens/DB before-after/清理仍按既有官方门，不另造替代协议。

以后再启retained候选，其a0c hook会按原实现写回54c；届时同样先确认设备空闲，再核新候选source/installed54c/完整manifest。无需提前为了“恢复候选”在baseline期间写回，不撤销当前运行source。

## 本次实际命令与已核执行记录

实际reference放在scripts目录，与上方旧模板的reference路径不同；真实argv如下，已由record保存并独立核对，**不得现在重跑**：

```text
/usr/local/bin/python3 /workspace/experiments/minicpm-s2/scripts/prepare_original_attention.py
  --attention /usr/local/lib/python3.12/site-packages/vllm/v1/attention/ops/triton_unified_attention.py
  --runtime /workspace/experiments/minicpm-s2/code/sql-mixed-20261021T080656Z/vllm_fl/patches/biv150_runtime.py
  --original-reference /workspace/experiments/minicpm-s2/scripts/triton_unified_attention.py.orig
  --apply
  --record-dir /workspace/experiments/minicpm-s2/dependency-restores/20261021T122607Z-original-baseline
```

record status=restored/mode=apply，before41796B/54c、after41176B/bab2、independent_reference_byte_equal=true。before.py、original-reference.py、retained-runtime.py各自SHA和helper8b33均正确；backup原件与本地a4早先`.orig`逐byte相同，独立AST反变换再次吻合。原权限mode33188/root:root已记录；preflight12:26:07.432605Z、pre_replace12:26:07.533529Z、post12:26:07.632596Z都68MiB/0%/9031closed且无进程。post installed hash=bab2来自已核exact helper的readback，live启动后bab2另由root只读确认；本文未用SSH重读live文件。
