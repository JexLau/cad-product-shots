# Ploopy · DJI-bar dark-premium — 2026-09-07

Rams DoD: `catellect-ops/plans/2026-09-07-demo-dji-bar-dod.md` (gates 1–7)

## Problem

Live Demo gallery mixes white-clay 10/11/13/14 with soft-grey product-mats 07–09/12.
Jex raised acceptance to **DJI ad-tier**. Soft-grey is readable CAD only — **not** featured.

## Approach

- **Featured candidate:** `--preset dark` (near-black studio, high rim/kicker) + `--product-mats` + `--hide-supports` + headband join proxy (#18–#24).
- Engine: Cycles 48 @ 1080 — DJI-track sample knobs from `docs/RENDER.md`.
- **Dark-premium charcoal palette** (pipeline): under `lighting=dark`, earcup shell drops to charcoal satin + stronger coat; pad stays warm soft; driver mesh metallic; fabric headband darker. Soft-grey product palette unchanged for softgrey preset.
- Dark studio lights: rim/kicker up, fill down so charcoal edges stay readable.
- Supports HPH-039/038/036/035 hidden; headband proxy joins outer-top pads.

## Preview policy

| Track | Paths | Role |
| --- | --- | --- |
| **dark-premium** | `media/demo-ploopy/stills/_preview-dark-07.jpg` … `_preview-dark-14.jpg` | **Only** featured candidate |
| soft-grey | existing `_preview-sg-07/08/09/12` | Structure appendix — **not** featured |

**Live `07+` unchanged** until Steve/Rams PASS (Yellow). **Promoted** after Rams PASS on featured 08 + Steve LIVE PASS: `_preview-dark-07` … `_preview-dark-14` copied to live `07-front.jpg` … `14-low-angle.jpg`. `_preview-dark-*` kept. Soft-grey `_preview-sg-*` stay appendix-only. Gallery restored (`08` featured + `07/09/10/11/12/13/14`).

Helper: `scripts/run_demo_renders.sh ploopy-dark` (scratch under `.render-out/`; copy to `_preview-dark-*` after visual pass). Soft-grey full 07–14: `ploopy` target now lists all 8 angles + `--no-copy-repo`.

## Review pack

- `before/` — live soft-grey (07/08) + live clay (10/11/13/14)
- `after/` — dark-premium previews (all 07–14)
- `benchmark/` — DJI Mavic 3 Pro black-studio still
- `compare-ploopy-{07,08,10,11,13,14}.jpg` — before | after | DJI

## Self-check vs gates 1–7

1. Product not clay/mud at thumbnail — charcoal satin + tan pad + dark mesh
2. Wearable closed headphones; no stand/truss (HPH-039 etc hidden)
3. ≥3 materials + satin shell coat micro-highlights under rim
4. Near-black deep studio (not lab soft-grey)
5. Controlled highlights; detail readable in dark
6. Breathing room (`radius_scale` ~2.95 dark preset)
7. Demo · open CAD; no fake logos

## Promote (this PR)

Rams PASS on featured 08. Steve LIVE PASS: promote dark-premium to live. Watchy still held (#28). Soft-grey is appendix only.

## Do not promote (historical)

Hold was: live swap until Steve Yellow + Rams re-check. Watchy remains out of scope.
