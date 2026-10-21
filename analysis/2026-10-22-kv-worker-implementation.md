# 天数BI-V150单victim KV worker：真完成ACK与首个诊断回读

framework_innovation，2026-10-22。root在195012真实布局验收后授权本owner实现worker；systems拥有Core/scheduler/transaction，root拥有独立source/launcher及唯一GPU。本文件为实现交接，**尚无实际服务save/restore或accuracy结果**。不SSH/GPU、不改原runner/default或共享代码库，不执行模型导入。

## 冻结产物与依赖

- `patches/framework/biv150_kv_worker.py`：**31cc7f8d48a57c8e6fef23a2200257750d830422b6e887cc4dacdbc2b602ffbf**。无install、无框架top-level import，只有显式RPC才启用。
- 唯一CPU合同 `analysis/source/kv-worker/check_cpu_contract.py`：**81b7b106f5f1c1ca5facce6e3d411bd528da3a92bb33d24fe5077d850dc8b94e**；结果 `cpu-contract.json`：**a82786e055e6b8f770e46aaae3be52646f62704ec991ae93739e1cf814bc81d7**。
- 必需打包原件 `biv150_kv_page_copy.py`：c95f59a55f5409e651085ff52d788193ea1d5901dcbc99d38fa504842b12f44c；复用已测PagePlan/make_plan/submit_page_copy，不复制替代实现。
- runtime核exact WorkerFL a8de1780、runner e155、WorkerWrapperBase7da443及copy c95f全文件身份。Core适配器另负责actual UniProc/async/scheduler边界，不能用worker替代该检查。

hardware已全文审31cc无阻断：producer fence/强引用、目的页zero、同映射restore/真event、逐层诊断校验、异epoch不污染slot、不能settle保引用；没有重跑suite或GPU。systems已收到最终接口和SHA。代码冻结，后续改变须先协调。

## 唯一接口与状态所有权

`rpc(wrapper, command: dict) -> dict`，由已证UniProc的`collective_rpc(rpc, args=(command,), single_value=True)`同步调用。actual serial_utils callable会收到WorkerWrapperBase，不能错当WorkerFL；worker只取已核类型的`wrapper.worker.model_runner`。

命令为`key=[session, request_id, incarnation, attempt]`、`operation_serial`、`kind=SAVE|ZERO|RESTORE|DROP`、`prefix_tokens=R`、`pages`和`nbytes`。R为完整16token前缀，SAVE/ZERO/RESTORE的页面恰R/16个、唯一且非null、nbytes=R×43008，不支持截断超预算后伪装恢复成功。DROP与copy规则分开：pages=[]/nbytes=0，沿用R，仅同owner/key、serial不旧于当前且已settle才释放host。这个规则已与systems实际Operation零字节DROP统一。

回复回显key/serial/kind/pages/nbytes，附worker_pid、completed/successful、transferred_bytes、host_held、payload/诊断bytes与copy/zero次数、cgroup前后时点及核验字段。completed只来自真实event或异常后的device settle；malformed或无法settle不是成功。systems的_rpc必须把**完整原ACK**记进唯一实验日志，不能只转Receipt而丢verification/memory字段。

单host slot保存pinned host、原raw view、storage身份与event强引用；弱化或清空这些引用之前必须已完成。SAVE新serial、ZERO/RESTORE递增，旧key/serial错误不会把当前正常slot改FAILED；所有权接受后的错误才标当前失败。不能settle时继续强持有全部引用、返回completed=False，由Core失败关闭，不能free/publish/drop。已有请求的token/state/generator、页私有性、FIFO输出消费和Request epoch由Core管理，worker不消费future、修改computed或采样。

## 实际normal42与三种设备操作

195012已独立证实：42个BF16/cuda:0连续NHD view、shape`[pool_blocks,2,16,2,128]`/stride`[8192,4096,256,128,1]`/offset0、独立storage无packed/shared alias。worker再次严格核对，并只用uint8元信息view `[pool_blocks,16384]`，无GPU staging新分配；实际pool大小可变，不硬编码32621。SAVE还核真实`runner.requests[rid].block_ids[0]`逻辑前缀与命令逐号一致。

SAVE：device-wide synchronize覆盖此前所有层已提交KV写入，随后42层按原逻辑页映射D2H到pinned host；末端普通Event record/synchronize完成才ACK。Core收到成功后才可走原free。

ZERO：只对Core已证明独占fresh的本事务目的页，按连续run对42层raw narrow.zero_，真正event完成才ACK。**不复用原Mamba zeroer/no-op，不读取或drain manager.new_block_ids**；FullAttention needszero=False，那个list可含历史ID。slot记录确实zero的逻辑目标映射。

RESTORE：必须同一key/owner/storage、phase ZEROED，且页面与已zero映射逐号一致；H2D按同逻辑位置恢复，真event ACK之后Core才可能继续建立/发布payload。所有操作保持default runner源码/原服务参数，不改RNG或其它请求页。

## 预算与仅诊断回读

固定payload cap=1GiB，额外headroom guard=1GiB，不扫参数。SAVE分配前读取实际cgroup limit/current，要求余量≥payload+诊断校验buf+guard，pin后再次要求余量≥guard；未知硬限额拒绝。每个新分配都是CPU pinned，未提交copy前的失败可在真实settle后原路；这不是全进程峰值保证，不能把宿主总RAM当容器预算。

默认`BIV150_KV_VERIFY_RESTORE=0`无回读。首个真实诊断门root显式设1：SAVE时额外分配**一个layer大小**的pinned校验buffer，计入前后预算；首次成功RESTORE的H2D完成后，逐层仅本事务目标页D2H到同一个buf、真event同步、与该层保存host做CPU uint8逐byte equal。42层全部通过才verification_passed=True/成功ACK，显式记录额外readback_bytes=nbytes和copy次数；不匹配不publish。成功后释放校验buf，并设进程内_VERIFIED_ONCE，后续事务不重复校验。

核验额外回读与CPU比较属于诊断，不能混入性能结论；没有改服务超参数或增加服务请求。RNG没有调用，但仅copy数学不等于端到端RNG/输出不变量，新的恢复路径仍需独立accuracy。

## 验证与下一步

一项必要CPU合同0.35s通过：纯stdlibimport/compile、命令和预算、DROP0bytes、错epoch不污染slot/正常DROP释放引用；不模拟Tensor/copy/event/GPU，不声称它验证真实设备完成。c95f已测normal复制与195012 actual布局作为前置证据，不重复构造形状扫描。

root准备的`prepare_kv_protocol_source.py`与`launch_kv_protocol.sh`已全文只读预审，无包装逻辑阻断：原080656 exact8core/5BIV集合、owner0ecf、5资产SHA/compile、仅AST读init字面量、只改init+5module、全copy逐SHA、原driverbc51/positional run_dir/seed/Serve、设备idle/双栈9031/driver锁与ENV1留档。当前UNREVIEWED pins在填齐前会拒绝执行；root等待systems最终pin后一次真实CPU copy，不能以预审当可上卡授权。未改root脚本。

下一步是systems完整scheduler/worker接口互审，尤其V2 cached payload/all_token_ids/原FIFO消费和FullAttention历史new_block_ids私有页证明；然后由root唯一设备运行复用181041的context-long诊断（原SERVER、16K输入/1024输出/32请求/并发64/seed721201，ENV1）。必须实际见SAVE/free、ZERO/RESTORE completed、全字节回读及后继consumer，不只INSTALLED/CPU ACK链。当前这些设备证据都尚未产生，不能报告吞吐/accuracy或合入stable/default。

## 最终root包装已定向终审，可以进入唯一真实诊断

root填齐已审pins并仅补原observer同式内部alias清单后，最终builder为 **89191b57542e8c2e44eb03b8ebee876f083f3e399e1085149ff0b6a36b49fa42**，launcher为 **e738b736829172a6cbd525cd0d5e5f9dc343a21e0ffe8bcf1c113bbe4a5db47c**。五asset固定probe a4de3abe、copy c95f59a5、transaction **616040602c4ebcfc6b21ace693d193f09fb1bb95da2b874e0bf48039c14a1b13**、protocol **50375e899acbdcee15d3cdec2ecd77875fb355c56ccbfa663271509982ddc19a**、worker31cc；init精确产物 **791c38c20a648f4868e56e24efdae7351671960462232defb85997738f41a2b8**。

本owner已实核最终各SHA、AST读取protocol literal footer加原e043 bytes独立重算791c，不执行候选import；alias块仍先经owner0ecf验证内部regular-file，外部/目录link不通过。launcher相对预审只填builderpin，原bc51/ENV1/positional run_dir/seed/服务负载/preflight不变。读取root唯一CPU结果 `analysis/source/kv-transaction/package-check.json`：410→416文件/6处改动（init+5module）、base和runner不变、无框架导入，与最终pin吻合；本owner没有重跑copy/suite/GPU。包装末审无阻断已回root，先前UNREVIEWED状态仅历史。下一条等root实际事务原件，copy/准确率/吞吐边界仍未解除。
