# Watchy · Party dark-premium knife-3 · 2026-09-07-v3

- DoD: `catellect-ops/plans/2026-09-07-demo-dji-bar-dod.md`
- Gate (knife-2 FAIL): `catellect-ops/reviews/2026-09-07-watchy-knife2-dji-bar-gate.md`
- Steering: Steve — stay on **Party** (no Slim); clip assembly first, then eink/mats/Ploopy light
- Prior: PR #32 knife-2 preview — **featured still held**
- Benchmark: `benchmark/mavic-3-pro-product-still-black-studio.png`
- Compare: `compare-08-before-after-dji.jpg` · `compare-07-before-after-dji.jpg` — columns **#32 after | knife-3 | DJI**

## Knife-3 changes (vs PR #32)

1. **Clips / DIY face retainers (priority):** PartyTop clip plate **hidden**; flush **consumer bezel** replaces wedge teeth on glass. Party side buttons that invaded the dial (read as 4 on-glass clips) **tucked to outer ±X walls**.
2. **Screen:** opaque **light-grey e-ink paper** (`eink_face_paper_light.png`) + opaque backplate + thinner Fresnel glass (low alpha). Time readable; cavity must not read through.
3. **Case mats:** deep satin engineering plastic (finer micro-grain) + **tiny cold-metal** only on short lug/bevel ticks (not uniform silver shell).
4. **Lighting:** same dark-premium language as Ploopy PASS 08 (near-void + rim/kicker); no exposure-only cheat.

**Not in this PR:** live `07/08/09/12` untouched; landing stay held; no Slim fork; no fake brands; UI contrast not further crushed.

## Deliverables

| Path | Role |
| --- | --- |
| `media/demo-watchy/stills/_preview-dark-07/08/09/12.jpg` | Featured **candidates** only |
| `reviews/...-v3/before/*-pr32.jpg` | #32 after (FAIL featured) |
| `reviews/...-v3/after/*` | knife-3 after |
| `reviews/...-v3/compare-08-before-after-dji.jpg` | 三列 08: #32 \| knife-3 \| DJI |
| `reviews/...-v3/compare-07-before-after-dji.jpg` | 三列 07: #32 \| knife-3 \| DJI |

## Reproduce

```bash
ENGINE=CYCLES SAMPLES=64 RES=1080 scripts/run_demo_renders.sh watchy-dark
# copy .render-out/party-dark-stills/{07,08,09,12}* → stills/_preview-dark-*
```

## Honest self-check vs Rams gates 1–7

| # | Gate | Verdict | Notes |
|---|---|---|---|
| 1 | 3s product not clay/kit-CAD | **PASS (stronger)** | Consumer bezel + opaque paper; DIY face clips removed |
| 2 | Category = watch | **PASS** | Screen UI + strap readable |
| 3 | ≥3 mats + “贵一点” light | **PARTIAL → near** | Case satin ≠ lug/bevel metal ≠ silicone ≠ glass ≠ paper; still short of DJI micro-spec richness |
| 4 | Deep studio language | **PASS** | Near-black void; Ploopy-ratio rim/kicker retained |
| 5 | Highlights controlled | **PARTIAL → stronger** | No clip wedge as brightest geometry; paper opaque; side ports/lugs catch some light; glass Fresnel restrained |
| 6 | Breathing room | **PASS** | Thin camera / radius_scale 3.55 |
| 7 | Honest demo | **PASS** | Demo · open CAD; MIT Party; Face glyphs only; no fake brands |

**Featured ship?** **NO — do not claim full 1–7 PASS until Rams re-check.** Knife-3 addresses clip dominance + opaque paper + local metal; **do not promote live / do not unhold landing.**

## Still short vs DJI / Ploopy pass

- Strap remains a straight demo bar (no wrist curve).
- Cold-metal ticks are intentional and tiny — may still read soft vs DJI hardware pages.
- Party CAD silhouette is still a kit window case under the bezel language.

## Attribution

Case CAD: **Party by SQFMI**, MIT — https://github.com/sqfmi/watchy-cases/tree/main/Party  
Face: upstream `Party/Face.png` (paper-light toned for studio).
