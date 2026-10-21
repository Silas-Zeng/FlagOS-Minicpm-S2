# 212106：KV容量必要下界早退的实际机制验收

本报告只覆盖天数 BI-V150 16SM/32GiB、6CPU、20GiB host、MiniCPM5-2B BF16、normal42 的原件机制，不外推沐曦－曦云 C500 或团队成绩。设备始终由 root 独占；本 owner 仅本地 CPU 读原件，没有 SSH/GPU 或重复测试套件。

## 已确认的行为

run 为 `20261021T212106Z-kv-capacity-context16k-long`，root 原包 SHA `8e04b0b6301c724741759d3a2926e17726b011448ec28b8a14a7ac2ce50af537`。实际 control 协议为 `67e4c07566ee3e52f84d6a96a494b8976d858420dadd5f833e66c3291e32fb73`，worker31cc、transaction616、copyc95f 都保持冻结版本。源码清单 SHA `73e5d880f5a92f528618ffda71677c2b56c4b49ae582258dc0946ff20809a436`，server.log SHA `16d041a2449a8ce2986cb4d8c95a9327871205c7b2d3641b97dd05f9a0323124`。

第一条 `RESTORE_DEFERRED` 在 server.log:208，明确 `reason=capacity_lower_bound`、`free_blocks=1039`、`saved_prefix_pages=1043`、pending/placeholders 均0、token_budget2018，host 保留。后续实际 marker 的 `fast_rejects=462` 与 `restore_skips=462` 相等。受测67e4只有严格 `F<P` 路径增加前一计数，因此本轮确认462次快捷拒绝；没有每次F的完整轨迹，不能把第一条1039推广到每次，也不能由次数推算CPU毫秒。

这个条件只拒绝不可能的分配：当前完整R前缀、computed0、无owned且无cached blocks、单 FullAttention 组必须取得P个不同页；ref0 cache页本来已计入真实freequeue F。`F>=P` 仍要原digest/history/allocator，可能受完整ISL/末token等约束失败，不代表放宽准入或保证成功。P是一组跨42层的逻辑页数，不能乘42。

## 本轮真实页几何与完成链

本轮R为 **16688 token / 1043页 / 717717504B**，不沿用旧16704/1044页。SAVE逻辑页图23段：37、757、126、104页四大段加19单页；42层合计966次copy，与真实ACK相同。

目的图正整数唯一、升序，ZERO与RESTORE命令逐项相同；独立重算66段，三大段为232..1027（796页）、30959..30995（37页）、31000..31146（147页），另63单页。实际 `PRIVATE_PAGES_ORDERED` 记录1043→66、对象/ID/list身份守恒；排序前完整数组未记录，不能声称直接比较了同次两份完整页数组。未来free次序可能改变的原边界仍保留。

真实ACK为：

| 阶段 | calls | 字节与完成 |
| --- | ---: | --- |
| SAVE | 966 | 717717504B，successful/completed均True |
| ZERO | 2772 | 同一私有目的映射，successful/completed均True |
| RESTORE | 2772 | 717717504B，successful/completed均True |
| VERIFY1回读 | 2772 | 全42层717717504B，verification_passed=True |

四个实际RPC的key/serial/kind/pages/prefix/bytes与返回逐项相符，serial为1..4。RESTORE之后原runner在Attention前的六项检查全True；原输出update之后消费16 scheduled token。DROP完成且 `host_held=False`。VERIFY1额外单层pinned buffer为17088512B，本轮不是默认VERIFY0，也不是比赛整模型accuracy证明。

独立专项JSON：[212106-capacity-hardware-review.json](source/kv-transaction/212106-capacity-hardware-review.json)，SHA `e96487e14917020bceaef83e9467eab03e41c93e02816ea17360783a863b2a4f`。其中保存完整66段、ACK、源身份与原始marker行号。

## 可保留与不可声称的结论

机制验收通过：462次必要下界拒绝真实发生，同时后继完整恢复/回读/消费保留。结果32成功/0失败，duration227.19113439507782s、TPS2451.9266629097337只记录为VERIFY1诊断。没有CPU阶段时间，不能由462次推导收益；也不与旧不同source/DB/容量/VERIFY设置的服务作因果对比。整模型accuracy与完整官方两档复现仍独立。

本轮最终KV521840 token；六块容量波动的profile直接原因仍未知，见 [容量原因审计](2026-10-22-kv-capacity-variance-audit.md)，不能以新最终读数补造旧轮原因。实际post为68/0、IPv4/IPv6关闭、416源文件零失败；完整DB/源后态由root/framework另行验收。

root另准备独立VERIFY0累计候选包装 `launch_kv_capacity_pair_screen.py` SHA `be934c108131fd754aea2468a555ad5852068a6a3d734a7df6aafbb7633ca93e`。本owner只读终审无阻断：逆换身份/variant/输出名逐byte回原11917，DB共同起点门/原bc51/锁/VERIFY0保留，212106清单73e5→包装5bef5daf→stable410/candidate416精确。它比较stable与累计capacity候选，不能单独归因462早退；未来仍须实核容量/DB/CPU与实际命中。本文没有执行该包装。
