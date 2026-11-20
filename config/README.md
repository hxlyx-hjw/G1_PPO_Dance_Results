# AutoDL 配置文件

实际环境配置文件由以下命令生成，不要手工复制示例：

```bash
bash prepare_config.sh
```

生成文件：

```text
config/autodl_environment.json
profiles/autodl_detected.env
```

`autodl_environment.example.json` 只是 RTX 5090 / 32 vCPU / 64 GB
参考样例，不是运行时配置。

## 选择逻辑

- RTX 5090 / 显存 ≥30 GB → `rtx5090_32g`
- RTX 4090 → `rtx4090_24g`
- RTX 3090 → `rtx3090_24g`
- 其他 ≥22 GB → `a10_24g`
- ≥14 GB → `rtx4080_16g`
- ≥10 GB → `generic_12g`
- 无 GPU → `cpu_fallback`

并行环境数还会受到 CPU 核数、内存和磁盘剩余空间限制。
