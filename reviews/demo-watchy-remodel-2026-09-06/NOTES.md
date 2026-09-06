# Watchy remodel — Yatari2 (Rams DoD) · 2026-09-06

Rams DoD: `catellect-ops/plans/2026-09-06-watchy-remodel-dod.md`  
Source table: `catellect-ops/research/2026-09-06-watchy-open-cad-sources.md`  
Steering: Yatari2 ＞ Party ＞ Slim (Steve/Feynman). Peechy / Apple / NC / yik3z excluded.

## Problem

Live Armadillonium reads as thick brick / battery shell: solid same-material face, weak strap read. Materials alone cannot pass. Landing Watchy hidden in #25 until remodel clears Rams.

## Approach

**Primary CAD:** SQFMI **Yatari2** MIT — `Yatari_2_Model.step` (+ Top/Bottom/Button STLs) via https://github.com/sqfmi/watchy-cases/tree/main/Yatari2

1. STEP → GLB with `scripts/step_to_glb.py` (cascadio); buttons already placed in STEP assembly.
2. Pipeline extras (`scripts/watchy_assemble_extras.py`, `--watchy-extras`):
   - **Boolean dial window** into front shell (STEP face is a solid plate — paint-only would fail DoD #2).
   - Recessed **e-ink screen insert** plane (light matte, distinct from case).
   - **Split demo strap** through 12/6 lug slots + under-case bridge + keepers/buckle (no logos).
3. Soft-grey product mats: dark satin case / light screen / light-grey buttons / soft dark strap.
4. Preview-only stills: `_preview-sg-07/08/09/12` — **live featured 07+ untouched**.

## Attribution

Case CAD: **Yatari2 by SQFMI**, MIT License — https://github.com/sqfmi/watchy-cases/tree/main/Yatari2  
Page caption stays **Demo · open CAD** / open e-ink watch case (not a shelf trademark).

## Source layout

`media/demo-watchy/source/`

- `Yatari_2_Model.step` / `.glb` / Top·Bottom·Button STLs
- `Yatari_2_DemoAssemble.glb` — demo extras baked (screen + strap)
- `LICENSE-MIT.txt` (+ `LICENSE-MIT-Yatari2.txt`)
- `archive-armadillonium/` — prior primary kept off featured

## Self-check vs Rams 1–5

| # | Gate | Verdict | Notes |
|---|---|---|---|
| 1 | 3s recognizable as a watch | **PASS** | Screen + side buttons + strap ends read as wristwatch |
| 2 | Dial/screen readable | **PASS** | Boolean window + light e-ink insert ≠ same-material brick face |
| 3 | Strap / lug–strap readable | **PASS** | Strap enters 12/6 slots; bridge under case |
| 4 | Not a brick | **PASS (borderline)** | Yatari2 remains chunky kit shell, but wearable watch read clears vs Armadillonium brick |
| 5 | 07+08 closed assembled wearable | **PASS** | Closed case + screen + strap; upright demo orientation |

## Preview policy

Soft-grey frames land as `_preview-sg-*` only. **Do not promote live** until Steve Yellow / Rams visual pass. Do not undo #25 hide.

## Reproduce

```bash
# optional STEP refresh
.venv-cad/bin/python scripts/step_to_glb.py \
  media/demo-watchy/source/Yatari_2_Model.step \
  media/demo-watchy/source/Yatari_2_Model.glb

ENGINE=EEVEE SAMPLES=48 RES=1080 scripts/run_demo_renders.sh watchy
# then copy .render-out/yatari2-stills/{07,08,09,12}* → stills/_preview-sg-*
```

## Slim note

Slim V4.5.3 scouted earlier; **not** formal source per steering. No Slim stills committed as primary.
