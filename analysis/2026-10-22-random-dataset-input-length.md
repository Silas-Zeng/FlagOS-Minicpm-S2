# 实际 RandomDataset 的同长目标与服务输入边界

2026-10-22，仅解释本实例BI-V150当前长负载与snapshot，不提出调度改动。root在设备空闲期纯pathlib取回安装源；本agent仅stdlib读取/AST语义审阅及核5份原字节SHA，没有导入框架、numpy/tokenizer或运行新的benchmark。

**本实例默认 `random_range_ratio=0.0`，不是1。每请求输入生成目标同长、输出请求预算同为1024；但当前原件不足以逐条证明所有服务端重分词后输入都恰为16384。** 两者必须分开表述，不凭总token数倒推逐请求分布。

## 实际参数、parser与生成路径

230224源审计中datasets/datasets.py SHA `4aebfc9a1a13b01599a1de8a880e08ff2bae7f6403d430a585908508cc5811b4`，utils.py SHA `14efee4c78ea60b38e1be458c192ff1972c3295dbebe91bacff414ebcf89c3b6`；serve.py为已有同字节b09e85ee。manifest五份source均独立字节/尺寸核同，机器记录在 `source/kv-memory-observer/random-dataset-source-review.json`，来源原件不改。

- datasets.py:1934–1945 parser `--random-range-ratio` 默认字符串 `0.0`、prefix_len0；RandomDataset:573默认值亦0.0。get_samples:2089解析后2372–2385实际random分支原样传 input/output/range/prefix。
- 原bc51 `context-long-screen` 调用原run_diagnostic_load.sh，实际load-commands为input16384/output1024/concurrency64/requests32/seed721201；helper未传range_ratio/prefix覆盖。B2原load日志Namespace直接证实range_ratio='0.0'/prefix0/batch1/input16384/output1024/ignore_eosTrue，并非仅从命令缺省推测。
- utils.py:64–99先扣 `tokenizer.num_special_tokens_to_add()`，再按输入和输出比例分别求上下界，并对每请求调用rng.integers。ratio0时上下界相同；**ratio1在校验[0,1)之外，会拒绝**。实际B2日志明确 `Sampling input_len from [16383, 16383] and output_len from [1024, 1024]`，据此本次num_special=1。
- 因prefix0，每请求构造的无special目标为16383，输出expected_output_len为1024。随机性在offset与内容，长度没有在区间内变化；default_rng按seed隔离使用。prefix0仅无显式公共prefix，不等于真实APC命中为零。

## 生成目标不等于服务端逐条分词保证

RandomDataset.generate_token_sequence:728–771构造allowed tokens，随后gen_prompt_decode_to_target_len:495–549反复decode→encode(add_special_tokens=False)，截断/补充至目标。默认最多10次调整；重试耗尽仍可返回token_mismatch，sample记录的是实际len(adjusted_token_sequence)。总mismatch累加非零才warning，正负抵消或没有warning也不是逐条成功证明。

serve.py:2026调用get_samples，2028–2031对random执行_align_prompts_to_server_tokenizer。该函数73–144先用`/tokenize`且add_special_tokensFalse比较**首prompt**，相等立即返回全部；不等才逐项取token，对比目标过长才truncate并detokenize，短者不补，失败保原prompt。故它不是无条件检查所有请求分词长度。B2日志未见对齐/重试mismatch warning，这只说明日志观测，不升格为每请求证明。

actual endpoint_request_func.py（174453源SHA5fd4b66d…）:175–194发送的是prompt文本、max_tokens=request.output_len，先把client prompt_len写入输出记录；244–247在有服务usage时以prompt_tokens/completion_tokens覆盖。serve.py:580–601再按成功请求的这些值汇总。B2 `save_detailed=False`，当前只有总input524288/output32768与32成功，不含逐请求输入长度。因此“服务端平均16384”不能证明32个服务端输入逐个都是16384。

生成目标16383、special扣1与服务汇总平均16384一致，符合服务重新加special的解释；但本批没有服务preprocess默认special配置/逐请求token计数完整证据，**该因果解释保持推断**。实际Request对象中的合法num_prompt_tokens/真实进度才是将来框架策略可用信息，不能拿benchmark序号、未来输出或离线全体数据表替代。

本核对不新增实验registry行，不改任何官方或负载参数，不把当前同长目标外推为所有历史run的逐请求明细，不补写victim observer尚未采到的字段。
