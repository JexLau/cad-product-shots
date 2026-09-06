# Ploopy headband join fix — 2026-09-06

Follow-up to live `60e8a9e` / #20. Steve/Jex: soft-grey Ploopy headband proxy FAILS join.

## Live failures (before)

| Shot | Symptom |
| --- | --- |
| 07 | Arc floats with gap to earcups |
| 09 / 12 | One side severed / earcup detached (previews never re-rendered with proxy; showed one-sided HPH-037) |

## Root cause

1. Prior proxy put low stubs only at extreme outer X (beside cups in screen space) while the ellipse rose before overlapping the cup body → floating arc in 07.
2. Extreme outer wall is shorter than the true top pad (`zmax` ~ cup_top−20mm at wall; real pad ~18–34% in from outer).
3. Earcups are hollow shells — cavity paths read as gaps; ends must sit on outer-third top pads.
4. `_preview-sg-09/12` were still from the pre-proxy hide-supports pass (severed HPH-037).

## Fix (`add_ploopy_headband_proxy`)

1. Measure **outer-third top pads** on HPH-013 / HPH-018 (mesh verts, not padded bbox).
2. Build vertical yokes from those pads + smooth crown arc.
3. Add fabric-matched **joint plugs** dug into the pads so ends read joined (no floating end-caps / AO gap).
4. Hide print junk **HPH-039/038/036/035**; hide one-sided stubs **HPH-037/033**.
5. Re-render soft-grey `_preview-sg-07/08/09/12` (live featured stills **unchanged**).

## Acceptance self-check

- Continuous wearable silhouette on 07/08/09/12 soft-grey previews
- Both ends joined into earcup outer-top pads
- No floating arc / severed band / split-in-half
- Print junk still hidden

## Watchy

Unchanged (no headband path).

## Policy

**Do not promote to live** until Steve PASS.
