#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PYTHONPATH="$ROOT/code"
export G1_DATA_ROOT="$ROOT/runtime"
export G1_DATASET_ROOT="$ROOT/data"
export MUJOCO_MENAGERIE="$ROOT/assets/mujoco_menagerie"
export G1_POLICY_PATH="$ROOT/assets/motion.pt"
export MUJOCO_GL="${MUJOCO_GL:-osmesa}"

ITERATIONS=2 ENVS=1 OUTPUT="$ROOT/outputs/smoke" \
  bash "$ROOT/train_dance_gpu.sh"
