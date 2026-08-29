# Preliminary DXF Visual Review

status: READY_FOR_OWNER_VISUAL_REVIEW
card_id: CADPID-DXF-VISUAL-PACK-03
reviewed source: `D22977/cad-pid-reconstruction` / `cadpid/dxf-canary-02`
exact reviewed head: `92939f90b37412f5263c38f87ef94026b96064d3`
source DXF: `output/dxf/cad-pid-reconstruction-preliminary.dxf`
source DXF Git blob: `5079181b1120a96e8c674afd0b5947f6027941d5`
source DXF SHA-256: `6FC7218D89203BEE92919A0D920B6BB3796F1DE00F9FED9AB1B1240D509A64D0`

## Render

The render is `output/render/cad-pid-reconstruction-preliminary.svg`. It was produced by the installed ezdxf 1.4.4 native `SVGBackend`, with a white background, monochrome-light colors, and filled glyph rendering. No dependency or reviewed product path was added or changed.

The SVG is valid, non-empty (52,110 bytes), and contains 106 vector paths for the 106 reopened DXF model-space entities. The same render was produced by two independent in-memory runs byte-for-byte identically. The renderer represents TEXT as vector glyph paths rather than literal SVG `<text>` nodes; the required tag and notice inventory below is the source TEXT inventory rendered into those paths.

## Visible equipment and tag inventory

| Tag | Source description | Visible associated content |
| --- | --- | --- |
| `P-3635A/B` | Slop Oil Pump (Sump 3-1) | pump geometry, suction/discharge, check/control valves, PI/FI, seal-plan source note |
| `P-3637A/B` | Slop Oil Pump (Sump 3-3) | pump geometry, suction/discharge, check/control valves, PI/FI, seal-plan note |
| `P-7509` | Waste PFO Drain Pump | pump geometry, suction/discharge, check/control valves, PI/TI/LI, source-note and unknown-insulation labels |
| `P-7511A/B` | VOC KO Drum Pump | horizontal pump geometry, suction/discharge, check/control valves, PI/FI/LI, source note |

Required tag counts in reopened DXF TEXT entities: each of the four tags is present exactly once. Required notices are present exactly once each: `PRELIMINARY - NOT FOR ENGINEERING RELEASE` and `SOURCE_COORD_UNITS / NTS`.

## Layer inventory

| Layer | Entity counts |
| --- | --- |
| `E-EQUIP` | CIRCLE 4; LINE 6; LWPOLYLINE 8 |
| `E-PIPE` | CIRCLE 4; LINE 32; LWPOLYLINE 4 |
| `E-INST` | CIRCLE 10; LINE 10 |
| `E-TEXT` | TEXT 24 |
| `E-FRAME` | LWPOLYLINE 1; TEXT 3 |

The DXF also contains the standard default layers `0` and `Defpoints`; the required project layers are all present. Total model-space inventory is 106 entities: CIRCLE 18, LINE 48, LWPOLYLINE 13, TEXT 27.

## Bounds and coordinate warning

Drawing bounds are `min=(-25.0,-24.0)` and `max=(950.0,74.0)`. The drawing explicitly carries `SOURCE_COORD_UNITS / NTS`; these are source-coordinate units and not a claim of true scale. The visual frame also carries `ENGINEERING FIELDS: TBD / UNKNOWN`.

The reopened-DXF audit reported `unrecoverable_errors=0` and `fixed_errors=0`. Existing source-derived regression checks remain passing, including P-7509 control-valve center X=625 in the 600–650 zone, the vertical-valve endpoint `[903,37]`, no `oldosoldbl`, and no emitted `150#C` or `300# RF` text.

## Unresolved engineering fields / TBDs

- drawing class and owner acceptance
- units and true scale
- line size/rating/material class
- insulation and heat tracing
- pump type/detail standard
- symbol standard
- title-block data and revision

## Safety boundary

This is a preliminary, non-release visual inspection artifact. It is not an engineering acceptance, approved design, final DWG, merge, or release. No rating, material, true scale, specification, or other unresolved engineering value has been selected or invented.

## Owner visual-review checklist

1. Confirm the relative placement and apparent geometry of all four pump stations within the frame, including the P-7509 station near its source-derived zone.
2. Confirm that equipment labels, instrument labels, `PRELIMINARY - NOT FOR ENGINEERING RELEASE`, and `SOURCE_COORD_UNITS / NTS` are readable at the intended viewing zoom.
3. Check suction/discharge line continuity and the visible placement/orientation of check valves and control valves for obvious breaks, overlaps, or misplaced symbols.
4. Identify any expected equipment, line, valve, instrument, label, or connection that is visibly missing from the current preliminary reconstruction.
5. Identify obvious visual defects such as clipping, collisions, illegible text, excessive whitespace, or frame/title-block presentation issues.

Owner review of this artifact is still required; no owner acceptance is inferred from its creation.
