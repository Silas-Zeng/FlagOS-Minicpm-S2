# Storage snapshot 与 Q32 profile 增量

本批登记六项CPU、profile、官方storage及Q32尝试。storage 16K只得到小幅观察，未更新性能基线；Q32候选在实际数值门失败后停止。原始证据和登记按本批一并同步，历史记录保持不变。

- `20261029T220427329020Z-native-k8-storage-snapshot`：真实PyTorch CPU Tensor边界/别名/set_新调用快照检查通过；ABBA/BAAB局部helper中位数121.378µs→80.748µs/调用（约33.47%），不是完整Adapter或服务收益。
- `20261029T220702833593Z-mixed-a-16k-profile`：profile在benchmark前被旧S2/S4 activation reader误拒绝K-only encoded路径；没有性能样本，不是模型或算子正确性失败。
- `20261029T222344850512Z-mixed-a-16k-profile`：同参非profile预热后的128请求暖态诊断。Q32最大非Graph GPU事件201.460s；已回收Mixed调度Q=2018、context=12108、KV=14126样例，但不等同kernel pointer ABI。profile/collector/analyzer成功，posthoc为`diagnostic_incomplete`，不是官方成绩。
- `20261029T224653126532Z-native-k8-storage-snapshot-b-16384-four-rounds`：四轮3923.23/4555.17/4551.99/4550.26 tok/s，弃首轮均值4552.473333；相对同起始DB的A 4548.78观察+0.0812%。KV页数相同，末态调优DB不同，不能称稳定因果收益。
- `20261029T233910926379Z-q32-causal-interior-component`：helper SHA与冻结身份不匹配，在编译前失败，无性能数据。
- `20261029T234221231370Z-q32-causal-interior-component`：step1048 A/B逐位不等，有限值、readonly、guard通过；未计时，停止候选，不修救。约41MB失败张量留在原件库。

完整storage恢复包按256KiB切块并附重组SHA。Q32失败恢复包与大型张量保留于本地/远端原件库；本批仅发布紧凑状态、源码、编译信息及哈希。暖态完整ixsys trace和恢复包的路径、大小、SHA沿索引保留，未拆块上传。
