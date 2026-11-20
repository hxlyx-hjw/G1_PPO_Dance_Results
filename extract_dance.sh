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
test -f "$ROOT/code/video_motion/multiview.py" || {
  echo "Missing package code: $ROOT/code/video_motion/multiview.py" >&2
  exit 3
}
cd "$ROOT/code"

A="$ROOT/data/dance/a/gWA_sBM_c01_d25_mWA0_ch01.mp4"
B="$ROOT/data/dance/b/gWA_sBM_c03_d25_mWA0_ch01.mp4"
CAL="$ROOT/data/dance/calibration.json"
POSE="$ROOT/data/dance/pose.npz"
REF="$ROOT/data/dance/reference.npz"

test -f "$A"
test -f "$B"
test -f "$CAL"

"$PY" -m video_motion multiview "$A" "$B" \
  --output "$POSE" \
  --fps 30 --max-seconds 12 --quality full --backend dlt \
  --calibration "$CAL" --no-auto-sync \
  --self-correct --repair-gap-seconds 0.7 | tee "$ROOT/data/dance/extract.log"

"$PY" -m fullbody retarget "$POSE" \
  --output "$REF" --root-mode contact_grounded --refine \
  | tee "$ROOT/data/dance/retarget.log"

echo "Reference ready: $REF"
