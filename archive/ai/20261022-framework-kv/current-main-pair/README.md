# 当前main与计算序候选短对照

140324基线为main `3283672b`完整445项；141159候选为同main加P的446项、tree `5c77e68caff6aa0c8b6c230adb78a2d4c293cca1`，仅runner与P helper两路径不同。两侧原bc51/SERVER/16K输入128输出/32请求/seed721201均32成功0失败，DB四端565表/20919行三hash相同。

基线119.113426929s/4435.973455 total tok/s，候选111.749335183s/4728.296586；KV为521840→521936，33门仅same_KV失败，gain=null。约+6.589830%只记表观变化，不能归因或认定稳定收益，不重复启动凑容量。完整结果见pair-result.json与原analysis/compute-order-current-main-pair.json。

本目录只保存launcher、回收/比较入口、身份材料和最小回执，tmp原件保留。原Git完整tar仍在tmp/current-main-baseline/current-main-3283672b.tar.gz，不重复复制；两个实际run/control与各自原tgz均在experiments/framework/下。record_pair.py是root已执行登记的留档，禁止因接续再次执行。准备回执中的executed=false是准备时状态，实际执行以root-run-receipts.json和pair-result.json为准。

组合完整105题142019由root独占运行；归档时未出结果。不能继承旧423或main独立102/105作为此组合验收。后续官方两负载完整测试须待本轮准确率通过，仍使用原官方测法，不把旧Q/KV实验ENV混入。
