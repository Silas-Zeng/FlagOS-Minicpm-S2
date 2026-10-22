# 035754实际三路：无新增窗口节流，保留单层小收益

本owner独占此文档。实际run为 `20261022T035754Z-kv-pitched-threeway-gate`，设备子进程260602，root包SHA `fa80a90332005eda7cc77862c82c85876a27ee9e10692456409b7abf909b4bbd`。本次只直接解析results里的六窗、CPU原统计、准备成本和对应解释，未执行systems唯一全原件验收或任何旧suite／GPU。

实际9b16 gate／818e runtime／0a4d C++、已编译SO9e33及maps libcudart d39d保持冻结；非0 stream handle94323367614720，实际maxpitch2147483647B。两实际map三路oracle／c95f字节、guard／整源／RNG均报告通过；C-linear是受控PAGE拆段，37／26全线性API、0二维，字段fallback9／4不表示设备能力不足。C2D使用实际maxpitch，真实提交11／6（2线性＋9／4二维）、fallback0。完整源／结果与清理由systems负责唯一整门核验。

## 单层首case固定64call，A／B／C／C／B／A

仅015315的1058页、17334272B参与计时。A为c95f，B为同桥C-linear，C为同桥C2D；六窗各64call。所有准备／event首record／submit预热在窗前；CPU整池比较在六窗后。

| 窗口 | wall ms／call | 同流event ms／call | Δnr_periods | Δnr_throttled／throttled_time |
| --- | ---: | ---: | ---: | --- |
| A1 | 0.682748388 | 0.679097235 | 0 | 0／0 |
| B1 | 0.655123797 | 0.652384877 | 1 | 0／0 |
| C1 | 0.631449424 | 0.628297448 | 0 | 0／0 |
| C2 | 0.631230563 | 0.628322840 | 1 | 0／0 |
| B2 | 0.654983385 | 0.652412593 | 0 | 0／0 |
| A2 | 0.689953056 | 0.653520525 | 0 | 0／0 |

本owner从每窗真实v1原文本重算before／after／delta，与记录逐项相符。六窗均无新增节流；仍56线程／600000:100000us额度，不曾改线程、额度或官方参数。CPU准备开始至首窗之前有55个period／46个throttled period、累计throttled_time增204298016825ns；可定位“计时前已发生过节流”，不能定位某个pattern／比较／分配函数，不能倒推032653异常根因。

| 两样本均值 | A | B | C |
| --- | ---: | ---: | ---: |
| wall ms／call | 0.686350722 | 0.655053591 | 0.631339994 |
| event ms／call | 0.666308880 | 0.652398735 | 0.628310144 |
| 进程CPU ms／call | 0.688556711 | 0.658792609 | 0.633713094 |

本轮热wall描述性差：A→B约4.55993%，B→C约3.62010%，组合A→C约8.01496%；event对应2.08764%／3.69231%／5.70287%。小收益值得保留。同桥B/C在本轮支持“保全部KV的2D合并相关改善”，比仅A/C更能区分路径；不能称DMA纯贡献、原生API内部不使用SM或单个Python操作成本。进程CPU时间包含进程全部线程及等待实现，也不是纯Python执行时间或wall。

A的event首尾0.6791／0.6535ms仍有差异；B、C在本轮两样本较接近，不意味着跨负载稳定。六窗无新增节流仅排除本轮观测窗口的该项增长，不排除调度／时钟／其它噪声。保留单次镜像结果，不再追加同类微门或追样本。

## 准备仍要付费，不能将热差乘42

| 窗外单次准备 ms | 015315 | 021658 |
| --- | ---: | ---: |
| 旧c95f plan | 1.351080 | 0.944637 |
| 新plan | 1.474416 | 1.055410 |
| C2D tensor检查／ctypes descriptor | 1.303388 | 0.449833 |
| C-linear tensor检查／ctypes descriptor | 0.807358 | 0.507724 |

新plan＋C2D准备分别2.777804／1.505243ms，均不在热submit窗口内。这些只是受当时CPU状态影响的单次样本；不能把它们当免费、直接乘42或与热均值相加宣称真实一次SAVE正／负收益。服务通常只做一次SAVE，尚需真实42层、首次加载、producer fence、pinned分配及完成事件成本。32GiB／16SM／6CPU背景没有改变这个边界。

## 下一步只走已授权真实事务

该信号足够保留，进入root已授权的一次原long／VERIFY1真实42层诊断，不另造22GiB合成fixture，也不把本轮8.01%当42层或E2E收益。新worker须保持FULL1aff／txn84be及原5d9a语义，仅替换SAVE；首次真实SAVE才载入精确818e／SO9e33，所有42层metadata先验，PreparedSave／桥首次提交前写入slot强持，原真实fence／event／失败settle保持。

SAVE完成且源free前，复用已预算单层verify_buffer，用冻结c95f逐层回读真实源页，实际event完成后比新host；42层全byte通过才SAVED，随后原FULL恢复／回读、runner及consumer。原host预算不增加，不能仅用host自证新SAVE正确。当前新worker仍是后继独立实现／审阅，尚无真实事务或性能结果。源／字节／采样／官方参数不因本轮变更。

专项JSON为 `source/kv-pitched-copy/035754-hardware-review.json`，保六窗原统计和重算值。本文没有写入systems报告，未SSH／GPU／重复validator；worker交叉审另记明确pin与结论。

## 后继新SAVE worker只读终审，非035754受测代码

新独立 `patches/framework/candidates/biv150_kv_pitched_save_worker.py` 最终SHA `a662e478d20884c5b1d65e0ee3d270a62453d88166b28e092dcaf3b35a3df854`。本owner已全文对比5d9a及唯一CPU stub合同，无当前一次真实VERIFY1门阻断：仅SAVE换为实际SDK batch，原scope、1GiB／headroom、producer fence、`_finish`和异常settle保持；runtime／邻接SO晚至真实SAVE加载，核隔离路径及实际lib身份。PreparedSave、桥和当前流在任何可能提交前写入slot；部分失败不能旧路重试，不settle仍持raw／host／descriptors／library等引用。

新SAVE完成后，VERIFY1复用原单层verify_buffer，逐层冻结c95f读真实源，`_finish`事件后CPU全byte比新host，42层全过才SAVED；buffer继续留给原FULL回读，VERIFY0不做新增源回读。协议1aff／事务84be／FULL覆盖证明／原消费者路径不动。服务可能使用的实际current stream包括0，不能继承单层非0流门的实测结论；新worker记录真实handle，下一真实事务的同流完成与独立42层源比才是现场证据。

作者唯一合同实际运行的worker是历史4f1dd74c…，test `38de41e794a85d258acc11c113e2f9d7b912197a689694b661634c245f6c4997`，1test／0.122s通过；`worker-cpu-check.json` SHA `9df0b498d9ed218ad56f799e3fc6d1117a6afd0d4feccc0611c294dafa0b7823`保留该身份，loader／Tensor／SDK／event为stub，不是设备证明。随后最终a662仅把/proc maps按resolved路径先去重、各库hash一次，避免同lib多mapping重复读8.39MB；旧4f归档SHA已核，定向delta无复制／语义改变，只compile，没有重跑合同或虚称最终设备通过。root和作者已收本owner无阻断回执，独立420源包装与真实VERIFY1仍待后继执行。
