# Demo surface mats pass — 2026-09-06

Rams DoD: `catellect-ops/plans/2026-09-06-demo-surface-mats-dod.md` (gates 1–6)

## Problem

Live soft-grey Ploopy/Watchy still read as whole-model clay: one value/roughness across parts.

## Approach (no brand stickers; GLB has no UV/textures)

**Ploopy**
- Hide print junk unchanged: HPH-039/038/036/035 (+ HPH-037/033 with headband proxy)
- Keep headband join proxy from #21 (outer-top pads + joint plugs)
- Earcups (HPH-013/018): procedural Principled Mix — satin cool shell ↔ darker warm soft pad (object-space medial ring + soft medial fill, Noise bump + sheen on pad)
- HPH-032: dark metallic driver mesh
- Headband proxy/joints: darker fabric sheen band (distinct from shell)

**Watchy**
- Remap CAD purple/gold/green → cool satin case / warm insert / near-black metal buttons

**Lighting**
- Product-mat softgrey pulls world/lights/exposure down so plastics do not chalk white under AgX

## Preview policy

Soft-grey frames land as `_preview-sg-07/08/09/12` only. **Live featured `07+` unchanged** until Steve PASS.

## Self-check vs gates

1. Not single chalk clay at thumbnail — shell / pad / mesh / band separate on Ploopy 08
2. ≥3 reads on 08: soft pad, hard shell, hard mesh (Watchy: case / insert / button)
3. Pads darker+warmer+duller+sheen vs shell
4. Shell satin (lower roughness + light coat) vs plaster
5. No fake logos
6. Same language on 07+08 (+09/12 previews)

## Do not promote

Hold live swap until Steve PASS.
