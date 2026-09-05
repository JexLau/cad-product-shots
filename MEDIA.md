# Media drop-in convention

Real Case #1 stills and the share card are **not in this repo yet**. This file is the slot map so assets can land without renaming HTML or CSS.

Do **not** commit stock photos, fake 3D, or AI-purple stand-ins. Wireframes in `index.html` stay until Jex drops real frames.

## Layout

```
media/
  case-01/
    stills/          # Case #1 stills (hero + case slot)
    clip/            # Optional orbit / ≤15s motion
  og/
    share.jpg        # 1200×630 Open Graph / Twitter card (TBD)
```

`index.html` points reserved `<figure>` slots at these paths via `data-media`. Replace the wireframe stage with an `<img>` (or `<video>`) using the same path when the file exists.

## Case #1 stills — `media/case-01/stills/`

| File | Use on page | Notes |
| --- | --- | --- |
| `01-ghost-perspective.jpg` | Hero reserved slot **and** Case featured slot | First still to ship. Same asset is fine in both places. |
| `02-white-bg-a.jpg` | Optional extra still | Not rendered until a real file exists. |
| `03-white-bg-b.jpg` | Optional extra still | |
| `04-white-bg-c.jpg` | Optional extra still | Pack calls for 3 white-background stills. |
| `05-studio-a.jpg` | Optional extra still | |
| `06-studio-b.jpg` | Optional extra still | Pack calls for 2 studio / detail stills. |

Preferred: JPEG or WebP, long edge ≥1600px, sRGB. Name, do not invent, the missing numbers — skip a file until the still is real.

## Case #1 clip — `media/case-01/clip/`

| File | Use |
| --- | --- |
| `01-orbit.mp4` | 360 / multi-angle orbit (or equivalent). H.264 + AAC, ≤15s if it is the short clip. |
| `01-orbit.webm` | Optional companion for `<video>`. |

Poster still can reuse `01-ghost-perspective.jpg` or a dedicated `01-orbit-poster.jpg` in `stills/`.

## Open Graph — `media/og/share.jpg`

| File | Spec |
| --- | --- |
| `share.jpg` | **1200×630**, JPEG, sRGB. Crop from a real Case #1 still when one exists. |

HTML already has the slot:

- `og:image` / `twitter:image` → `https://jexlau.github.io/cad-product-shots/media/og/share.jpg`
- `og:image:width` 1200, `og:image:height` 630

Until `share.jpg` is committed, crawlers may 404 that URL. Do not point the meta tags at a fake product render. If the site moves to a custom domain, update the absolute URLs in `index.html` to match.

`twitter:card` stays `summary` until a real share image exists; switch to `summary_large_image` in the same change that adds `share.jpg`.

## What this page must not gain

- Stock / marketplace “3D product” images
- AI-generated purple / neon stand-ins
- Invented Case #1 photography
