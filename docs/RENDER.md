# Case #1 — one-click multi-angle stills

Headless Blender EEVEE script that imports the Catellect product-story GLB,
applies a white-background studio lighting preset, and writes new marketing
stills into `media/case-01/stills/` using MEDIA.md-friendly names (`07+`,
`10-orbit-*`). It does **not** overwrite `01`–`06`.

## One command

```bash
bash scripts/run_case01_stills.sh /workspace/catellect-ops/media/case-01/stills
```

Equivalent expanded form:

```bash
LD_LIBRARY_PATH=/workspace/blender-install/blender-5.2.0-linux-x64/lib:$LD_LIBRARY_PATH \
  /workspace/blender-install/blender-5.2.0-linux-x64/blender --background --factory-startup \
  --python scripts/render_case01_stills.py -- \
  --out /workspace/catellect-ops/media/case-01/stills
```

By default the script also copies outputs into this repo’s
`media/case-01/stills/` (omit with `--no-copy-repo`).

## Flags

| Flag | Default |
| --- | --- |
| `--out` | `/workspace/catellect-ops/media/case-01/stills` |
| `--res` | `1080` (square JPEG) |
| `--glb` | first existing among uncompressed / story GLBs |
| `--force` | off (still refuses to overwrite `01`–`06`) |
| `--no-copy-repo` | skip copy into repo `media/case-01/stills/` |

## Outputs

| File | Angle / pose |
| --- | --- |
| `07-front.jpg` | Front, lid closed |
| `08-three-quarter.jpg` | 3/4, lid closed |
| `09-top.jpg` | Top / plan |
| `10-orbit-a.jpg` | Side orbit |
| `11-orbit-b.jpg` | Rear-quarter orbit |
| `12-detail.jpg` | Closer detail |
| `13-open-three-quarter.jpg` | 3/4, lid open (story frame ~28) |
| `14-open-front.jpg` | Front, lid open |

Geometry source: product-story GLB (same Case #1 CAD path). No fake / stock images.
