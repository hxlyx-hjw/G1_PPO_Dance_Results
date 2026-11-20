# Third-party notices

## AIST++ / AIST Dance Database

The training motion originates from AIST++ clip:

```text
gWA_sBM_cAll_d25_mWA0_ch01
```

The two source views are camera c01 and camera c03. Videos, camera calibration,
mocap annotations and derived motion data are subject to the AIST Dance DB
research terms:

- https://aistdancedb.ongaaccel.jp/
- https://aistdancedb.ongaaccel.jp/terms_of_use/

The original videos are intentionally excluded from the public Git tree.
Do not redistribute them outside the scope permitted by the original terms.

## Unitree G1 MuJoCo assets

`assets/mujoco_menagerie/unitree_g1` retains its original Unitree Robotics
license. See:

```text
assets/mujoco_menagerie/unitree_g1/LICENSE
```

## Python and CUDA wheels

The offline wheelhouse is not committed to Git because it contains several GB
of third-party NVIDIA, PyTorch and Triton packages. Install them from their
official package indexes or obtain them from the original AutoDL package.
