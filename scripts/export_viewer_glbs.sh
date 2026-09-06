#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BLENDER="${BLENDER:-/workspace/blender-install/blender-5.2.0-linux-x64/blender}"
if [[ ! -x "$BLENDER" ]]; then
  echo "ERROR: blender not found at $BLENDER" >&2
  exit 2
fi
export LD_LIBRARY_PATH="$(dirname "$BLENDER")/lib:${LD_LIBRARY_PATH:-}"
export PYTHONUNBUFFERED=1
TARGET="${1:-all}"
exec "$BLENDER" --background --factory-startup --python "$ROOT/scripts/export_viewer_glb.py" -- --target "$TARGET"
