#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -x "$ROOT/.venv-clean/bin/python" ]; then
  PY="${PYTHON:-$ROOT/.venv-clean/bin/python}"
else
  PY="${PYTHON:-python3}"
fi

exec "$PY" "$ROOT/detect_autodl_environment.py"
