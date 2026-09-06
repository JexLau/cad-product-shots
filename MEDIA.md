# Media drop-in convention

Case #1 proof slots that have landed are wired in `index.html`. This file stays the slot map so later stills can drop in without renaming HTML or CSS.

Do **not** commit stock photos, fake 3D, or AI-purple stand-ins. Skip a numbered file until the still is real.

## Layout

```
media/
  case-01/
    stills/          # Case #1 stills (hero + case slots)
    clip/            # Optional orbit / ≤15s motion
  og/
    share.jpg        # 1200×630 Open Graph / Twitter card
```

`index.html` points `<figure>` slots at these paths via `data-media`. Real files use `<img>` or `<video>` at the same path.

## Case #1 stills — `media/case-01/stills/`

| File | Use on page | Status |
| --- | --- | --- |
| `01-ghost-perspective.jpg` | Hero slot **and** Case featured slot (full-width) | **On the page.** Same asset in both places. |
| `02-white-bg-a.jpg` | Case 2-up grid | **On the page.** |
| `03-white-bg-b.png` | Case 2-up grid — open-lid hero | **On the page.** Landed as PNG. |
| `04-white-bg-c.png` | Case 2-up grid | **On the page.** Landed as PNG. Pack’s 3 white-background stills are now on the page. |
| `05-studio-a.jpg` | Case 2-up grid — studio / detail | **On the page.** |
| `06-studio-b.png` | Case 2-up grid — yellow-post detail | **On the page.** Landed as PNG. Pack’s 2 studio / detail stills are now on the page. |
| `07-front.jpg` | Case gallery | **On the page.** Pipeline multi-angle (front). |
| `08-three-quarter.jpg` | Case gallery | **On the page.** Pipeline multi-angle (3/4). |
| `09-top.jpg` | Case gallery | **On the page.** Pipeline multi-angle (top). |
| `10-orbit-a.jpg` | Case gallery | **On the page.** Pipeline multi-angle (orbit). |
| `11-orbit-b.jpg` | Case gallery | **On the page.** Pipeline multi-angle (orbit). |
| `12-detail.jpg` | Case gallery | **On the page.** Pipeline multi-angle (detail). |
| `13-open-three-quarter.jpg` | Case gallery | **On the page.** Pipeline multi-angle (open lid). |
| `14-open-front.jpg` | Case gallery | **On the page.** Pipeline multi-angle (open lid). |

Preferred: JPEG or WebP, long edge ≥1600px, sRGB. Name, do not invent, the missing numbers.

## Case #1 clip — `media/case-01/clip/`

| File | Use | Status |
| --- | --- | --- |
| `01-orbit.mp4` | 360 / multi-angle orbit (or equivalent). H.264 + AAC, ≤15s if it is the short clip. | **On the page** as a muted `<video>` (poster = `01-ghost-perspective.jpg`). |
| `01-orbit.webm` | Optional companion for `<video>`. | Not on the page yet. |

Poster still reuses `01-ghost-perspective.jpg`. A dedicated `01-orbit-poster.jpg` in `stills/` can replace it later.

## Open Graph — `media/og/share.jpg`

| File | Spec | Status |
| --- | --- | --- |
| `share.jpg` | **1200×630**, JPEG, sRGB. Crop from a real Case #1 still. | **On the page.** |

HTML points crawlers here:

- `og:image` / `twitter:image` → `https://jexlau.github.io/cad-product-shots/media/og/share.jpg`
- `og:image:width` 1200, `og:image:height` 630
- `twitter:card` is `summary_large_image`

If the site moves to a custom domain, update the absolute URLs in `index.html` to match.

## What this page must not gain

- Stock / marketplace “3D product” images
- AI-generated purple / neon stand-ins
- Invented Case #1 photography


## Demo · open CAD packs

| Pack | Path | License | Landing | Hard line |
| --- | --- | --- | --- | --- |
| Open headphones | `media/demo-ploopy/` | CERN-OHL-S-2.0 | **On the page** — live qualified demo; **material-passed stills only** (`08` featured + `07`, `09`, `12`) | No endorsement / fake brand / logo |
| Open e-ink watch case | `media/demo-watchy/` | MIT (SQFMI Yatari2) | **Held / 施工中** — gallery withheld pending next remodel iteration | Not Apple Watch; not “Watchy” shelf name |

Demo gallery shows **material-passed stills only**. Ploopy clay / truss angles `10-orbit-a`, `11-orbit-b`, `13-rear-three-quarter`, `14-low-angle` stay on disk under `media/demo-ploopy/stills/` and are **not** wired in `index.html` until a full re-render. Do not delete those JPGs.

Primary source for the watch pack is SQFMI Yatari2 (`source/Yatari_2_Model.step` + demo assemble GLB). Armadillonium archived under `source/archive-armadillonium/`. Featured stills `07/08/09/12` and `_preview-sg-*` copies remain in-repo; do not wire them back onto the landing until the next iteration passes. Still **Demo · open CAD** — no trademark claim.

Pipeline: `scripts/render_stills_pipeline.py` (`--glb`/`--step`/`--stl`/`--obj`). STEP → GLB via `scripts/step_to_glb.py` when Blender lacks a CAD importer.
