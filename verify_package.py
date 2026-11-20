"""Self-contained layout, dependency and G1 asset verification.

All paths are derived from this file's location.  The script does not depend on
PYTHONPATH, the current working directory or the AutoDL base environment.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CODE = ROOT / "code"
sys.path.insert(0, str(CODE))

os.environ["MUJOCO_GL"] = "disable"
os.environ.setdefault("G1_DATA_ROOT", str(ROOT / "runtime"))
os.environ.setdefault("G1_DATASET_ROOT", str(ROOT / "data"))
os.environ.setdefault("MUJOCO_MENAGERIE", str(ROOT / "assets" / "mujoco_menagerie"))
os.environ.setdefault("G1_POLICY_PATH", str(ROOT / "assets" / "motion.pt"))


def require(path: Path) -> None:
    if not path.is_file():
        raise FileNotFoundError(f"missing package file: {path}")
    print(f"[OK] {path.relative_to(ROOT)}")


def main() -> None:
    required = [
        CODE / "g1_walkfree" / "__init__.py",
        CODE / "g1_walkfree" / "resources.py",
        CODE / "fullbody" / "__main__.py",
        CODE / "fullbody" / "train_balanced.py",
        CODE / "video_motion" / "multiview.py",
        ROOT / "assets" / "motion.pt",
        ROOT / "assets" / "mujoco_menagerie" / "unitree_g1" / "g1.xml",
        ROOT / "data" / "dance" / "reference.npz",
    ]
    for path in required:
        require(path)

    import cv2
    import mediapipe
    import mujoco
    import numpy as np
    import torch
    from g1_walkfree.resources import find_menagerie, find_policy

    with np.load(ROOT / "data" / "dance" / "reference.npz", allow_pickle=False) as z:
        frames = len(z["times"])
        joints = len(z["joint_names"])
        duration = float(z["times"][-1] - z["times"][0])

    print("python:", sys.version.split()[0])
    print("numpy:", np.__version__)
    print("opencv:", cv2.__version__)
    print("mediapipe:", mediapipe.__version__)
    print("mujoco:", mujoco.__version__)
    print("torch:", torch.__version__)
    print("cuda build:", torch.version.cuda)
    print("cuda available:", torch.cuda.is_available())
    if torch.cuda.is_available():
        print("gpu:", torch.cuda.get_device_name(0))
    print("reference frames:", frames)
    print("joints:", joints)
    print("duration:", duration)
    print("menagerie:", find_menagerie())
    print("policy:", find_policy())
    print("MUJOCO_GL:", os.environ["MUJOCO_GL"])
    print("VERIFY PASS")


if __name__ == "__main__":
    main()
