# 独立C3重复view清理：最短接续

仅CPU准备，尚未部署或上卡，无性能／模型准确率结论。与hot-key完全独立。

- runtime `biv150_c3_view_reuse.py`：`ba085577f24684cb980cdd09c2978192ff9b8b3a70fa62aadc1cfd3efced61d4`。精确1219原forward AST只替两处unbind和unified的Q/out重复全段slice；数学／完整kwargs／scale.expand不变。复用原a129 scope和plan消费依赖，K/V输入不再作无用slice。未知条件原路，launch失败不重试，不允许叠JIT run候选。
- gate `validate_c3_views.py`：`e5eef652b72cc40afb0af98649811d0eb52dea7956f237354b2c0d646ca5f460`。沿现有两case：D29/P2019与Q2048，KV16K；保随机页／共享旧prefix／负padding slot／输出bits／整KV／RNG。新Q/out非默认流、原forward恢复与不支持output scale的原错误保留；只有P2019做32call预record ABBA及CPU/stat观察，纯prefill必须fallback。
- launcher `launch_c3_views_gate.sh`：`7418e0de944050b9d11eb6c510b140d33c4360675012c8c1d1d01bfc0f1906eb`。仅沿旧prefix launcher改两素材名／新run标签；原controller是唯一设备锁／子进程／monitor／清理owner。
- `check_c3_views_cpu.py`／`cpu-check.json`：唯一CPU合同已一次通过，无Torch导入；实际1219和a129调用对照的两个unified所有kwargs、视图offset／alias、非1scale来源／shape／stride相同，slice12→4、unbind2→1，原异常不重试、恢复原forward。它只用CPU描述符／记录器，**不证明GPU数学、实际factory身份、stream readiness或性能**。gate另已compile／纯CPU import／help通过。

依赖仍是原C2 e5f68a30、C3 a129361f、Attention54c495dc、helpers59d9d34b、backend1219c4d1、writer f18224e5。需原门四个辅助Python和monitor脚本，不能只上传这两文件猜依赖。root唯一SSH／GPU owner；由其选新UTC目录执行，先证真实selected_calls及所有检查，不命中／负收益照录，不扩大矩阵或混组合103/105。独立互审回执待补。

框架 owner 最终只读互审通过（未运行任何合同或设备）：实核 runtime ba085 相对首稿仅拒绝 JIT instance.run 叠加；两处 unbind/两处 Q-out 全段 slice 的 AST 逆回、原 C3 scope/plan wait/两次调用次序、完整 scale/kwargs 与异常不重试边界一致。gate e5eef 的新 Q/out 非默认流、P 真实 selected/纯 prefill fallback、非 1 scale 与原 output_block_scale 错误、32 ABBA 和 finally 恢复相互配套；launcher7418 仍由原 controller 唯一持锁/清理。CPU receipt 只证明描述符/调用合同；尚未上卡。按用户最新要求暂停新增实验准备，全部保持 tmp，不复制正式代码或当成已合并 PR。
