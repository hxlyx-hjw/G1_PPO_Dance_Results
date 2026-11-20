# AutoDL 双视角舞蹈 PPO 训练包

这是从 G1 项目内部抽出的 AIST++ 双机位舞蹈训练包，面向：

```text
AutoDL
RTX 5090 / 32 GB
CUDA 13.0
Torch 2.7.0
Python 3.11
```

AutoDL 实例中的 `python3` 也可能是 3.12；脚本按 `python3` 创建 venv，3.11/3.12
都可使用。

## 显卡与环境选择

项目网络只有 188→128→128→29，显存需求很低；瓶颈主要是 CPU MuJoCo 环境。

| GPU | 显存 | 建议 vCPU | 建议内存 | 结论 |
| --- | ---: | ---: | ---: | --- |
| RTX 5090 | 32 GB | 16+ | 64 GB | 首选，速度快 |
| RTX 4090 | 24 GB | 16+ | 64 GB | 性价比首选 |
| A10 / RTX 3090 | 24 GB | 12+ | 48 GB | 可用但较慢 |
| RTX 4080 | 16 GB | 12+ | 32 GB | 入门可用 |
| 12 GB 级 GPU | 12 GB | 8+ | 32 GB | 保守配置 |

本包离线 Torch 为 `2.7.0+cu128`，适用于 RTX 5090（Blackwell）和 RTX 40/30 系列。
推荐 AutoDL 实例：**RTX 5090 32GB、16+ vCPU、64GB 内存、100GB 数据盘**；
如果预算有限，**RTX 4090 24GB** 已足够。

## 样本

```text
舞蹈：AIST++ gWA (Waacking)
片段：gWA_sBM_cAll_d25_mWA0_ch01
视角：c01 + c03
时长：约 12 秒 / 360 帧 / 30 Hz
标定：AIST++ c01/c03 K/R/t
```

已经预提取：

```text
data/dance/pose.npz
  MediaPipe 2D + DLT 三角化
  有效关节 94.9%
  中位重投影误差 6.09 px
  自修正 187 帧

data/dance/reference.npz
  G1 29-DoF 全身重定向
  360 帧
  contact_grounded + 足底支撑修正
```

因此**不重新提取也能直接开始 PPO 训练**。

## 上传

在本地生成 tar 包后上传：

```bash
scp AutoDL_Dance_PPO_Package.tar.gz root@<autodl-host>:/root/autodl-tmp/
```

服务器：

```bash
cd /root/autodl-tmp
tar -xzf AutoDL_Dance_PPO_Package.tar.gz
cd AutoDL_Dance_PPO_Package
chmod +x *.sh
```

## 用 JupyterLab 一键配置

如果使用 AutoDL 自带 JupyterLab，可同时上传：

```text
/root/autodl-tmp/AutoDL_Dance_PPO_Package.tar.gz
/root/autodl-tmp/AutoDL_Jupyter_Setup.ipynb
```

打开 `AutoDL_Jupyter_Setup.ipynb`，依次运行单元。Notebook 会自动：

1. 查找并在需要时解压训练包；
2. 检查 GPU、CUDA 和 PyTorch；
3. 创建全新的包内 `.venv-clean` 并安装 CUDA Torch 和全部依赖；
4. 运行 `verify_package.sh`；
5. 运行 2 轮烟测；
6. 后台启动 100k 轮训练；
7. 显示日志和模型文件位置，并提供中止训练单元。

本地根目录也放了一份可直接上传的副本：

```text
E:\TEST_RECORD\G1_Project\AutoDL_Jupyter_Setup.ipynb
```

## 安装

```bash
bash install_autodl.sh
bash verify_package.sh
```

每次安装都会先删除包内旧的 `.venv`、`.venv-clean`、`.venv*.bak.*` 和
`.venv*.old.*`，然后创建全新的 `.venv-clean`。不使用
`--system-site-packages`，不依赖 AutoDL 基础环境里已有的 NumPy、MediaPipe
或 MuJoCo，也不保留环境备份。脚本会安装：

```text
torch 2.7.0 (cu128 index)
numpy 1.26.4
mediapipe 0.10.21
mujoco 3.3.x
gymnasium / scipy / opencv-contrib-python
```

**Torch 已离线打包**：`wheels/torch-cu128-cp312/` 内含
`torch 2.7.0+cu128`、全部 NVIDIA CUDA 12.8 运行库和 Triton 3.3.0。
安装时优先执行：

```bash
pip install --no-index --find-links wheels/torch-cu128-cp312 \
  torch==2.7.0+cu128
```

正常安装不再下载约 1 GB 的 Torch 和 2.6 GB CUDA 运行库；只有 wheelhouse
缺失或本地安装失败时才回退联网。wheelhouse 目标为 Linux x86_64 / Python 3.12。

如果镜像的 CUDA 需要其他 Torch 轮子，可在安装前覆盖：

```bash
TORCH_INDEX=https://download.pytorch.org/whl/cu128 \
TORCH_VERSION=2.7.0 \
  bash install_autodl.sh
```

需要只清理环境而不重新安装：

```bash
bash reset_environment.sh
```

该脚本只删除 `.venv*`、缓存和 `environment.freeze.txt`，保留
`code/`、`assets/`、`data/`、`outputs/` 和 `runtime/`。

安装结束后会生成 `environment.freeze.txt`，可用于确认实际版本。训练、验证和
重定向默认设置 `MUJOCO_GL=disable`，不加载 OSMesa/EGL，因此不依赖系统图形库。

## 直接训练

默认 50,000 轮、8 个 MuJoCo 环境、CUDA：

```bash
bash train_dance_gpu.sh
```

先自动读取 AutoDL 环境并生成配置：

```bash
bash prepare_config.sh
cat config/autodl_environment.json
cat profiles/autodl_detected.env
bash train_auto.sh
```

检测器会读取系统版本、GPU 型号/显存/驱动、CUDA、CPU 核数、内存、磁盘和
Python/Torch 状态，再选择 profile 并限制并行环境数。

建议先用 2 轮、1 环境烟测：

```bash
bash smoke_test.sh
```

自定义：

```bash
ITERATIONS=100000 ENVS=8 DEVICE=cuda OUTPUT=/root/autodl-tmp/runs/gwa_100k \
  bash train_dance_gpu.sh
```

续训：

```bash
RESUME=/root/autodl-tmp/runs/gwa_100k/latest.pt \
ITERATIONS=150000 \
  bash train_dance_gpu.sh
```

训练目录会保存 `latest.pt`、`policy.pt`、`best.json` 和日志。

## 重新提取

如果修改了视频或相机参数：

```bash
bash extract_dance.sh
```

该脚本使用随包相机标定，执行：

```text
MediaPipe 2D × 2
  → DLT 三角化
  → 短时空洞自修正
  → G1 retarget
  → reference.npz
```

## 目录

```text
AutoDL_Dance_PPO_Package/
  code/
    video_motion/       # MediaPipe + DLT + 多视角
    fullbody/           # retarget + PPO train_balanced
    g1_walkfree/        # G1 模型接入
  assets/
    mujoco_menagerie/   # G1 MJCF + meshes
    motion.pt           # G1 腿部平衡先验
  data/dance/
    a/ b/               # AIST++ c01/c03 原视频
    calibration.json
    pose.npz
    reference.npz
  outputs/
  runtime/
```

## 说明

- 本包使用 DLT 后端，不需要 SMPL-X 权重。
- 训练使用 CPU MuJoCo 物理 + CUDA PPO 网络。
- `ENVS=8` 是起点；根据 AutoDL 实例的 CPU 核心数调整。
- AIST++ 视频、标定和派生动作仍受 AIST Dance DB 研究条款约束，见
  `data/dance/LICENSE_NOTE.txt`。

## 常见问题

如果出现 `ModuleNotFoundError: No module named 'g1_walkfree'`，说明运行的是
旧版脚本或没有从包根目录执行。重新解压当前 tar，然后只运行：

```bash
cd /root/autodl-tmp/AutoDL_Dance_PPO_Package
bash verify_package.sh
```

当前脚本会显式把包内 `code/` 加入 `sys.path`，不再依赖外部 `PYTHONPATH`。

如果旧脚本出现 `AttributeError: 'NoneType' object has no attribute 'glGetError'`，
说明它尝试加载 OSMesa。当前训练不需要渲染，直接执行：

```bash
export MUJOCO_GL=disable
python -c 'import mujoco; print(mujoco.__version__)'
bash smoke_test.sh
```

当前包已经默认使用 `MUJOCO_GL=disable`。如果以后需要离屏渲染视频，
再单独安装 `libegl1`/`libosmesa6` 并使用 `G1_MUJOCO_GL=egl`。

然后重新运行：

```bash
bash smoke_test.sh
```
