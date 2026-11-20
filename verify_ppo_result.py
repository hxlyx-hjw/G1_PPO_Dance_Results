"""Replay the packaged best PPO policy in MuJoCo and write an evaluation report."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent
CODE = ROOT / "code"
if str(CODE) not in sys.path:
    sys.path.insert(0, str(CODE))

os.environ.setdefault("G1_DATA_ROOT", str(ROOT))
os.environ.setdefault("G1_DATASET_ROOT", str(ROOT / "data"))
os.environ.setdefault("MUJOCO_GL", "disable")

from fullbody.ppo import evaluate  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--checkpoint",
        type=Path,
        default=ROOT / "results" / "policy.pt",
    )
    parser.add_argument(
        "--reference",
        type=Path,
        default=ROOT / "results" / "reference.npz",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "results" / "local_replay_validation",
    )
    args = parser.parse_args()
    for name, path in (
        ("checkpoint", args.checkpoint),
        ("reference", args.reference),
    ):
        if not path.is_file():
            raise FileNotFoundError(f"{name} not found: {path}")
    report = evaluate(
        str(args.reference.resolve()),
        str(args.checkpoint.resolve()),
        str(args.output.resolve()),
        viewer=False,
    )
    summary = {
        key: report.get(key)
        for key in (
            "policy_used",
            "fallen",
            "steps",
            "simulation_seconds",
            "mean_reward",
            "mean_joint_mse",
            "max_root_xy_error_m",
            "mean_contact_match",
            "reference_completed",
        )
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if report.get("reference_completed") else 1


if __name__ == "__main__":
    raise SystemExit(main())
