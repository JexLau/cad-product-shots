# Design notes

Service landing for geometry-faithful CAD marketing assets. One scroll. No product app.

## Information architecture

1. **Hero** — offer, lead, audience, primary + secondary CTAs
2. **Who for / not** — qualify hardware teams; disqualify photo-only and freestyle-AI asks
3. **3 steps** — send assembly → geometry-faithful frames → continue only if the free still is useful
4. **Standard pack** — In / Out / SLA / how we price (no public rate card)
5. **Geometry proof** — alignment, consistency across angles, human acceptance gate
6. **Case #1** — own wearable hardware; featured ghost still + white-background + studio stills (and optional orbit clip). Missing pack frames stay off the page — not a row of empty cards.
7. **FAQ** — formats, NDA, timing, in-house tools, how we price (not a rate card), “is this AI video?”
8. **Footer CTA** — same primary action; `mailto:jexlau.dev@gmail.com` with subject `Free test frame STEP`. Footer also shows that address.

## Visual

Near-black studio field, paper-gray type and frames, geometric sans (Outfit + Work Sans) with IBM Plex Mono for spec labels. Hairline grid, no neon, no purple, no “AI product” glow.

## Assumptions we are shipping against

| Assumption | Decision on this page |
| --- | --- |
| **N = 5** | Standard pack includes **5 hero stills** (3 white-background + 2 studio / detail). |
| **Ghost / perspective** | Ghost / perspective assembly is **in the pack**. True explode is an **add-on**, not a default deliverable. |
| **Free 1 still** | First still is a free test frame. If it is not useful, the buyer does not pay for it. Full pack is quoted after that. |
| **No public price** | No USD price card and no dollar figures on the Pack card. On-page line: priced like outsourced 3D / film work; quote after we talk. FAQ “How do you price?” is collapsed and marked **not our rate card**. |
| **Not SaaS** | No accounts, no upload widget, no embed. Primary CTAs (hero, sticky header, footer) are `mailto:jexlau.dev@gmail.com?subject=Free%20test%20frame%20STEP`. |
| **Samples** | Hero and Case featured (full-width) use `01-ghost-perspective.jpg`. Case 2-up grid uses `02-white-bg-a.jpg`, `03-white-bg-b.png` (open-lid), `04-white-bg-c.png`, `05-studio-a.jpg`, and `06-studio-b.png` (yellow-post). Optional muted orbit clip uses `01-orbit.mp4` with the ghost still as poster. Drop-in paths live in [MEDIA.md](./MEDIA.md). No stock fake-3D renders. |
| **Share card** | `og:image` / `twitter:image` point at the committed 1200×630 `media/og/share.jpg`. `twitter:card` is `summary_large_image`. |

## Out of scope (intentionally absent)

Accounts, Growthfy, personal social handles, pipeline / renderer brand names, “AI powered” or freestyle-AI render pitch.
