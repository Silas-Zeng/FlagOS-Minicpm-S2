# 公共前缀扫描：只排队成本观察

主线固定干净6f，算子由队友负责。本包未部署；默认helper关闭，接线**只启用observe**，skip服务未获批准。不要为本项单独运行五分钟，应并入下一项有价值且经owner审阅的服务诊断。

实际死工作依据：df780 Scheduler.schedule:1002–1009计算公共前缀；2e91 manager:520→22e FullAttentionManager:590–598逐页refcount扫描；6f runner:2591/2627–2722仅用于cascade资格。1219 Triton Builder没有覆盖能力方法，继承actual backend.py c524988a… 的固定False；与APC的命中查询、哈希、分配和free是不同路径，不关闭APC。230548真实长负载有Running1阶段，但当前165525末个partial histogram的N1=32含31个smoke步，可能尚未覆盖最终长尾，不能以此证明全程N1很少或很多。

helper严格识别实际EngineCoreProc、AsyncScheduler、同PID UniProc/Wrapper/WorkerFL/ModelRunnerFL、单组42层原Triton Builder。首次Core.step才核自然加载源，未提前import设备模块。observe原callee恰一，保原结果/异常context；按单请求/多请求分别累计wall及calling-thread CPU，邻接clock成本包含在数值中；2的幂次只输出partial累计，不能当完整benchmark总数。无GPU API、同步、页值或Future访问。候选skip代码仅N1且单attention-group，multi原路且不读clock，但**没有部署/净收益依据**。

准备器核原完整412 map，输出只修改init并新增helper→413，原6f runner不变。显式环境BIV150_PREFIX_COST_OBSERVE=1才安装，init失败原路继续；CORE_HOOKED只预检，实际ARMED与CPU_COST_PARTIAL才证明接入。launch只沿原bc51 owner/锁/双idle/DB/source，不新建controller；需owner明确给base和已有load_mode，当前不执行。若以后与其它诊断合并，须单独审核该诊断source差分，不能把严格412验证改成任意叠加。

判定：累计原callee预算很小则关闭，不以O(千页)或1KiB元数据推出大收益。观察成本不是可等额兑现的E2E收益。当前仅新增源码syntax/精确init附加compile，未跑复杂mock、设备或旧合同；framework已确认消费者链和d0698主体，最终微小计时分支差分待封口。没有性能/正确性通过声称。
