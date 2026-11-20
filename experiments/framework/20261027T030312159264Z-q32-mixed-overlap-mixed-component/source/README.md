# main241 Q32 与自然混合 GQA 双流：唯一组件

只验证 D63/P1985、KV4096、64请求/总2048token 的一个混合层。真实 main241 原 C3 自然切片；当前 D63 的 GQA 自然为 S4，不套旧 N64/S2。A 原串行、B 原字节 93c 双流，两臂原 writer＋原 GQA producer/reducer＋原 Q32 prefill 全部计入；没有新数学、kernel、KV布局、权重或生产补丁。

旧 D29/P2019/KV16K 双流64calls仅 wall省0.349%/Event慢0.040%，未确认收益。重判仅因当前Q32 block1024/shared64KiB 与 GQA block64/shared8KiB 的资源组合不同；不声称实际共驻。实际Q32 Manager返回、优化hash/grid与GQA实际grid/归约均先捕获，随后完全还原observer再计时。

复用93c的ready→side decode+reducer→current join与tensor record_stream/强引用生命周期，每call原事件和collect成本均保留。两次换Q中间无host同步，主stream立即clone消费；整输出逐位、padding、finite、整KV不变、输入/RNG、同步后pending0全部硬门。随后只有一次完整32calls ABBA；普通timing events预热但运行内fork/join事件不移出，不用Graph隐藏Python成本。Event/wall同时报告，无一致净正信号停止；不扫形状/优先级/参数。

入口复用已审main241组件owner，只有case和runlabel差分，765源码/native14f/共同DB恢复/唯一锁/9031/设备preflight与自有PID清理不变。

```bash
python3 entry.py --source-dir <main241精确765源码> --native-library <native14f.so> --case mixed
```

这不是模型吞吐或准确率结果，不证明42层生产强引用峰值或自动获得部署资格。CPU准备不SSH/GPU；由root统一串行启动。
