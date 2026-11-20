#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$ROOT/.venv-clean"
TORCH_VERSION="${TORCH_VERSION:-2.7.0}"
TORCH_INDEX="${TORCH_INDEX:-https://download.pytorch.org/whl/cu128}"
WHEELHOUSE="$ROOT/wheels/torch-cu128-cp312"

echo "[0/4] Removing old environments and backups"
rm -rf -- "$ROOT/.venv" "$ROOT/.venv-clean"
for old in "$ROOT"/.venv*.bak.* "$ROOT"/.venv*.old.*; do
  [ -e "$old" ] && rm -rf -- "$old"
done
rm -f -- "$ROOT/environment.freeze.txt"

echo "[1/4] Creating clean venv: $VENV"
python3 -m venv "$VENV"

PY="$VENV/bin/python"
echo "[1/4] Python: $($PY --version)"

echo "[2/4] Installing CUDA PyTorch $TORCH_VERSION from $TORCH_INDEX"
$PY -m pip install --upgrade pip setuptools wheel
if [ "$TORCH_VERSION" = "2.7.0" ] && \
   [ -f "$WHEELHOUSE/torch-2.7.0+cu128-cp312-cp312-manylinux_2_28_x86_64.whl" ]; then
  echo "Using bundled offline torch wheelhouse: $WHEELHOUSE"
  if ! $PY -m pip install --no-index --find-links "$WHEELHOUSE" \
      "torch==2.7.0+cu128"; then
    echo "Bundled wheelhouse install failed; falling back to network."
    $PY -m pip install "torch==$TORCH_VERSION" --index-url "$TORCH_INDEX"
  fi
else
  echo "Bundled torch wheel not found; using network."
  $PY -m pip install "torch==$TORCH_VERSION" --index-url "$TORCH_INDEX"
fi

echo "[3/4] Installing video/PPO dependencies"
$PY -m pip install -r "$ROOT/requirements-autodl.txt"
$PY -m pip freeze > "$ROOT/environment.freeze.txt"

echo "[4/4] Verifying complete package"
export MUJOCO_GL=disable
"$PY" "$ROOT/verify_package.py"
"$PY" "$ROOT/detect_autodl_environment.py"
echo "Environment ready. Use: bash train_auto.sh"
