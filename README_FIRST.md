# 完整训练包：先读这里

这个目录是一个完整、离线可安装的 AutoDL 训练包，包含：

- G1 双视角提取与 retarget 代码
- 12 秒 AIST++ gWA 舞蹈视频、标定、pose 和 reference
- G1 MuJoCo 资产和平衡策略
- `torch 2.7.0+cu128` 及全部 NVIDIA CUDA / Triton wheel
- 全新环境安装脚本、GPU 自动检测和 5090/4090 等 profile
- JupyterLab notebook

## 1. 上传并校验外层压缩包

```bash
cd /root/autodl-tmp
sha256sum AutoDL_Dance_PPO_COMPLETE_20261102.tar.gz
```

必须与旁边的 `.sha256` 文件完全一致。

## 2. 解压

```bash
tar -xzf AutoDL_Dance_PPO_COMPLETE_20261102.tar.gz
cd AutoDL_Dance_PPO_Package
```

## 3. 逐文件完整性校验

```bash
python3 verify_archive.py
```

必须看到：

```text
ARCHIVE VERIFY PASS
```

如果有 missing/mismatch，说明上传或解压仍不完整，不要继续安装。

## 4. 创建全新环境

```bash
bash install_autodl.sh
```

脚本会删除旧 `.venv*`，创建 `.venv-clean`，从包内 wheelhouse 离线安装 Torch，
再安装视频/PPO 依赖并自动执行硬件检测。

## 5. 验证、烟测、训练

```bash
bash verify_package.sh
bash smoke_test.sh
bash train_auto.sh
```

自动配置：

```text
config/autodl_environment.json
profiles/autodl_detected.env
```

默认输出：

```text
/root/autodl-tmp/runs/gwa_100k
```

## 常用排错

确认磁盘：

```bash
df -h /root/autodl-tmp
```

确认代码与数据：

```bash
test -f code/g1_walkfree/__init__.py && echo CODE_OK
test -f data/dance/reference.npz && echo REFERENCE_OK
test -f assets/mujoco_menagerie/unitree_g1/g1.xml && echo ASSETS_OK
test -f wheels/torch-cu128-cp312/torch-2.7.0+cu128-cp312-cp312-manylinux_2_28_x86_64.whl && echo TORCH_WHEEL_OK
```

训练不需要 OpenGL：

```text
G1_MUJOCO_GL=disable
```
