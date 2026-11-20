# Q32 连续页仿射寻址

在完整且连续的KV页区间内，以仿射页号替代页表读取；跨界与尾部保留原页表路径。编译审阅确认命中分支去除页表读取，但ASM SGPR spill计数98→110。理想连续页布局的5-case数值门通过、四组ABBA局部省1.4188%；descriptor构建/H2D与真实覆盖率未测，仅保留条件候选。

- [20261030T024139836824Z-q32-affine-pages-compile-probe](../runs/bi-v150/20261030T024139836824Z-q32-affine-pages-compile-probe.md): 编译审阅确认完整连续页命中分支以仿射页号替代页表读取，fallback仍保留；A/B runtime寄存器135、shared57344、runtime spill均相同，但ASM SGPR spill计数98→110。仅合成descriptor编译探针，无reader、数值或性能测量，真实覆盖率与descriptor构建/H2D成本未知。
- [20261030T024939570521Z-q32-affine-pages-component](../runs/bi-v150/20261030T024939570521Z-q32-affine-pages-component.md): 5个case全输出逐位一致，选定CPU FP64、guard、只读与changed-Q检查通过。四组ABBA Event均值A7.989743/B7.876383 ms，省1.418813%，四组方向一致。仅理想连续页合成布局，未计descriptor构建/H2D且无真实覆盖率与生命周期验证；保留条件候选，不接服务、不更新基线。
