#!/usr/bin/env bash
# One-click Case #1 multi-angle stills (Blender EEVEE headless).
set -euo pipefail
BLENDER="${BLENDER:-/workspace/blender-install/blender-5.2.0-linux-x64/blender}"
LIBDIR="$(dirname "$BLENDER")/lib"
export LD_LIBRARY_PATH="${LIBDIR}:${LD_LIBRARY_PATH:-}"
export PYTHONUNBUFFERED=1
OUT="${1:-/workspace/catellect-ops/media/case-01/stills}"
SCRIPT="$(cd "$(dirname "$0")" && pwd)/render_case01_stills.py"
shift || true
exec "$BLENDER" --background --factory-startup --python "$SCRIPT" -- --out "$OUT" "$@"
