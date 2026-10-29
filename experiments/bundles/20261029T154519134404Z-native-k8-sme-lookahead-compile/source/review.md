# NativeK8 K-lookahead 增量复核

审阅范围：仅源变换的同步、共享内存边界与 S2/S4/尾页控制流。候选 SHA256 `108131ada8a8b5cae65264f3348b2947ba34eeeb561ea790505bc84f3511ef45`；base git blob 校验通过，执行逆变换后与 main `899ce77470b0b539aebc108fd122f668c2d5894d` 的冻结 base CU 逐字节相同，codec 原字节一致。未编译、未运行GPU。

- K stage 对齐既有布局探针：page stride 16384B、head offset 128B、descriptor row stride 256B；两个16×64B SME tile的全局K偏移为0/64B，shared偏移0/1024B，合计写K stage 2048B。K data占shared起始2048B；当前PV读取的V从 `stage+1024`（字单位，即byte offset 4096）开始，两个区域不重叠。此处复用已通过的独立2048B K布局测试，不扩大为attention正确性证明。
- K0 prologue仅在 `position < full_upper` 时发起，随后 `waitcnt(8ULL)` 和既有CTA barrier，之后才由 `KReady=true` 消费。S2/S4仍由同一已冻结template/grid实例化，候选变更没有动 `Segments`/grid限制。
- 当前页的V保持原有顺序：issue V → QK/softmax → 原V wait8及ready barrier → 可选next-K issue → 当前PV → 条件next-K wait8 → 原页尾barrier。待发起的next K只写K区，PV读取V区；页尾barrier后才进入下一页并重新issue V，因此两次异步搬运之间有明确完成点。SME wait作用是保证下一页K在下一次QK/共享读之前完成；不可由源码次序推断其与PV真实重叠。
- `has_next = next_position < full_upper`，只允许当前segment内尚有后续完整16-slot页时提前读取block table并发K。segment末尾不会探测下一segment页；partial tail走原 `issue_k_i8(..., valid, ...)` masked load路径，且默认不启用lookahead。`lower>=length`仍原样返回，`full_upper==lower`时不发K0；只剩partial页时由旧tail路径处理。
- Q codec、QK、softmax、PV、累加顺序、reducer接口与输出由精确锚点/逆变换保持原字节。构建guard继承main的 `__IX_ARCH__` 条件，不因host pass缺设备宏报错。CPU验证：base blob正确、inverse byte-exact、codec byte-exact均通过。

**结论：允许进入CPU compile-only门，不授权设备运行或性能结论。** 实际生成的S2/S4 LLVM/ASM需确认next-K两条SME load在PV指令前发射，且对应K wait没有被后端提前到PV前；若编译器把wait提前，或共享stage/资源/符号检查不符，停止，不以源码顺序宣称重叠。CPU编译通过也不构成数值正确性或生产资格。
