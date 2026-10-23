# 125330 内部长度 guard 修正

原事件客户端在任何背景请求发送前，把 `SampleRequest.prompt_len` 硬等于原 CLI `--random-input-len 16384`，因此误拒正常原请求；不是P质量或到达事件失败。仅复制新gate，将内部guard改为16383并加一行BOS注释；原payload、题目/采样、MM/ID检查、事件门、模型与到达编排均未改。旧失败证据不动。

固定gate SHA：`b7422674fb183afe95aa909dffb12fe7ed56f574b6de768c78230a8267628604`。`gate.diff`及`static-check.json`记录compile和逐byte逆回原7cf010d7；未导入框架/tokenizer、运行样本生成、HTTP或设备。原load/owner由root显式更新gate身份，不能只替文件而留下旧pin。

源码依据为source-audits/20261021T230224Z-benchmark-datasets：

- `datasets.py:602–603`及`utils.py:70–74`先减 `tokenizer.num_special_tokens_to_add()`；本次一个BOS，原CLI16384对应内部16383。
- `datasets.py:750–772`生成序列后以 `add_special_tokens=False`重编码，内部长度是adjusted序列长度；`:658–664`原样存该值与`request_id_prefix + str(i)`。
- `SampleRequest:85`的MM默认None；RandomDataset不传MM。`serve.py:1000–1020`直接沿用内部长度、MM和ID，不在此处补回BOS。

原CPU构造参数（仅root获准运行一次，当前作者未运行）：`get_tokenizer('/workspace/MiniCPM5-2B', tokenizer_mode='auto', trust_remote_code=False)`；`RandomDataset(random_seed=721201, dataset_path=None, disable_shuffle=False).sample(tokenizer=tok, num_requests=32, prefix_len=0, input_len=16384, output_len=128, range_ratio=0.0, request_id_prefix=<125330原Namespace的prefix>, batchsize=1, no_oversample=False)`。LoRA默认None。核当前special数为1、32个内部长度均16383、输出128、MM均None及ID唯一；不改字段以凑断言。重编码有有限尝试，不能只凭目标长度声称32个实际样本已通过。

源SHA：datasets `4aebfc9a1a13b01599a1de8a880e08ff2bae7f6403d430a585908508cc5811b4`；utils `14efee4c78ea60b38e1be458c192ff1972c3295dbebe91bacff414ebcf89c3b6`；serve `b09e85eed6f5f7a9075b40a19fc1dd8e94a1c449665c2c6510f349e0409e77b7`。root执行CPU生成前可核实际这三源同一身份，未扩gate运行时锁或增加动态tokenizer调用。
