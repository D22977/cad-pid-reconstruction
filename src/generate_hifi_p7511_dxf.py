"""Generate the bounded P-7511A/B high-fidelity visual canary.

The geometry is intentionally a new editable vector reconstruction.  It uses
the live OH2 anchor as a normalized visual contract and never treats the
source script or raster reference as installed engineering authority.
"""

from __future__ import annotations

import argparse
import html
import json
import re
from collections import Counter
from pathlib import Path
from typing import Iterable, Sequence

import ezdxf


Point = tuple[float, float]

LAYER_COLORS = {
    "EQUIP-CASING": 5,
    "EQUIP-SUPPORT": 30,
    "EQUIP-MOTOR": 4,
    "EQUIP-COUPLING": 6,
    "PIPING": 3,
    "PIPING-VALVE": 1,
    "INSTRUMENT": 2,
    "TEXT": 7,
    "NOTES": 8,
}

REQUIRED_TEXT = (
    "P-7511A/B",
    "VOC KO Drum Pump",
    "FROM D-7511 BTM",
    "Seal Plan 11/52",
    "PI",
    "FI",
    "LI",
)


def add_line(container, start: Point, end: Point, layer: str):
    return container.add_line(start, end, dxfattribs={"layer": layer})


def add_polyline(
    container, points: Sequence[Point], layer: str, close: bool = False
):
    entity = container.add_lwpolyline(
        points, format="xy", dxfattribs={"layer": layer}
    )
    entity.close(close)
    return entity


def add_circle(container, center: Point, radius: float, layer: str):
    return container.add_circle(center, radius, dxfattribs={"layer": layer})


def add_arc(
    container,
    center: Point,
    radius: float,
    start_angle: float,
    end_angle: float,
    layer: str,
):
    return container.add_arc(
        center,
        radius,
        start_angle,
        end_angle,
        dxfattribs={"layer": layer},
    )


def add_text(container, value: str, position: Point, height: float, layer: str):
    entity = container.add_text(
        value, dxfattribs={"layer": layer, "height": height}
    )
    entity.dxf.insert = position
    entity.dxf.rotation = 0.0
    return entity


def add_arrow(container, tip: Point, direction: Point, layer: str, size: float = 1.6):
    dx, dy = direction
    px, py = -dy, dx
    x, y = tip
    base = (x - dx * size, y - dy * size)
    points = [
        tip,
        (base[0] + px * size * 0.55, base[1] + py * size * 0.55),
        (base[0] - px * size * 0.55, base[1] - py * size * 0.55),
    ]
    return add_polyline(container, points, layer, close=True)


def add_layers(doc: ezdxf.document.Drawing) -> None:
    for name, color in LAYER_COLORS.items():
        if name not in doc.layers:
            doc.layers.add(name, color=color)


def build_casing_block(doc: ezdxf.document.Drawing) -> None:
    block = doc.blocks.new("HIFI_VOLUTE_CASING", base_point=(0, 0))
    outline = [
        (0, 6),
        (2, 4),
        (7, 2.5),
        (15, 2),
        (22, 3.5),
        (27, 7),
        (29, 10),
        (28, 13.5),
        (25, 17),
        (20, 19.5),
        (15, 20),
        (10, 19),
        (6, 17.5),
        (2, 14),
        (0, 10),
    ]
    add_polyline(block, outline, "EQUIP-CASING", close=True)
    add_arc(block, (15, 10), 7.5, 18, 342, "EQUIP-CASING")
    add_arc(block, (15, 10), 4.5, 30, 330, "EQUIP-CASING")
    add_line(block, (2, 10), (28, 10), "EQUIP-CASING")


def build_valve_block(doc: ezdxf.document.Drawing) -> None:
    block = doc.blocks.new("HIFI_DOUBLE_TRIANGLE_VALVE", base_point=(0, 0))
    add_polyline(block, [(-4, -3), (0, 0), (-4, 3)], "PIPING-VALVE", close=True)
    add_polyline(block, [(4, -3), (0, 0), (4, 3)], "PIPING-VALVE", close=True)
    add_line(block, (0, 0), (0, 5), "PIPING-VALVE")
    add_line(block, (-1.8, 5), (1.8, 5), "PIPING-VALVE")


def add_equipment(msp, d: float) -> None:
    body_width = 1.5 * d
    center_y = 0.5 * d
    coupling_x = 1.5 * d
    motor_left = 1.75 * d
    motor_right = 2.75 * d
    base_left = -0.25 * d
    base_right = 3.75 * d

    msp.add_blockref(
        "HIFI_VOLUTE_CASING",
        (0, 0),
        dxfattribs={"layer": "EQUIP-CASING"},
    )

    # Axial suction nozzle and a short flange at the casing face.
    add_polyline(
        msp,
        [(-12, 8), (0, 8), (0, 12), (-12, 12)],
        "EQUIP-CASING",
        close=True,
    )
    add_line(msp, (-12, 7), (-12, 13), "EQUIP-CASING")
    add_line(msp, (-9, 8), (-9, 12), "EQUIP-CASING")

    # Support feet and the common baseplate.
    add_polyline(
        msp,
        [(base_left, -3), (base_right, -3), (base_right, 0), (base_left, 0)],
        "EQUIP-SUPPORT",
        close=True,
    )
    add_polyline(msp, [(4, 0), (10, 0), (9, 3), (5, 3)], "EQUIP-SUPPORT", close=True)
    add_polyline(
        msp, [(20, 0), (26, 0), (25, 3), (21, 3)], "EQUIP-SUPPORT", close=True
    )
    add_polyline(
        msp,
        [(motor_left, 0), (motor_right, 0), (motor_right, 3), (motor_left, 3)],
        "EQUIP-SUPPORT",
        close=True,
    )
    add_circle(msp, (0, -1.5), 0.9, "EQUIP-SUPPORT")
    add_circle(msp, (70, -1.5), 0.9, "EQUIP-SUPPORT")

    # Shaft, bearing housing, guard, and coupling envelope.
    add_line(msp, (body_width - 6, center_y), (motor_left + 2, center_y), "EQUIP-COUPLING")
    add_polyline(
        msp,
        [(25, 5), (31, 5), (35, 7), (35, 13), (31, 15), (25, 15)],
        "EQUIP-COUPLING",
        close=True,
    )
    add_circle(msp, (coupling_x, center_y), 5, "EQUIP-COUPLING")
    add_circle(msp, (coupling_x, center_y), 2.2, "EQUIP-COUPLING")
    add_arc(msp, (coupling_x, center_y), 6, 35, 325, "EQUIP-COUPLING")
    add_polyline(
        msp,
        [(26, 10), (28, 10), (28, 13), (26, 13)],
        "EQUIP-COUPLING",
        close=True,
    )

    # Motor body, endbell, shaft and repeated cooling fins.
    add_polyline(
        msp,
        [
            (motor_left + 2, 4),
            (motor_right - 3, 4),
            (motor_right, 6),
            (motor_right, 14),
            (motor_right - 3, 16),
            (motor_left + 2, 16),
        ],
        "EQUIP-MOTOR",
        close=True,
    )
    add_polyline(
        msp,
        [(motor_left - 1, 6), (motor_left + 2, 6), (motor_left + 2, 14), (motor_left - 1, 14)],
        "EQUIP-MOTOR",
        close=True,
    )
    add_circle(msp, (motor_right, center_y), 3, "EQUIP-MOTOR")
    for x in (41, 44, 47, 50, 53):
        add_line(msp, (x, 4), (x, 16), "EQUIP-MOTOR")
    add_line(msp, (motor_left - 4, center_y), (motor_left + 2, center_y), "EQUIP-MOTOR")


def add_process_piping(msp, d: float) -> None:
    center_y = 0.5 * d
    discharge_x = 0.75 * d

    # Left axial suction, with an arrow indicating the source-side approach.
    add_line(msp, (-38, center_y), (-12, center_y), "PIPING")
    add_line(msp, (-38, center_y - 2), (-12, center_y - 2), "PIPING")
    add_arrow(msp, (-33, center_y), (1, 0), "PIPING")

    # Upward discharge and an elbow to the instrument/valve run.
    add_line(msp, (discharge_x - 1.5, d), (discharge_x - 1.5, 38), "PIPING")
    add_line(msp, (discharge_x + 1.5, d), (discharge_x + 1.5, 38), "PIPING")
    add_line(msp, (discharge_x - 1.5, 38), (43, 38), "PIPING")
    add_line(msp, (discharge_x + 1.5, 38), (43, 38), "PIPING")
    add_polyline(
        msp,
        [(discharge_x - 1.5, 38), (discharge_x - 1.5, 40), (discharge_x + 1.5, 42), (discharge_x + 1.5, 38)],
        "PIPING",
        close=False,
    )
    add_arrow(msp, (43, 38), (1, 0), "PIPING")

    # Explicit double-triangle valve geometry, not a rectangle proxy.
    msp.add_blockref(
        "HIFI_DOUBLE_TRIANGLE_VALVE",
        (25, 38),
        dxfattribs={"layer": "PIPING-VALVE"},
    )

    # Small pipe branch and a liquid-level indication on the suction side.
    add_line(msp, (-18, center_y), (-18, 16), "PIPING")
    add_circle(msp, (-18, 18), 2.4, "INSTRUMENT")
    add_line(msp, (-18, 16), (-18, 15.6), "INSTRUMENT")


def add_instruments_and_text(msp, d: float) -> None:
    # Discharge PI/FI bubbles and leaders.
    for label, x in (("PI", 28), ("FI", 35)):
        add_circle(msp, (x, 45), 2.4, "INSTRUMENT")
        add_line(msp, (x, 42.6), (x, 38), "INSTRUMENT")
        add_text(msp, label, (x - 1.3, 44.2), 1.8, "TEXT")
    add_text(msp, "LI", (-19.3, 17.2), 1.8, "TEXT")

    add_text(msp, "P-7511A/B", (0, 66), 3.4, "TEXT")
    add_text(msp, "VOC KO Drum Pump", (0, 61), 2.4, "TEXT")
    add_text(msp, "Seal Plan 11/52", (34, 24), 1.8, "TEXT")
    add_text(msp, "FROM D-7511 BTM", (-43, 18), 1.8, "TEXT")
    add_text(msp, "NTS / PRELIMINARY / NON-RELEASE", (0, -9), 1.9, "NOTES")
    add_text(msp, "HIFI visual canary; no installed scale", (0, -6.5), 1.5, "NOTES")
    add_text(msp, "left axial suction / upward discharge", (0, 52), 1.4, "NOTES")
    add_text(msp, "family topology + owner visual proportions", (0, 49), 1.4, "NOTES")


def build_document(model: dict) -> ezdxf.document.Drawing:
    if model["station"] != "P-7511A/B":
        raise ValueError("model is outside the authorized station scope")
    if tuple(model["drawing_status"]) != ("NTS", "PRELIMINARY", "NON-RELEASE"):
        raise ValueError("drawing status must remain NTS/PRELIMINARY/NON-RELEASE")
    for required in REQUIRED_TEXT:
        if required not in model["source_text"]:
            raise ValueError(f"missing source text: {required}")

    d = float(model["normalized_envelope"]["D_units"])
    doc = ezdxf.new("R2013")
    doc.header["$TDCREATE"] = 0.0
    doc.header["$TDUPDATE"] = 0.0
    doc.header["$LASTSAVEDBY"] = "CADPID-HIFI-P7511-CANARY-01"
    # ezdxf otherwise generates these GUIDs afresh on every save.
    doc.header["$FINGERPRINTGUID"] = "{11111111-1111-4111-8111-111111111111}"
    doc.header["$VERSIONGUID"] = "{22222222-2222-4222-8222-222222222222}"
    add_layers(doc)
    build_casing_block(doc)
    build_valve_block(doc)
    msp = doc.modelspace()
    add_equipment(msp, d)
    add_process_piping(msp, d)
    add_instruments_and_text(msp, d)
    return doc


def entity_inventory(doc: ezdxf.document.Drawing) -> dict:
    modelspace_counts = Counter(entity.dxftype() for entity in doc.modelspace())
    block_counts = Counter()
    blocks = []
    for block in doc.blocks:
        if block.name.startswith("*"):
            continue
        blocks.append(block.name)
        block_counts.update(entity.dxftype() for entity in block)
    return {
        "modelspace_entity_counts": dict(sorted(modelspace_counts.items())),
        "block_entity_counts": dict(sorted(block_counts.items())),
        "named_blocks": sorted(blocks),
        "modelspace_total": sum(modelspace_counts.values()),
    }


def svg_x(x: float) -> float:
    return 105.0 + x * 8.0


def svg_y(y: float) -> float:
    return 580.0 - y * 8.0


def svg_line(start: Point, end: Point, cls: str = "line") -> str:
    return (
        f'<line class="{cls}" x1="{svg_x(start[0]):.2f}" y1="{svg_y(start[1]):.2f}" '
        f'x2="{svg_x(end[0]):.2f}" y2="{svg_y(end[1]):.2f}" />'
    )


def svg_polyline(points: Iterable[Point], cls: str = "line", close: bool = False) -> str:
    values = " ".join(f"{svg_x(x):.2f},{svg_y(y):.2f}" for x, y in points)
    if close:
        values += f" {values.split()[0]}"
    return f'<polyline class="{cls}" points="{values}" />'


def svg_circle(center: Point, radius: float, cls: str = "line") -> str:
    return (
        f'<circle class="{cls}" cx="{svg_x(center[0]):.2f}" cy="{svg_y(center[1]):.2f}" '
        f'r="{radius * 8:.2f}" />'
    )


def svg_text(value: str, position: Point, size: float, cls: str = "label") -> str:
    return (
        f'<text class="{cls}" x="{svg_x(position[0]):.2f}" y="{svg_y(position[1]):.2f}" '
        f'font-size="{size * 8:.2f}">{html.escape(value)}</text>'
    )


def build_svg() -> str:
    casing = [
        (0, 6),
        (2, 4),
        (7, 2.5),
        (15, 2),
        (22, 3.5),
        (27, 7),
        (29, 10),
        (28, 13.5),
        (25, 17),
        (20, 19.5),
        (15, 20),
        (10, 19),
        (6, 17.5),
        (2, 14),
        (0, 10),
    ]
    out = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="700" viewBox="0 0 1200 700">',
        '<title>P-7511A/B high-fidelity editable-vector canary preview</title>',
        '<rect width="1200" height="700" fill="#f7f9fc" />',
        '<style>',
        '.equip{fill:#d8e6ff;stroke:#174ea6;stroke-width:2.2}',
        '.support{fill:#e8ddc8;stroke:#76521f;stroke-width:2}',
        '.motor{fill:#d6d6ef;stroke:#34348f;stroke-width:2.2}',
        '.coupling{fill:none;stroke:#9b3b7d;stroke-width:2.2}',
        '.pipe{fill:none;stroke:#16803c;stroke-width:2.2}',
        '.valve{fill:#fff0c2;stroke:#a66a00;stroke-width:2.2}',
        '.instrument{fill:#fff;stroke:#b22222;stroke-width:2}',
        '.label{font-family:Arial,sans-serif;fill:#17202a}',
        '.note{font-family:Arial,sans-serif;fill:#4a5568}',
        '.center{fill:none;stroke:#8994a4;stroke-width:1;stroke-dasharray:5 4}',
        '</style>',
    ]
    out.append(svg_line((-42, 10), (78, 10), "center"))
    out.append(svg_polyline(casing, "equip", close=True))
    out.append(svg_circle((15, 10), 7.5, "coupling"))
    out.append(svg_circle((15, 10), 4.5, "coupling"))
    out.append(svg_polyline([(-12, 8), (0, 8), (0, 12), (-12, 12)], "equip", close=True))
    out.extend([svg_line((-12, 7), (-12, 13), "equip"), svg_line((-9, 8), (-9, 12), "equip")])
    out.append(svg_polyline([(-5, -3), (75, -3), (75, 0), (-5, 0)], "support", close=True))
    out.append(svg_polyline([(4, 0), (10, 0), (9, 3), (5, 3)], "support", close=True))
    out.append(svg_polyline([(20, 0), (26, 0), (25, 3), (21, 3)], "support", close=True))
    out.append(svg_polyline([(35, 0), (55, 0), (55, 3), (35, 3)], "support", close=True))
    out.extend([svg_circle((0, -1.5), 0.9, "support"), svg_circle((70, -1.5), 0.9, "support")])
    out.extend([svg_line((24, 10), (37, 10), "coupling"), svg_circle((30, 10), 5, "coupling")])
    out.append(svg_polyline([(25, 5), (31, 5), (35, 7), (35, 13), (31, 15), (25, 15)], "coupling", close=True))
    out.append(svg_polyline([(37, 4), (52, 4), (55, 6), (55, 14), (52, 16), (37, 16)], "motor", close=True))
    out.append(svg_polyline([(34, 6), (37, 6), (37, 14), (34, 14)], "motor", close=True))
    out.append(svg_circle((55, 10), 3, "motor"))
    for x in (41, 44, 47, 50, 53):
        out.append(svg_line((x, 4), (x, 16), "motor"))
    out.extend(
        [
            svg_line((13.5, 20), (13.5, 38), "pipe"),
            svg_line((16.5, 20), (16.5, 38), "pipe"),
            svg_line((13.5, 38), (43, 38), "pipe"),
            svg_line((16.5, 38), (43, 38), "pipe"),
            svg_line((-38, 10), (-12, 10), "pipe"),
            svg_line((-38, 8), (-12, 8), "pipe"),
        ]
    )
    out.append(svg_polyline([(21, 35), (25, 38), (21, 41)], "valve", close=True))
    out.append(svg_polyline([(29, 35), (25, 38), (29, 41)], "valve", close=True))
    out.append(svg_line((25, 38), (25, 43), "valve"))
    out.append(svg_line((23.2, 43), (26.8, 43), "valve"))
    out.extend([svg_circle((28, 45), 2.4, "instrument"), svg_circle((35, 45), 2.4, "instrument")])
    out.extend([svg_line((28, 42.6), (28, 38), "instrument"), svg_line((35, 42.6), (35, 38), "instrument")])
    out.extend([svg_circle((-18, 18), 2.4, "instrument"), svg_line((-18, 16), (-18, 15.6), "instrument")])
    out.extend(
        [
            svg_text("P-7511A/B", (0, 66), 3.4),
            svg_text("VOC KO Drum Pump", (0, 61), 2.4),
            svg_text("Seal Plan 11/52", (34, 24), 1.8),
            svg_text("FROM D-7511 BTM", (-43, 18), 1.8),
            svg_text("PI", (26.7, 45.4), 1.8),
            svg_text("FI", (33.7, 45.4), 1.8),
            svg_text("LI", (-19.3, 18.4), 1.8),
            svg_text("NTS / PRELIMINARY / NON-RELEASE", (0, -9), 1.9, "note"),
            svg_text("HIFI visual canary; no installed scale", (0, -6.5), 1.5, "note"),
            svg_text("left axial suction / upward discharge", (0, 52), 1.4, "note"),
            svg_text("family topology + owner visual proportions", (0, 49), 1.4, "note"),
        ]
    )
    out.append('</svg>')
    return "\n".join(out) + "\n"


def build_report(model: dict, inventory: dict) -> str:
    return f"""# P-7511A/B HIFI canary report

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

`D = {model['normalized_envelope']['D_units']} display units` means the visible casing height only. It is not an installed dimension.

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
{json.dumps(inventory, indent=2, sort_keys=True)}
```

## Acceptance boundary

Parser/audit cleanliness and deterministic repeat generation are checked by `tests/test_hifi_p7511_dxf.py`. This canary is ready only for owner visual-fidelity review. It is not engineering acceptance and does not authorize vertical drawing work, merge, release, or final DWG.
"""


def write_outputs(model_path: Path, dxf_path: Path, svg_path: Path, report_path: Path) -> dict:
    model = json.loads(model_path.read_text(encoding="utf-8"))
    doc = build_document(model)
    auditor = doc.audit()
    if auditor.has_errors:
        raise RuntimeError(f"DXF audit reported {len(auditor.errors)} errors")

    dxf_path.parent.mkdir(parents=True, exist_ok=True)
    svg_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    doc.saveas(dxf_path)
    # ezdxf regenerates VERSIONGUID while serializing. Keep the ASCII DXF
    # byte-stable so repeat generation is an auditable canary property.
    dxf_text = dxf_path.read_text(encoding="utf-8")
    dxf_text = re.sub(
        r"(\$VERSIONGUID\r?\n\s*2\r?\n)\{[0-9A-F-]+\}",
        r"\g<1>{22222222-2222-4222-8222-222222222222}",
        dxf_text,
        count=1,
    )
    dxf_text = re.sub(
        r"1\.4\.4 @ [^\r\n]+",
        "1.4.4 @ 2026-01-01T00:00:00+00:00",
        dxf_text,
    )
    for header_name in ("$TDCREATE", "$TDUCREATE", "$TDUPDATE", "$TDUUPDATE"):
        dxf_text = re.sub(
            rf"({re.escape(header_name)}\r?\n\s*40\r?\n)[^\r\n]+",
            r"\g<1>0.0",
            dxf_text,
            count=1,
        )
    class_marker = "  0\nSECTION\n  2\nCLASSES\n"
    class_start = dxf_text.index(class_marker) + len(class_marker)
    class_end = dxf_text.index("  0\nENDSEC", class_start)
    class_body = dxf_text[class_start:class_end]
    class_parts = re.split(r"(?=  0\nCLASS\n)", class_body)
    class_header = class_parts[0]
    class_records = class_parts[1:]
    class_records.sort(
        key=lambda record: re.search(r"\n  1\n([^\r\n]+)", record).group(1)
    )
    dxf_text = (
        dxf_text[:class_start]
        + class_header
        + "".join(class_records)
        + dxf_text[class_end:]
    )
    dxf_path.write_text(dxf_text, encoding="utf-8", newline="\n")
    svg_path.write_text(build_svg(), encoding="utf-8", newline="\n")
    inventory = entity_inventory(doc)
    report_path.write_text(build_report(model, inventory), encoding="utf-8", newline="\n")
    return inventory


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--dxf", type=Path, required=True)
    parser.add_argument("--svg", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    inventory = write_outputs(args.model, args.dxf, args.svg, args.report)
    print(json.dumps(inventory, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

