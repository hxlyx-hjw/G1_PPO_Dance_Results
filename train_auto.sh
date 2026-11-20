#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROFILE_FILE="${PROFILE_FILE:-$ROOT/profiles/autodl_detected.env}"

if [ ! -f "$PROFILE_FILE" ]; then
  bash "$ROOT/prepare_config.sh"
fi

set -a
# shellcheck disable=SC1090
source "$PROFILE_FILE"
set +a

echo "Using profile: $PROFILE_NAME"
echo "GPU: $GPU_NAME (${GPU_MEMORY_MB} MB)"
echo "ENVS: $ENVS | ITERATIONS: $ITERATIONS | DEVICE: $DEVICE"
echo "OUTPUT: $OUTPUT"

exec bash "$ROOT/train_dance_gpu.sh"
