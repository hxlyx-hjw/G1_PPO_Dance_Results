#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Removing Python environments and environment backups..."
rm -rf -- "$ROOT/.venv" "$ROOT/.venv-clean"
for old in "$ROOT"/.venv*.bak.* "$ROOT"/.venv*.old.*; do
  [ -e "$old" ] && rm -rf -- "$old"
done

echo "Removing Python caches..."
find "$ROOT/code" -type d -name __pycache__ -prune -exec rm -rf -- {} +
find "$ROOT/code" -type d -name .pytest_cache -prune -exec rm -rf -- {} +
rm -f -- "$ROOT/environment.freeze.txt"

echo "Environment reset complete."
echo "Preserved: code/, assets/, data/, outputs/, runtime/"
