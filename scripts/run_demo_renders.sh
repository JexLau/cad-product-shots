#!/usr/bin/env bash
set -euo pipefail
BLENDER="${BLENDER:-/workspace/blender-install/blender-5.2.0-linux-x64/blender}"
export LD_LIBRARY_PATH="$(dirname "$BLENDER")/lib:${LD_LIBRARY_PATH:-}"
export PYTHONUNBUFFERED=1
SCRIPT="/workspace/cad-product-shots/scripts/render_stills_pipeline.py"
TARGET="${1:?target watchy|ploopy|case01}"
ENGINE="${ENGINE:-EEVEE}"
SAMPLES="${SAMPLES:-32}"
RES="${RES:-1080}"
# Soft-grey live demos: product materials + hide print supports (not white clay).
case "$TARGET" in
  watchy)
    exec "$BLENDER" --background --factory-startup --python "$SCRIPT" -- \
      --glb /workspace/cad-product-shots/media/demo-watchy/source/Yatari_2_Model.glb \
      --out /workspace/cad-product-shots/.render-out/yatari2-stills \
      --repo-stills /workspace/cad-product-shots/media/demo-watchy/stills \
      --shots simple --engine "$ENGINE" --samples "$SAMPLES" --res "$RES" \
      --preset softgrey --radius-scale 2.85 --bg 0.22 --exposure -0.70 --light-scale 0.40 \
      --no-clay --product-mats --hide-supports --watchy-extras --force \
      --only 07-front.jpg,08-three-quarter.jpg,09-top.jpg,12-detail.jpg \
      --no-copy-repo
    ;;
  ploopy)
    exec "$BLENDER" --background --factory-startup --python "$SCRIPT" -- \
      --glb /workspace/cad-product-shots/media/demo-ploopy/source/PloopyHeadphones-RevA.glb \
      --out /workspace/cad-product-shots/media/demo-ploopy/stills \
      --repo-stills /workspace/cad-product-shots/media/demo-ploopy/stills \
      --shots simple --engine "$ENGINE" --samples "$SAMPLES" --res "$RES" \
      --preset softgrey --radius-scale 2.4 --bg 0.20 --exposure -0.75 --light-scale 0.38 \
      --no-clay --product-mats --hide-supports --no-watchy-extras --force
    ;;
  case01)
    exec "$BLENDER" --background --factory-startup --python "$SCRIPT" -- \
      --glb /workspace/previews/generated-story/catellect-product-story-v2-uncompressed.glb \
      --out /workspace/catellect-ops/media/case-01/stills \
      --repo-stills /workspace/cad-product-shots/media/case-01/stills \
      --shots case01 --engine CYCLES --samples 16 --res 1080 \
      --bg 0.26 --exposure -0.55 --light-scale 0.42 --force
    ;;
  *) echo "unknown $TARGET"; exit 2;;
esac
