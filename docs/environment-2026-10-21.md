# Environment record: 2026-10-21

## Connection

- Entry: FlagOS SSH gateway
- SSH authentication: dedicated Ed25519 key created for this task
- Public-key fingerprint:
  `SHA256:YBsnxjMuO8HB3V9pbejfv7EabmMZ0Umjvy2ffGkH6bM`
- Hostname inside container: `000cf2952330`
- User: `root`

Private keys and connection secrets are not stored in this repository.

## Host and runtime

| Item | Observed value |
|---|---|
| Kernel | Linux 5.4.0-148-generic x86_64 |
| Host-visible system memory | 503 GiB |
| Container memory limit | 20 GiB (`memory.max=21474836480`) |
| Platform-visible CPU allocation | 6 CPUs |
| Host-visible CPUs | 112 (`nproc`) |
| Swap | 8 GiB |
| Container root filesystem | 50 GiB overlay |
| Accelerator | Iluvatar BI-V150 |
| Visible devices | 1 |
| Device memory | 32,768 MiB |
| Device UUID | `b18272be-ac3a-5ec1-80d8-eed9d1d1b3ab` |
| Compute capability reported by PyTorch | `7.1` |
| Multiprocessor count | 16 |
| L2 cache | 16 MiB |
| Driver / IX-ML | 4.5.0 / 4.4.0 |
| CoreX | 4.5.0 |
| Python | 3.12.11 |
| PyTorch | 2.10.0+corex.4.5.0 |
| Transformers | 5.14.1 |
| vLLM | 0.24.0+empty |
| vLLM plugin FL | 0.3.0rc0+g13eb9be69 |
| FlagGems | 5.3.5 |
| FlagTree | 0.6.2a3+iluvatar3.6 |

FlagGems reports vendor `iluvatar`, device type `cuda`, and
`use_c_extension=False`. The observed Attention path is therefore the pure
Triton implementation in `flag_gems.ops.flash_api`, not the optional C++
operator extension.

The host PCI topology exposes many accelerators, but both PyTorch and `ixsmi`
expose only one device to this container. Results must not be described as
two-card results. The host-visible CPU count is not the platform allocation:
the reservation displayed by OnlineLab is 6 CPUs.

## Workspace

| Path | Size | Revision/status |
|---|---:|---|
| `/workspace/MiniCPM5-2B` | 4.7 GiB | local model snapshot |
| `/workspace/vllm-plugin-FL` | 9.7 MiB | `13eb9be69ecc5b5ca4f79c44e9ee40081eaa1bf0`, `main`, ahead of `origin/main` by 6 |
| `/workspace/FlagGems` | 105 MiB | `4df52d9168ac55c1c1061cefb4638c570292d896`, tag `v5.3.5` |
| `/workspace/evalscope-datasets` | 452 KiB | `math_500/test.jsonl` present |

The required model checkpoint is approximately 5.03 GB and is stored as one
safetensors shard.

## Verification notes

- `git ls-remote` from the local host confirmed that the official
  `flagos-2026-s2` branch points to
  `13eb9be69ecc5b5ca4f79c44e9ee40081eaa1bf0`. This is exactly the installed
  `vllm-plugin-fl` revision and the source checkout commit.
- The source checkout is locally named `main`, but its commit is the official
  competition branch tip. We will create a local branch with the official name
  before making changes, without rewriting the existing checkout.
- The instance exposes exactly one accelerator despite the earlier expectation
  of two. All device measurements follow a single-card protocol.
- The service started successfully and the official smoke request returned a
  valid MiniCPM response.
- Confirm `math_500` Level 3 subset completeness through the official
  evaluation before final submission.
