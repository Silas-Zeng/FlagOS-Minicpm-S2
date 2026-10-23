# 原题四题的真实 P 路径诊断

固定060425的423计算序源/map6cf2e1d7，新增诊断helper并显式重定三处runner锁，完整424 map见`files-prepare.json`；不含结构shadow、双prepare、额外模型前向或新算子。生成入口：`python prepare_math4.py --base <冻结423> --output <新目录> --emit-only`。当前部署素材为`files/`，runner22a63b4c、helper29b95266、builder0f4f7fc4。

服务端env：`BIV150_COMPUTE_ORDER_MATH4_DIR=<独立control>/math4-artifacts`。只在真实P outside且已进入生成期的最多4个ChatCompletion内部完整RID上，记录原行、实际P所用CPU position c、prompt长度L、下一生成token的0-based index=c−L+1；原_sample恰一次成功返回后才写每PID的`outside-0..3.json`和`BIV150_COMPUTE_ORDER_MATH4_SAMPLED`。不读取采样token值，不动原采样方法、RNG、历史或InputBatch顺序；marker不证明GPU完成或答案正确。

客户端只在已锁实际EvalScope1.11.1中包装原`completion_params`与`on_response`：仅追加`extra_body.return_token_ids=True`，原raw字典和hook返回不改，旁存完整响应后仍走原choice转换/原judge，退出归还owned hook。原adapter会丢choice扩展字段，故该旁存必要。CLI固定为：

```sh
python3 capture_evalscope.py --output <全新client目录> -- eval <原6e045参数，另加--limit 4及独立work-dir>
```

capture9e1f6bcf。原模型/题目模板、batch8、temperature1/top_p.95/max32768与判卷不改；官方脚本文件不动。本轮仅423单臂：另一owner复用原bc51，先原32×16K/128背景，等本run FIRST_SELECTED后再启动capture；不加ready/start flags、代理、HTTP题目客户端、额外预热或重试。210s编排界限由原owner派生load维护，import错过窗口则记未覆盖。

必须后验核原题库顺序index0..3的四个question_id（原prediction按完成顺序写，不能取前四行）；原prediction保留的ModelOutput.id与旁存response.id一致。完整内部RID按实际源码external ID及其8随机字符后缀唯一匹配，不能直接等同或任意strip；prompt_len还须同旁存prompt_token_ids长度。用真实生成token IDs离线decode前缀定位答案前关系，不encode生成文本冒充原IDs；命中token已晚于答案边界、文本/ID关联不明、原题身份不符或无及时outside，均不认覆盖。四个marker不替代四题完成、原review或新路径精度；本诊断不是官方105题准确率或性能成绩。

CPU仅compile/完整输入输出map/精确逆回/方法AST检查，_sample本体不变。team_view_final_check已只读新增窄审29b952/9e1f6b/0f4f7f通过，无当前诊断阻断；未执行客户端、模型、GPU或新旧suite。实际命中与答案前关系仍待root唯一派发及原件验收，受审代码冻结。

只读结果入口`read_math4.py`：`--eval-dir <原EvalScope timestamp目录> --raw-dir <client旁存> --events-dir <math4-artifacts> --reference-predictions <061500完整原prediction.jsonl> --output <新JSON> [--tokenizer <本地原tokenizer目录>]`。不重判原答案；0个相关outside时直接报告四题原judge与覆盖0，不导入transformers或加载tokenizer。若有对应记录，独立核四题身份、response与完整RID、prompt长度和下一输出index，只解码真实IDs的命中前前缀与全部输出，保存解码旁件；前缀已有完整boxed则保守拒覆盖，缺decoder/无完整boxed不作时间断言。仅compile，实际运行由root在完整原件到达后执行，不以reader退出0称新路径精度通过。
