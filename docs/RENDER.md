# CAD stills render pipeline

`scripts/render_stills_pipeline.py` (also `render_case01_stills.py`) accepts
`--glb` / `--obj` / `--stl` / `--step`, writes `07+` stills, never overwrites `01`–`06`.

## STEP

Stock Blender 5.2 has no STEP importer. Tessellate first:

```bash
python3 -m venv /tmp/cad-venv && /tmp/cad-venv/bin/pip install cascadio
/tmp/cad-venv/bin/python scripts/step_to_glb.py path/to/model.step path/to/model.glb --tol-linear 0.1
```

Native `--step` fails clearly if no CAD addon is present.

## Run

```bash
./scripts/run_demo_renders.sh case01   # Catellect GLB → media/case-01/stills
./scripts/run_demo_renders.sh ploopy   # open headphones
./scripts/run_demo_renders.sh watchy   # open e-ink watch case
```

## Lighting (P0 contrast)

Soft-grey controlled studio — **not** paper-white cyclorama:

- World `--bg` ~0.20–0.26 (soft grey)
- Floor darker than world for edge separation
- Size-scaled area lights with high key:fill ratio (`--light-scale`)
- AgX High Contrast + `--exposure` pull-down to avoid blown highlights
- Clay / dampened GLB materials for readable form


## Studio-dark preset (DJI-track sample)

Near-black backdrop + high rim/kicker contrast. Does **not** replace the soft-grey
live pack — keep `--preset softgrey` (default) for readable CAD DoD stills.

Single-shot Watchy three-quarter preview:

```bash
BLENDER=/workspace/blender-install/blender-5.2.0-linux-x64/blender
OUT=/tmp/watchy-dark-preview
mkdir -p "$OUT"
"$BLENDER" -b -P scripts/render_stills_pipeline.py -- \
  --glb media/demo-watchy/source/Armadillonium_Model.glb \
  --shots simple --only 08-three-quarter.jpg \
  --preset dark --engine CYCLES --samples 64 --res 1080 \
  --out "$OUT" --no-copy-repo --force
cp "$OUT/08-three-quarter.jpg" media/demo-watchy/stills/_preview-dark-08.jpg
```

Same knobs for Ploopy (`media/demo-ploopy/source/PloopyHeadphones-RevA.glb` → `media/demo-ploopy/stills/_preview-dark-08.jpg`).
Same knobs for Case#1 (`catellect-product-story-v2` GLB → `media/case-01/stills/_preview-dark-08.jpg`).
Same knobs for Case#1 top/detail (`_preview-dark-09.jpg`, `_preview-dark-12.jpg`; Rim 32 / Kicker 14 render-time).

`--preset dark` (alias: `studio-dark`) sets roughly `--bg 0.03`, dialed-down rim/key/kicker
(Rim energy ~28), weaker GLB dampen + satinize (not clay), exposure ~-0.65 / light-scale ~0.34 for dark bg,
slightly higher `--radius-scale`, and a Cycles shadow-catcher floor so the slab does not blow out.
Explicit CLI flags still override preset knobs. Soft-grey defaults remain unchanged.

## Hard line

No brand-official images / fake logos. Demo · open CAD labels only.
