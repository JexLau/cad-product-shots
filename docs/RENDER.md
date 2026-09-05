# CAD stills render pipeline

Headless Blender script: import GLB / OBJ / STL / STEP, white-bg studio lights, write `07+` stills without overwriting `01`–`06`.

## One command

```bash
./scripts/run_case01_stills.sh /workspace/catellect-ops/media/case-01/stills
```

```bash
./scripts/run_case01_stills.sh /path/to/out -- --glb /path/to/model.glb --engine CYCLES --samples 32
./scripts/run_case01_stills.sh /path/to/out -- --stl media/demo-ce/source/Main-Enclosure.stl --shots simple
./scripts/run_case01_stills.sh /tmp/step-out -- --step /path/to/assembly.step   # clear error if no importer
```

Stock Blender 5.2 has no STEP importer. Use `scripts/step_to_glb.py` (cascadio) then `--glb`, or install a CAD addon.

Default engine: **Cycles CPU** (headless-safe). Demo · open CAD: `media/demo-ce/` (MouDio MIT speaker).
