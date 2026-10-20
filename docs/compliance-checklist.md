# Competition compliance checklist

Status values: `pending`, `verified`, or `not applicable`.

| Requirement | Evidence | Status |
|---|---|---|
| Use MiniCPM5-2B only | local model config and safetensors hash | pending final |
| Use `vllm-plugin-FL` branch `flagos-2026-s2` | remote branch tip resolved to `13eb9be69`; source commit hashes recorded | verified at baseline |
| Use FlagGems `v5.3.5` | tag resolves to `4df52d9168ac55c1c1061cefb4638c570292d896` | verified at baseline |
| Keep official service arguments | command file in every baseline directory | verified at baseline |
| Do not edit or tune official benchmark script | script hash `0813eba574e9d1eb50c297c515baa426da1bcb61ce8c78a398b482f246005565` | verified at baseline |
| Do not change hyperparameters to enable quantization/speculation | launch-command diff review | pending every candidate |
| Do not switch operators without an implementation change | code diff and kernel evidence | pending every candidate |
| Do not merge the latest framework branch | fixed base commit and patch-only diff | pending final |
| Keep model behavior and output valid | smoke + operator tests | pending final |
| `math_500` Level 3 >= 0.95 | official evaluation log | pending |
| 4K and 16K performance greater than the 1% window | official benchmark CSV | pending |
| Report strategies appear and are enabled in submitted code | code-to-report matrix | pending final |
| Reproducible from a clean environment | clean setup transcript | pending final |
| Submit `report.pdf`, `readme.md`, and source | release archive inspection | pending final |
| FlagGems included when operator changes exist | release archive and diff | pending |
| Awarded PR submitted within 3 working days | only after award | not applicable now |

The official page leaves the throughput lower/upper and TTFT interval text
incomplete. Final acceptance gates must not claim more certainty than the
official response provides.
