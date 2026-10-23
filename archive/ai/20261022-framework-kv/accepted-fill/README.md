# accepted-token GPU fill 候选

独立基于213134原422/runner cc442，不叠compute-order、computed-H2D或425。只在固定MiniCPM5-2B BF16、TP1、noSpec/nohybrid、单组42层FullAttentionSpec路径省2141的GPU fill；原CPU fill、buffer/shape、事件、位置/seq/slot、采样和所有算子不变。

`prepare_accepted_fill.py`固定完整map82514，生成仍422文件，仅runner与worker/protocol两处整runner锁变化。`files/`只是三路径镜像，不可当完整部署源；`files-prepare.json`含完整目标map、三个hunk与精确逆回结果。

```sh
python3 /path/to/assets/prepare_accepted_fill.py \
  --base /workspace/experiments/minicpm-s2/code/q-gqa-kv-swap-20261022T213134Z \
  --output /workspace/experiments/minicpm-s2/code/accepted-fill-<newUTC>
```

默认False；原KV初始化成功结束后一次冷核实际FullAttentionSpec源7e3c及模型/并行/无消费者条件。profiling或任何未知条件仍原fill；每次KV重初始化重置。原配置固定于Engine，未新增动态模式切换。热路径只有一个已缓存bool，无函数、hash、组遍历、新GPU字节或同步。

实际消费者：cc442:2168仅asyncspec correction；2484仅spec Mamba/GDN metadata；1577/1587/4315为hybrid相关。原_prepare_inputs的其他AST全部保持，CPU fill2140保留；dummy不调用此方法，graph replay前的真实prepare仍经过该判断。`BIV150_ACCEPTED_GPU_FILL_SKIP_ENABLED`仅证明冷scope，实际prepare可用同Engine既有`BIV150_CPU_METADATA_FIRST_SELECTED`佐证经过此处，不代表全程覆盖、GPU完成或数值验证。

仅做stdlib compile、完整map、精确逆回及AST增量检查（`static-check.json`）；未导入框架、运行mock/旧门、SSH或GPU。现成002156同名fill约3.5–4.8us但无法唯一归此语句，不宣称大收益；额外热bool成本尚无服务实测。下一设备验证由root安排，不能继承422准确率或将安装日志当收益。team_view_final_check已只读封口：冷scope/消费者闭包、缓存时序与三路径身份无当前短测阻断，未重复运行检查或设备。
