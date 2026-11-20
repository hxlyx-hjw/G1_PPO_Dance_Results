# AutoDL GPU / 环境 profile

本项目 PPO 网络很小：

```text
Actor: 188 -> 128 -> 128 -> 29
Critic: 188 -> 128 -> 128 -> 1
JointAssist: 29 个 16 维残差头
minibatch: 256
horizon: 128
```

GPU 显存不是主要瓶颈，CPU MuJoCo 环境和 CPU 核心数更影响吞吐量。

## 推荐矩阵

| Profile | GPU | 显存 | 建议 vCPU | 建议内存 | 并行环境 |
| --- | --- | ---: | ---: | ---: | ---: |
| `rtx5090_32g` | RTX 5090 | 32 GB | 16+ | 64 GB | 12 |
| `rtx4090_24g` | RTX 4090 | 24 GB | 16+ | 64 GB | 10 |
| `a10_24g` | A10 | 24 GB | 12+ | 48 GB | 8 |
| `rtx3090_24g` | RTX 3090 | 24 GB | 12+ | 48 GB | 8 |
| `rtx4080_16g` | RTX 4080 | 16 GB | 12+ | 32 GB | 6 |
| `generic_12g` | 12 GB 级 | 12 GB | 8+ | 32 GB | 4 |

首选 **RTX 5090 32GB**，其次 **RTX 4090 24GB**。两者都支持本包的
`torch 2.7.0+cu128` 离线 wheelhouse。

## 自动检测

```bash
bash prepare_config.sh
cat profiles/autodl_detected.env
```

检测器会读取：

- `/etc/os-release`
- `nvidia-smi` 的 GPU/显存/驱动/计算能力
- CPU 核心数
- `/proc/meminfo`
- `/root/autodl-tmp` 磁盘空间
- Python、Torch、CUDA 状态

并写出：

```text
profiles/autodl_detected.env
config/autodl_environment.json
```

自动按 GPU 选择 profile，再根据 CPU 核数和内存降低并行环境数。

## 使用检测配置训练

```bash
bash train_auto.sh
```

手动指定 profile：

```bash
PROFILE_FILE=profiles/rtx4090_24g.env bash train_auto.sh
```
