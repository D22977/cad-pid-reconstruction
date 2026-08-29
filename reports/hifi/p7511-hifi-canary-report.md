# P-7511A/B HIFI canary report

This is a fidelity canary for the single **P-7511A/B** horizontal OH2 station. It is an editable-vector visual reconstruction, not installed-dimension authority.

## Status and scope

- Drawing status: NTS / PRELIMINARY / NON-RELEASE.
- Scope: only P-7511A/B; no vertical equipment was drawn.
- actual installed model identity: UNKNOWN.
- engineering acceptance: false.
- Merge, release, and final DWG: not authorized.
- Raster image is not embedded in the DXF; the outputs contain editable vector entities only.

## Evidence and provenance

- Control authority: Issue #3 comment 5460514157.
- OH2 dimension-anchor terminal: Issue #24 comment 5460380680, overall READY_FOR_HIFI_CANARY.
- Preserved vertical anchor: Issue #25 comment 5460272822; not used as product geometry.
- Verified source bridge: cadpid/source-bridge-00, evidence/derived/verified-source-script-extract.txt.
- Owner reference image SHA-256: B0B1AC51A1E452727DB231CEDAA0D9631FCE34D4FDB025C46F5DBDBDD8205F7A.
- Official-family context inspected in the anchor: KSB RPH, Sulzer OH2, and Flowserve PHL family topology. These sources do not establish P-7511 identity.

## Normalized visual contract

`D = 20 display units` means the visible casing height only. It is not an installed dimension.

| Element | HIFI proportion used | Provenance class | Permitted use |
|---|---|---|---|
| Volute/casing silhouette | body x=0.00..1.50D; body y=0.00..1.00D | FAMILY_PROPORTION_INFERENCE + VISUAL_REFERENCE_INFERENCE | visual reconstruction |
| Shaft centerline | y=0.50D | FAMILY_PROPORTION_INFERENCE + VISUAL_REFERENCE_INFERENCE | visual topology |
| Coupling/guard | center x=1.50D, y=0.50D; visual radius 0.25D | VISUAL_REFERENCE_INFERENCE | visual reconstruction |
| Motor body/endbell/fins | x=1.75..2.75D; y=0.10..0.90D | FAMILY_PROPORTION_INFERENCE + VISUAL_REFERENCE_INFERENCE | visual reconstruction |
| Baseplate and feet | x=-0.25..3.75D; y=-0.20..0.00D | FAMILY_PROPORTION_INFERENCE + VISUAL_REFERENCE_INFERENCE | visual reconstruction |
| Suction | left axial approach on shaft centerline | FAMILY_PROPORTION_INFERENCE + VISUAL_REFERENCE_INFERENCE | visual routing intent |
| Discharge | x=0.75D at casing top, routed upward | FAMILY_PROPORTION_INFERENCE + VISUAL_REFERENCE_INFERENCE | visual routing intent |
| Source labels | P-7511A/B, VOC KO Drum Pump, FROM D-7511 BTM, Seal Plan 11/52 | SOURCE_TEXT_EVIDENCE | text correction only |

The published family examples are dimensional/proportional anchors only. No unsupported pressure, material, class, rating, flow, head, nozzle connection, motor, or installed dimension was promoted into this drawing.

## Visible inventory

The canary includes the OH2 volute/casing, suction and discharge nozzles, support feet, baseplate, bearing/coupling region, coupling guard, horizontal motor body/endbell/fins/shaft, double-triangle valve, PI/FI/LI bubbles and leaders, arrows, and source-derived labels.

```json
{
  "block_entity_counts": {
    "ARC": 2,
    "LINE": 3,
    "LWPOLYLINE": 3
  },
  "modelspace_entity_counts": {
    "ARC": 1,
    "CIRCLE": 8,
    "INSERT": 2,
    "LINE": 19,
    "LWPOLYLINE": 12,
    "TEXT": 11
  },
  "modelspace_total": 53,
  "named_blocks": [
    "HIFI_DOUBLE_TRIANGLE_VALVE",
    "HIFI_VOLUTE_CASING"
  ]
}
```

## Acceptance boundary

Parser/audit cleanliness and deterministic repeat generation are checked by `tests/test_hifi_p7511_dxf.py`. This canary is ready only for owner visual-fidelity review. It is not engineering acceptance and does not authorize vertical drawing work, merge, release, or final DWG.

