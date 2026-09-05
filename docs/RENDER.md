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

Lighting: soft-grey studio (not paper-white), size-scaled area lights,
`--exposure` / `--light-scale` / `--bg` knobs. Defaults bias toward readable
product contrast (avoid blown white).

## Hard line

No brand-official images / fake logos. Demo · open CAD labels only.
