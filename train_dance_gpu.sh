#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -x "$ROOT/.venv-clean/bin/python" ]; then
  PY="${PYTHON:-$ROOT/.venv-clean/bin/python}"
elif [ -x "$ROOT/.venv/bin/python" ]; then
  PY="${PYTHON:-$ROOT/.venv/bin/python}"
else
  PY="${PYTHON:-python3}"
fi
export PYTHONPATH="$ROOT/code"
export G1_DATA_ROOT="$ROOT/runtime"
export G1_DATASET_ROOT="$ROOT/data"
export MUJOCO_MENAGERIE="$ROOT/assets/mujoco_menagerie"
export G1_POLICY_PATH="$ROOT/assets/motion.pt"
export MUJOCO_GL="${G1_MUJOCO_GL:-disable}"

test -f "$ROOT/code/g1_walkfree/resources.py" || {
  echo "Missing package code: $ROOT/code/g1_walkfree/resources.py" >&2
  exit 3
}
test -f "$ROOT/code/fullbody/train_balanced.py" || {
  echo "Missing package code: $ROOT/code/fullbody/train_balanced.py" >&2
  exit 3
}
cd "$ROOT/code"

REF="$ROOT/data/dance/reference.npz"
OUT="${OUTPUT:-$ROOT/outputs/aistpp_gwa_ppo}"
ITERATIONS="${ITERATIONS:-50000}"
ENVS="${ENVS:-8}"
HORIZON="${HORIZON:-128}"
DEVICE="${DEVICE:-cuda}"
LOG="$ROOT/outputs/train_$(date +%Y%m%d_%H%M%S).log"

test -f "$REF" || { echo "Missing $REF; run extract_dance.sh first." >&2; exit 2; }
mkdir -p "$OUT" "$ROOT/outputs"

ARGS=(
  "$REF"
  --output "$OUT"
  --iterations "$ITERATIONS"
  --envs "$ENVS"
  --horizon "$HORIZON"
  --device "$DEVICE"
  --leg-weight "${LEG_WEIGHT:-0.15}"
  --arm-weight "${ARM_WEIGHT:-1.0}"
  --motion-gain "${MOTION_GAIN:-1.35}"
  --rl-pd-influence "${RL_PD_INFLUENCE:-0.7}"
  --hand-rl-pd-range ${HAND_RANGE_MIN:-0.2} ${HAND_RANGE_MAX:-0.6}
  --foot-rl-pd-range ${FOOT_RANGE_MIN:-0.5} ${FOOT_RANGE_MAX:-0.9}
  --joint-assist
  --airborne-reward
)

if [ -n "${RESUME:-}" ]; then
  ARGS+=(--resume "$RESUME")
fi

echo "Training reference: $REF"
echo "Output: $OUT"
echo "Iterations: $ITERATIONS | envs: $ENVS | device: $DEVICE"
echo "Log: $LOG"

set -o pipefail
"$PY" -u -m fullbody.train_balanced "${ARGS[@]}" 2>&1 | tee "$LOG"
