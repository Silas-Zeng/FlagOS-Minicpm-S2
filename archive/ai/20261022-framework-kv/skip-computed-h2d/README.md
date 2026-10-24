# 省去 metadata 成功分支的 computed H2D

仅 CPU 准备，当前未上卡／未有净收益或新准确率。原 QGQA414（runnercc442）与全部 0e961/1bb85/SQL/C2/C3/Q/GQA helper 保留；只改 `_prepare_inputs` 三小段，不加新热 helper/guard。原 async-spec 条件与更新 body 完整保留，else 只标原 copy 待办，metadata helper False 才按待办执行原 H2D，再接原 GPU 算术。同步 event、固定 GPU buffer、accepted fill、原采样／调度参数均不变；helper 或 copy 抛错不捕获重试。

- `prepare_skip_computed_h2d.py`：23d833a1bd3f4155652a2457b19bdaedf29b918de488e18e5b986b2cb5e08427。
- `candidate_model_runner.py`：97f41ac455cad0db7c8ddfd2b9809e77326b6472285cb14e56ce486f2f0f7443。
- 完整输入 map bf69d06d，输出 map425245ed，均414项且仅runner差异。runner.diff、static-check.json保存精确逆回／AST检查。未改旧冻结树或宽放runtime白名单。
- 现有guard接受范围核对：metadata只锁InputBatch/utils；async按scope/tensor合同；SQL/C2/C3/GQA/Q锁各自SQL/Attention/backend/helper/compiler来源，未锁runnerSHA；全部原字节。旧KVworker的e155锁本来不适用cc442，不启用或放宽它。

**最短设备门已准备**：`validate_skip_computed_h2d.py` 461676a0b6517e5c832d315fbcfe18aff059ad0bd23cf14e51da7f34cfe4af42，小fork已用b1240720 actual-method门，保原5CASE／真实CpuGpuBuffer与BlockTable／单owner清理。双方加载原0e961+1bb85；成功时baseline computed等CPU当前值，candidate computed保持-113毒值，真正的positions/seq/slots/input/logits/CPU镜像逐项一致。下一次以原async-spec拒绝scope（valid count None，不模拟spec校正）使真实helper False，全方法原copy恢复computed；再恢复成功scope／重毒走原4step event+固定地址graph，追加input IDs消费。原32calls ABBA host-wall含最终drain保留为描述，不作为性能pass门，窗口须metadata delta32。只有两项必要fixture字段增补，无新模型模拟器。

CPU仅compile／runpy import／help、原公共函数与5CASE AST核对通过，未导入Torch/Triton/vLLM。门自身复用原控制器锁／300s／PID／monitor／清理；官方任务结束且root实核空闲后才允许由root调用。示意CLI（本页未执行）：

```bash
root=/workspace/experiments/minicpm-s2
base=$root/code/q-gqa-service-candidate-20261022T184141Z
assets=$root/scripts/skip-computed-h2d-20261022
# 运行目录必须换成新的UTC，沿旧helper owner，只运行一次
PYTHONPATH="$base:$root/scripts" python3 "$assets/validate_skip_computed_h2d.py"   --run-dir "$root/framework/<新UTC>-skip-computed-h2d-method"   --runner-path "$base/vllm_fl/worker/model_runner.py"   --runtime-path "$base/vllm_fl/patches/biv150_cpu_metadata.py"   --async-runtime-path "$base/vllm_fl/patches/biv150_async_token_update.py"   --transform-path "$assets/prepare_skip_computed_h2d.py"
```

部署source时仅需preparer＋base-source-sha256.json：`python3 prepare_skip_computed_h2d.py --base-dir <原414> --output-dir <全新code目录>`，源树外receipt保存完整before/after map并后验基点不变。不在此门执行prepare整copy。通过后可沿原bc51 4K/128out/64/c64同seed服务candidate/base，Qartifact ENV与两路真实execute marker保留；DB/KV失配则不可归因。方法门不运行模型权重／Attention、未覆盖实际async-spec校正或模型accuracy，不继承为这些边界的证明。

root增量审修正：fallback只更新computed前32行，所以只核这32行等当前CPU；原先前5case使基线尾部有历史值、候选尾部留毒，不比较或填平无消费者尾部。初稿d5f22ea4原件保留，最后只此一处与pin更新，syntax过未重跑旧门。

root已补`launch_skip_computed_h2d.sh`：启动前检查原414全map、冻结gate/preparer/owner、双栈端口和严格空卡，再以`PYTHONPATH=$base:$root/scripts`调用原单owner控制器。本地`tmp/deploy_short_gate.py skip-computed-h2d`负责传输与启动，但目前未执行；必须先等官方202736结束并完成清理。失败保留原目录，不改正在运行的官方源码。

跨owner最终只读审：hardware核preparer23d833／runner97f41／gate461676及原CPU／GPU消费者、pending分支、[:32]恢复和固定graph消费者，无新增设备门阻断；未重跑旧fixture／设备。三件冻结，root仍唯一设备owner。
