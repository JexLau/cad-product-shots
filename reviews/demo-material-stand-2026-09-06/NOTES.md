# Demo material / stand pass — 2026-09-06

Rams DoD: `catellect-ops/plans/2026-09-06-demo-material-stand-dod.md`

## Hidden (render exclude; CAD source kept)

Ploopy (`PloopyHeadphones-RevA.glb` mesh **data** names):

| Mesh | Obj | Why hidden |
| --- | --- | --- |
| **HPH-039** | `NAUO6` | Lattice headphone stand + rectangular base |
| **HPH-038** | `NAUO11` | Floating duplicate serpentine flexbars (ghost) |
| **HPH-036** | `NAUO9` | Tripod / assembly-jig lattice |
| **HPH-035** | `NAUO8` | Bare serpentine headband flexbars (fabric wrap not in CAD; DoD bans serpentine supports in finals) |

**Kept:** earcups HPH-013/018, driver mesh rings HPH-032, sliders HPH-033/037.

Watchy: no print-support meshes; material remap only.

## Materials

- **Ploopy:** Principled plastics — cool shell vs darker driver mesh (+metallic) vs satin metal sliders vs darker headband. `--no-clay`. Product lighting pulls world/lights down so greys do not chalk.
- **Watchy:** cool charcoal case (was CAD purple), warm mid insert (was gold), near-black buttons. No lavender clay / heavy dampen.

## Still policy

Featured live `07`/`08` **not** swapped until Steve/Rams gate. New soft-grey frames land as:

- `media/demo-ploopy/stills/_preview-sg-07.jpg` / `_preview-sg-08.jpg`
- `media/demo-watchy/stills/_preview-sg-07.jpg` / `_preview-sg-08.jpg`
- plus `after/` copies here

## Known residual (flag for Steve)

- Without HPH-035 the CAD has no fabric headband — earcups+sliders only; 07 may show assembly gaps.
- Earcup embossed `left` foot tabs are part of earcup mesh (not separate hide targets).
- Optional follow-up: quiet studio stand prop or fabric-band proxy for wearable silhouette.

## Follow-up

Headband proxy pass: `reviews/demo-headband-proxy-2026-09-06/` (restores wearable silhouette; live stills still held).
