# math_500 Level 3 after the reduction fix

Score **0.9714 (102 of 105)**, 22 m 11 s, no request errors, mean completion 47.79
output tokens per second per request. Same protocol as the other Level-3 runs
(evalscope, Level 3 subset, batch 8, temperature 1.0, top_p 0.95, max_tokens 32768).

Identical score to the fixed-width kernel run in
accuracy/20261022T152000Z-level3-gqa-kernel, so making the split-K width dynamic cost
nothing in accuracy. Gate is 0.95; the teammate build is 0.9810 and the stated
baseline 0.962. Served by baseline/20261022T170500Z-gqa-fixed with
VLLM_FL_BIV150_GQA_DECODE=1, and a greedy smoke check on that server returned text
identical to the fixed-width build on the same prompt.
