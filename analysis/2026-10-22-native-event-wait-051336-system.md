# 051336：直接Corex flags3事件完成性通过，等待CPU未下降

唯一本地系统审计JSON `analysis/source/event-wait/051336-native-system-review.json` SHA `365e6760d219626534209cc56bdd01220ee1be4d45305b421bf49e90291e7cd7`。85项seal完整文件集合、source5/f3133-7bac-327e-ee01、实际Corex头、编译命令/exit0/stdoutstderr/ldd/rpath/readelf和桥加载前后实际libcudart d39d均核。SO16256B，SHA1376f0e8cd8e6f988b15b6389fa07448df1cc842ec40d88245c9941862f508bf。归档1859977B/SHA7a059bde2104e0f404e2983fa3b234976970198838d4905d554f3fb8ad8c7d7b。

A generic、B typedblocking、C独立SDK创建的Corex BlockingSync|DisableTiming事件。真实C创建flags=3且SO身份匹配，绕过Torch事件创建/缓存；D2H仍由同一显式非0Torch stream提交，SDK事件记录同一handle。六窗ABCCBA各四trial，每trial八次32MiB pinned D2H。24trial144项完成/query/完整host字节/guard/源不变及RNG全部通过，early_complete总0；native事件settled后close通过，无失败清理的全设备同步救场。

| 窗口 | wait wall ms | wait线程CPU ms |
|---|---:|---:|
| A | 9.420034 | 9.436844 |
| B | 9.901833 | 9.919480 |
| C | 9.419391 | 9.434407 |
| C | 9.421018 | 9.436430 |
| B | 9.422719 | 9.437989 |
| A | 9.422119 | 9.437016 |

直接SDK route的等待线程CPU仍约9.435ms、接近wall9.420ms，没有降低等待CPU的证据，不接入模型服务。不据此断言Corex驱动内部具体实现；也不将B首窗波动或时钟采样区间差异当收益。六窗v1cpu.stat节流增量0，原6CPU/56Torch线程保持。验证在被测等待返回后、任何独立源回读前完成，不以额外同步掩盖失败。

DB前后523表19474行，物理dc2c/schema0dc7/logicalc05d三SHA同；05:13:44.418199Z后态68MiB/0%、无GPU进程、9031双栈closed，源码前后不变，controller266261/worker266288 exit0。root第一次在SCP session37357尚未退出时尝试读取，遭文件锁拒；确认write_stdin exit0后解包、85项原件完整校验均通过。该收集时序不是设备失败，不重跑本门。

registry117/queue90已收口。按用户要求，这是最后手头设备门，随后仅整理GitHub与不同方法的PR。没有新研究、自动服务接入或大测试，本agent不操作GitHub。
