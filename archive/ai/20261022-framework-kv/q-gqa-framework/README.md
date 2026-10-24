# Q-hoist + GQA 框架兼容短服务

只改原Q77b安装身份守卫，识别exact PR12 GQA wrapper及其canonical原54c闭包，不实际unwrap调用、不重绑统一入口。保持C2→C3→GQA→runner ctor Q；未知包装拒绝，Q/GQA算术与调度均不改。GQA helper1a81409b与原PR12 footer逐byte复用。

完整clean6f412 map44355588，baseline413的runner精确cc7f834d，candidate414=同GQA基线＋Qhelper和最小双路径观察append0f25839e（由原409e接线仅增观察）。两variant固定原bc51、seed721201、原SERVER；只接受原decode4K或context16K-long两既有screen，不自造负载。

```bash
bash launch_q_gqa_service.sh /workspace/experiments/minicpm-s2/code/cpu-combination-combined-20261022T100830Z baseline context16k-long
# 封存与空闲后由root串行candidate，同screen才可比较。
```

部署为implementation.json中7素材；helper/runner/preparer只compile，bash-n通过，未整copy／GPU／新大mock。hardware增量静态审通过。原Q核心／编译／launch／restore全留原，新增守卫只有安装一次身份检查；稳态无额外dispatcher。

INSTALLED与GQA FIRST_WIDTH只作startup/attempt证据，不能当真实execute完成。候选在同一execute包装内记录Q/GQA实际成功execute增量，允许两者不同step命中，证据齐后撤观察；graph replay不增Python计数，未出现delta不能断言operator没运行。基线保持原PR12无observer，GQA FIRST_WIDTH只是attempt/startup证据，完整成功负载不等于逐step覆盖。新的联合数值／准确率尚未验证，单项准确率不能相加继承；DB四端/KV/环境失配不归因。root独占设备，本owner无SSH／网络写入。

只读比较入口：`compare_service_pair.py --baseline-run ID --candidate-run ID --screen context16k-long --output NEW.json`；比完整source／原SERVER-load-driver-benchmark／DB四端／KV／包与CPU配额／成功tokens／候选双marker及后态。可比才输出single_pair_percent_if_comparable，任何失配为null，描述比率仍保留。尚未执行当前pair原件，不预写结果。

冻结时点说明：上文“未GPU／未准确率”指本owner制作资产时的状态；root随后183552/184141真实服务已完成，单pair吞吐+7.466632%，详[最新方法记录](METHOD.md)。组合accuracy184819运行中。

最新状态：184819组合准确率独立PASS101/105，105成功／0传输失败／0cap／无空答案；DB增长为529表19769行，后继须用新起点。详METHOD，不改变此前单pair边界。
