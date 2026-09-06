# Watchy · Party dark-premium (DJI bar) · 2026-09-07

DoD: `catellect-ops/plans/2026-09-07-demo-dji-bar-dod.md`  
Steering: Steve — **Party** primary (sqfmi/watchy-cases/Party, MIT+STEP). Yatari2 demoted. Slim backup unused.  
Benchmark: `benchmark/mavic-3-pro-product-still-black-studio.png`  
Compare: `compare-08-before-after-dji.jpg`

## What changed

1. **CAD shell:** `Party/` STEP → `scripts/party_assemble.py` → `media/demo-watchy/source/Party_Model.glb` (Top+Bottom+4×Button; Plug omitted). Face oriented −Y for pipeline.
2. **Extras:** Party flush dial → shallow boolean pocket in Bottom + recessed e-ink insert + thin glass + longer demo strap (`scripts/watchy_assemble_extras.py`).
3. **Face:** upstream `Face.png` (softened paper) as e-ink texture — time/date/status glyphs, **no brand logos**.
4. **Lighting:** `--preset dark-premium` featured candidate. Soft-grey only appendix (`appendix-softgrey/` / existing `_preview-sg-*`).
5. **Camera:** flatter / longer lens / more air on 07–08 (`watchy_thin` shot table) to reduce brick mass.

**Not in this PR:** live `07/08/09/12` untouched; landing not un-held (leave #28 construction hold).

## Deliverables

| Path | Role |
| --- | --- |
| `media/demo-watchy/stills/_preview-dark-07/08/09/12.jpg` | **Primary** featured candidates |
| `reviews/.../before/*-live-yatari2.jpg` | Current live Yatari2 |
| `reviews/.../after/*` | Party dark after |
| `reviews/.../benchmark/mavic-*.png` | DJI still |
| `reviews/.../appendix-softgrey/` | Structure appendix only |

## Reproduce

```bash
# STEP parts already under media/demo-watchy/source/party/
/workspace/blender-install/blender-5.2.0-linux-x64/blender --background --factory-startup \
  --python scripts/party_assemble.py

ENGINE=EEVEE SAMPLES=40 RES=1080 scripts/run_demo_renders.sh watchy-dark
# copy .render-out/party-dark-stills/{07,08,09,12}* → stills/_preview-dark-*
```

## Honest self-check vs Rams gates 1–7

| # | Gate | Verdict | Notes |
|---|---|---|---|
| 1 | 3s product not clay/white-mod | **PARTIAL** | Dark studio + satin case + Face glyphs beat Yatari2 white patch; still reads kit/CAD more than DJI consumer finish |
| 2 | Category = watch (screen + strap) | **PASS** | Readable dial UI + strap through 12/6; closed assemble |
| 3 | ≥3 materials + “贵一点” light | **PARTIAL** | Case / e-ink / glass / strap / buttons separated; satin roll-off weaker than DJI; glass glint under-controlled |
| 4 | Deep studio language | **PASS (borderline)** | Near-black bg + dark floor; floor light pool still a bit “lab spot” vs DJI rock/void |
| 5 | Highlights controlled | **PARTIAL** | No huge chalk flood; Face paper still relatively bright vs DJI micro-spec; case rim uneven |
| 6 | Breathing room | **PASS** | Thin camera + radius_scale ~3.55; subject not edge-cropped |
| 7 | Honest demo | **PASS** | Demo · open CAD; MIT Party; no fake Apple/logos |

**Featured ship?** **NO** — not full 1–7. Good enough for Steve preview / Yellow discussion; **do not promote live**.

## Still short vs DJI bar

- Party geometry is thin (~5 mm) but **face slots + clip tabs** still kit-like; camera cannot fully erase DIY read.
- E-ink Face remains **high-key paper** under glass — not dark coated optics like DJI lenses.
- Strap is straight demo bars (continuity yes, wrist curve no).
- Rim energy / material micro-response still below Mavic still.
- If Party stalls visually, next CAD fork is Slim V4.5.3 (scout primary historically) — not done here per Steve Party-first.

## Attribution

Case CAD: **Party by SQFMI**, MIT — https://github.com/sqfmi/watchy-cases/tree/main/Party  
Face art: upstream `Party/Face.png` (softened for dark studio).
