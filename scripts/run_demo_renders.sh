#!/usr/bin/env bash
set -euo pipefail
BLENDER="${BLENDER:-/workspace/blender-install/blender-5.2.0-linux-x64/blender}"
export LD_LIBRARY_PATH="$(dirname "$BLENDER")/lib:${LD_LIBRARY_PATH:-}"
export PYTHONUNBUFFERED=1
SCRIPT="/workspace/cad-product-shots/scripts/render_stills_pipeline.py"
TARGET="${1:?target watchy|ploopy|case01}"
# Prefer EEVEE for demo packs: lower RAM, faster; Cycles still available via ENGINE=CYCLES
ENGINE="${ENGINE:-EEVEE}"
SAMPLES="${SAMPLES:-32}"
RES="${RES:-1080}"
case "$TARGET" in
  watchy)
    exec "$BLENDER" --background --factory-startup --python "$SCRIPT" -- \
      --glb /workspace/cad-product-shots/media/demo-watchy/source/Armadillonium_Model.glb \
      --out /workspace/cad-product-shots/media/demo-watchy/stills \
      --repo-stills /workspace/cad-product-shots/media/demo-watchy/stills \
      --shots simple --engine "$ENGINE" --samples "$SAMPLES" --res "$RES" \
      --radius-scale 2.6 --bg 0.68 --force
    ;;
  ploopy)
    exec "$BLENDER" --background --factory-startup --python "$SCRIPT" -- \
      --glb /workspace/cad-product-shots/media/demo-ploopy/source/PloopyHeadphones-RevA.glb \
      --out /workspace/cad-product-shots/media/demo-ploopy/stills \
      --repo-stills /workspace/cad-product-shots/media/demo-ploopy/stills \
      --shots simple --engine "$ENGINE" --samples "$SAMPLES" --res "$RES" \
      --radius-scale 2.4 --bg 0.68 --clay --force
    ;;
  case01)
    exec "$BLENDER" --background --factory-startup --python "$SCRIPT" -- \
      --glb /workspace/previews/generated-story/catellect-product-story-v2-uncompressed.glb \
      --out /workspace/catellect-ops/media/case-01/stills \
      --repo-stills /workspace/cad-product-shots/media/case-01/stills \
      --shots case01 --engine CYCLES --samples 16 --res 1080
    ;;
  *) echo "unknown $TARGET"; exit 2;;
esac
