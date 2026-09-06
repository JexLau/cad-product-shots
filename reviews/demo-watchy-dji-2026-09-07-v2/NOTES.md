# Watchy · Party dark-premium knife-2 · 2026-09-07-v2

- DoD: `catellect-ops/plans/2026-09-07-demo-dji-bar-dod.md`
- Gate (prior FAIL): `catellect-ops/reviews/2026-09-07-watchy-dji-bar-gate.md`
- Steering: Steve — stay on **Party** (no Slim); knife order ①mats ②rim ③glass ④strap
- Prior: PR #31 merged preview archive — **featured still held**
- Benchmark: `benchmark/mavic-3-pro-product-still-black-studio.png`
- Compare: `compare-08-before-after-dji.jpg` · `compare-07-before-after-dji.jpg`

## Knife-2 changes (vs PR #31)

1. **Case mats:** charcoal satin engineering plastic (rough ~0.58, low coat) + micro grain; **local cold metal only on strap lugs** — remove uniform silver-spray shell.
2. **Rim/kicker:** Ploopy-pass dark lighting ratio; Watchy absolute energy cut so flat shell stays charcoal (not washed silver); near-void floor (gate 4).
3. **Screen:** thinner cover glass (Fresnel coat + light alpha); Face.png kept but **dark-toned** (`eink_face_dark_toned.png` + HSV) — muted e-ink paper, not chalk sticker.
4. **Strap:** wider/thinner silicone proportions, single soft keeper, tip in silicone family (not bright buckle plate), light bevel — less industrial rail.

**Not in this PR:** live `07/08/09/12` untouched; landing stay held; no Slim fork.

## Deliverables

| Path | Role |
| --- | --- |
| `media/demo-watchy/stills/_preview-dark-07/08/09/12.jpg` | Featured **candidates** only |
| `reviews/...-v2/before/*-pr31.jpg` | #31 after (FAIL featured) |
| `reviews/...-v2/after/*` | knife-2 after |
| `reviews/...-v2/compare-08-before-after-dji.jpg` | 三列 08 |
| `reviews/...-v2/compare-07-before-after-dji.jpg` | 三列 07 |

## Reproduce

```bash
ENGINE=CYCLES SAMPLES=56 RES=1080 scripts/run_demo_renders.sh watchy-dark
# copy .render-out/party-dark-stills/{07,08,09,12}* → stills/_preview-dark-*
```

## Honest self-check vs Rams gates 1–7

| # | Gate | Verdict | Notes |
|---|---|---|---|
| 1 | 3s product not clay/kit-CAD | **PARTIAL → stronger** | Charcoal satin + muted dial beat #31 silver spray; Party **clip tabs / kit window** still DIY-read — geometry limit, not paint |
| 2 | Category = watch | **PASS** | Screen UI + strap readable |
| 3 | ≥3 mats + “贵一点” light | **PARTIAL / near** | Case plastic ≠ lug metal ≠ silicone ≠ glass ≠ buttons; roll-off closer to Ploopy luminance (~case p50≈100 vs Ploopy ~79); still short of DJI micro-spec richness |
| 4 | Deep studio language | **PASS (improved)** | Near-black void; lab floor pool largely gone vs #31 soft grey pool |
| 5 | Highlights controlled | **PARTIAL** | No chalk flood on Face; bevel rim glints present; Party facets still catch hard edges |
| 6 | Breathing room | **PASS** | Thin camera / radius_scale 3.55 |
| 7 | Honest demo | **PASS** | Demo · open CAD; MIT Party; Face glyphs only; no fake brands |

**Featured ship?** **NO — still not full 1–7.** Knife-2 is the right direction for Rams re-check on 3+5; **do not promote live / do not unhold landing.**

## Still short vs DJI / Ploopy pass

- Party flush-window **retaining clips** read kit regardless of mats.
- Strap is better silicone but still a straight demo bar (no wrist curve).
- Glass Fresnel is restrained (readable UI first); not coated-optic drama.
- If Party remains hopeless after Rams re-check → Slim V4.5.3 is the CAD fork (not this PR).

## Attribution

Case CAD: **Party by SQFMI**, MIT — https://github.com/sqfmi/watchy-cases/tree/main/Party  
Face: upstream `Party/Face.png` (dark-toned for studio).
