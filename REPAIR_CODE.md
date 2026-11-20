# 代码/配置修复包

本文件对应的修复包只补齐以下内容：

```text
code/
profiles/
config/
verify_package.py
verify_package.sh
prepare_config.sh
train_auto.sh
train_dance_gpu.sh
detect_autodl_environment.py
install_autodl.sh
reset_environment.sh
smoke_test.sh
requirements-autodl.txt
```

不会删除或覆盖：

```text
.venv-clean/
wheels/
assets/
data/
outputs/
runtime/
```

在 AutoDL 上从包根目录执行：

```bash
tar -xzf /root/autodl-tmp/AutoDL_Dance_Code_Repair_20261101.tar.gz
bash verify_package.sh
```

看到 `VERIFY PASS` 后再运行 `bash smoke_test.sh`。
