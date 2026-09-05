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
| `01-ghost-perspective.jpg` | Hero slot **and** Case featured slot | **On the page.** Same asset in both places. |
| `02-white-bg-a.jpg` | Case extra still | **On the page.** |
| `03-white-bg-b.jpg` | Optional extra still | Not on the page yet. |
| `04-white-bg-c.jpg` | Optional extra still | Not on the page yet. Pack calls for 3 white-background stills. |
| `05-studio-a.jpg` | Case studio / detail slot | **On the page.** |
| `06-studio-b.jpg` | Optional extra still | Not on the page yet. Pack calls for 2 studio / detail stills. |

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
