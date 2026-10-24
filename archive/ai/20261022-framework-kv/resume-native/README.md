# 当前6f：首次抢占后同请求恢复窗口诊断

只诊断，不改调度、KV、模型数值或服务参数，不启用任何旧swap／capacity／progress／pitched方法。复用114435的native owner与footer生命周期，基点固定完整412文件的干净6f100830；候选仍412文件，仅runner追加本footer。原32请求×16K输入／1024输出、c64、seed721201及SERVER保持，driver只允许本隔离诊断将原long case与native联合。

实际`preempted_req_ids`出现后绑定首个同rid及原worker CachedRequestState；只有该rid再次被实际payload调度q>1才start。其它新prefill不会触发。记录每步N／M／q／payload computed与原CPU缓存观察值，最多8次连续execute，或追上抢占前CPU known长度后，在下一execute入口才同步stop，包含上一调用外部的sample_tokens。窗口包含同批全部请求，不能将整窗kernel时间都归到受害请求。

`gpu_completed_floor=None`明确未知；CPU computed／known值可能滞后或乐观，不是设备完成证明，也不据此声称可避免多少已执行重算。原6f `_update_states`只移除未调度的InputBatch行，保requests对象；V2恢复经`_update_streaming_request`原地更新同对象，因此正常恢复不会被身份守卫误拒绝。终止／对象更换则停止关联，不跨请求生命周期。

纯decode N直方图只读CPU scheduled长度，按总步2的幂或N变化（最多64次变化记录）稀疏写partial snapshot，stop也带累计；不依赖shutdown必达。包括driver单请求smoke，不推完整覆盖或图padding耗时。没有逐步文件I/O、token值、future访问、额外KV查询；profiling同步仅本窗口起止，不作为性能分数。

部署五件：`resume_native_footer.py`、`prepare_resume_native.py`、`run_resume_native_screen.py`、`launch_resume_native.sh`、`base-source-sha256.json`。root唯一GPU owner运行：

```bash
bash <assets>/launch_resume_native.sh
```

冻结身份：footer `e13d46137f48f8bc6923676115c3f8b7dbf12e5fd4ec176721fad2b35fe0c26b`；preparer `671817d2dfffb267d092477420bb5309bbbc568baa4136b96ab4415d8492e0ed`；driver `c0e163524a0ebb4fa1dcf84b0f61103f4e8a4fa593394ba20c7aca30d967f79b`；launcher `579992c40eef6bb94943ec8cf61d78f72b1dc5c32321b2ca4ef6d012d351b749`；完整map `443555886596b94372076aa40e1b159f70475bca7f7a1e0fc901a69804566a34`；runner `01d7bc0106ee11c2643af2817a4ddb871d2b3a00a6b44beb2ae05da4b90c8a1a`。

语法／Bash-n及唯一新增触发CPU合同通过，receipt在`cpu-check.json`。首次fixture缺`__file__`在调用前失败，仅补fixture元信息后重过，原失败短记`cpu-initial-error.txt`保留；没有修改候选算法、执行实际profiler／GPU／SSH／整source复制或旧套件。hardware已读最终5资产新增差分，无本轮诊断阻断。尚无本诊断真实结果。
