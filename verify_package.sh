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
export MUJOCO_GL=disable
export PYTHONPATH="$ROOT/code"
exec "$PY" "$ROOT/verify_package.py"
