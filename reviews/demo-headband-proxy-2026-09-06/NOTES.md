# Ploopy headband proxy — 2026-09-06

Follow-up to #18 (`demo-material-stand-2026-09-06`).  
Rams DoD: `catellect-ops/plans/2026-09-06-demo-material-stand-dod.md` · gate **#4** wearable/assembled silhouette.

## Blocker (#18 LIVE_PROMOTE FAIL)

Hiding HPH-035 (bare serpentine flexbars) removed the only headband bridge. Featured 07/08 read as two floating earcups.

## Fix

Procedural **quiet fabric arc** in `scripts/render_stills_pipeline.py` → `add_ploopy_headband_proxy()`:

1. Detect earcups HPH-013 / HPH-018 world bboxes.
2. Build an elliptical C-path (crown + side yokes into outer cup faces).
3. Sweep a soft oval tube mesh; Principled fabric (`Prod_HeadbandProxy` / sheen, dark grey, high roughness).
4. Not print lattice / not serpentine / no brand logos.

CLI: on by default; `--no-headband-proxy` to disable.

## Still hidden (print junk)

| Mesh | Why |
| --- | --- |
| HPH-039 | Lattice stand + base |
| HPH-038 | Ghost duplicate flexbars |
| HPH-036 | Tripod / jig lattice |
| HPH-035 | Bare serpentine flexbars |

When proxy is on, also hide one-sided stubs **HPH-037 / HPH-033** (no left twin in this GLB — otherwise right-yoke-only fights the quiet arc).

**Kept product:** HPH-013/018 earcups, HPH-032 driver rings.

## Watchy

Stronger case (cool charcoal) / insert (warm mid) / button (near-black, slightly specular) separation — no headband path.

## Still policy

Live featured `07`/`08` **not** swapped. Soft-grey frames:

- `media/demo-ploopy/stills/_preview-sg-07.jpg` / `_preview-sg-08.jpg`
- `media/demo-watchy/stills/_preview-sg-07.jpg` / `_preview-sg-08.jpg`

Propose live promote after Steve/Grok PASS on Rams #4 (+ #1–3/#5 from #18).

## Self-check Rams #4

Featured pose = continuous wearable/assembled silhouette readable at ~1m (arc + yokes bridge both cups; no floating pair).
