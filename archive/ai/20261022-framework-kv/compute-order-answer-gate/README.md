# 计算序辅助答案门

只检验实际选路的端到端答案可用性，不是官方accuracy、逐层数值、随机token或RNG状态逐位等价证明；本门用时不用于收益。原422为baseline，060425冻结423为candidate，不叠accepted-fill。

原bc51 owner仅增加辅助CLI约束、将一次load命令换为client（`owner.diff`两切口，可精确逆回）。原SERVER、独占锁、smoke、监控、源/环境记录、超时、清理不变，官方脚本不改。薄launcher固定两份完整源/map并归档control；原sealer完成DB-after/source-post/idle/seal。

先在CPU用实际本地tokenizer生成一次请求，两个服务共用该文件；本地尚未执行tokenizer或生成数据。JSONL含32个不同前16-token块、精确16384 token ID输入，末尾few-shot简单加法、每题不同真值。模型不加载；API要求不添加special tokens，并以后验usage核16384/128。采样固定temperature1/top_p.95/max128/ignoreEOS，无request seed，沿global RNG路径；并发上限64，总请求32。

```sh
# assets为本目录五个已冻结运行py（含run_answer_gate.py）上传目录；只由root执行。
python3 "$assets/prepare_requests.py" --tokenizer /workspace/MiniCPM5-2B \
  --output /workspace/experiments/minicpm-s2/diagnostic-inputs/compute-order-answer-<UTC>/requests.jsonl

# 每次只启动一侧；等原owner清理并封存后再启动另一侧，不自动pair。
python3 "$assets/launch_answer_gate.py" baseline --requests "$shared_requests"
python3 "$assets/launch_answer_gate.py" candidate --requests "$shared_requests"

# 每侧结束后复用原工具，不改变原始结果。
python3 /workspace/experiments/minicpm-s2/scripts/seal_framework_screen.py "$run"
```

每条原始请求/响应及独立结果位于`RUN/context-16k/`，总表为`answer-summary.json`。判首个完整`<answer>整数</answer>`真值，不跳过第一个错误tag找后续正确答案；忽略强制128输出的后续续写。所有32条transport/实际长度/答案均须通过。candidate还必须在本负载起止之间新增同Engine实际`FIRST_SELECTED`，Dprefix/outside均正、原N行映射、forward已返回；marker本身位于logits/sampler前，完整答案为另一个事实，不能说每个请求都被分区。

两臂summary的`requests_sha256`必须一致；baseline自己不过则该门无判别力，不能归罪候选；candidate无真实命中则仅fallback兼容。独立问题真值确定不代表两侧随机文本应逐位相同。若API拒绝token ID/add_special_tokens参数，或usage多了BOS等，则原始错误保留并拒绝，不静默改请求重试。

额外覆盖限制：marker没有request ID或该请求输出token位置。某些请求的首个答案可能早于首次命中，P只影响其后续续写；同时窗中尚未完成prefill的请求仍可能经P后产生答案。现有证据不能逐条建立这种归属，不据“命中+32首tag正确”宣称全部答案直接覆盖P或所有q1逆映射已证。若必须建立逐请求归属，应另经批准加最小一次CPU观察，本门不自行扩大。

`static-check.json`只记录作者compile/原SERVER AST/两切口精确逆回。team_view_final_check已新增只读审6daf/9b645/19853无运行阻断：无request seed、首完整tag/usage、负载内新增marker及原清理路径相符，没有运行client/owner或旧门。root已独立CPU生成请求，作者未运行tokenizer、mock、SSH或GPU。root安排新卡队列，先baseline自己通过才继续candidate；不继承061500的fallback准确率资格。
