"""Generate the six-path P-7511 old-style horizontal pump body repair."""
from __future__ import annotations

import argparse
import html
import json
import math
import re
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

import ezdxf

PROTOCOL = "CADPID_HIFI_P7511_BODY_REFERENCE_V1"
CARD_ID = "CADPID-HIFI-P7511-BODY-REPAIR-01"
LAYERS = (
    "EQUIP-CASING",
    "EQUIP-SUPPORT",
    "EQUIP-MOTOR",
    "EQUIP-COUPLING",
    "TEXT",
    "CENTERLINE",
)
FIXED_FINGERPRINT = "{A6B1C2D3-E4F5-4678-9012-3456789ABCDE}"
FIXED_VERSION = "{B7C2D3E4-F5A6-4789-0123-456789ABCDEF}"


@dataclass(frozen=True)
class Primitive:
    kind: str
    layer: str
    values: tuple


class Geometry:
    def __init__(self) -> None:
        self.items: list[Primitive] = []

    def line(self, layer: str, start: tuple[float, float], end: tuple[float, float]) -> None:
        self.items.append(Primitive("line", layer, (start, end)))

    def polyline(
        self, layer: str, points: list[tuple[float, float]], closed: bool = False
    ) -> None:
        self.items.append(Primitive("polyline", layer, (tuple(points), closed)))

    def circle(self, layer: str, center: tuple[float, float], radius: float) -> None:
        self.items.append(Primitive("circle", layer, (center, radius)))

    def arc(
        self,
        layer: str,
        center: tuple[float, float],
        radius: float,
        start: float,
        end: float,
    ) -> None:
        self.items.append(Primitive("arc", layer, (center, radius, start, end)))

    def text(self, layer: str, value: str, insert: tuple[float, float], height: float) -> None:
        self.items.append(Primitive("text", layer, (value, insert, height)))


def _validate_model(model_path: Path) -> dict:
    model = json.loads(model_path.read_text(encoding="utf-8"))
    if model.get("protocol") != PROTOCOL or model.get("card_id") != CARD_ID:
        raise ValueError("model is not the live P-7511 body-only contract")
    return model


def build_geometry() -> Geometry:
    g = Geometry()
    casing = "EQUIP-CASING"
    support = "EQUIP-SUPPORT"
    motor = "EQUIP-MOTOR"
    coupling = "EQUIP-COUPLING"
    centerline = "CENTERLINE"
    text = "TEXT"

    # A thin common baseline and aligned feet establish the horizontal body envelope.
    g.line(centerline, (0.0, 12.0), (850.0, 12.0))
    g.polyline(support, [(0.0, 0.0), (850.0, 0.0), (850.0, 15.0), (0.0, 15.0)], True)
    g.circle(support, (35.0, 7.5), 3.0)
    g.circle(support, (815.0, 7.5), 3.0)

    # Fuller lower scroll with an intentionally asymmetric old-style volute silhouette.
    outer_volute = [
        (82.0, 118.0), (105.0, 80.0), (150.0, 52.0), (215.0, 40.0),
        (278.0, 55.0), (325.0, 95.0), (350.0, 150.0), (362.0, 210.0),
        (350.0, 272.0), (322.0, 325.0), (282.0, 370.0), (235.0, 402.0),
        (185.0, 412.0), (140.0, 394.0), (108.0, 350.0), (90.0, 300.0),
        (76.0, 250.0), (74.0, 180.0),
    ]
    g.polyline(casing, outer_volute, True)
    g.arc(casing, (220.0, 210.0), 132.0, 18.0, 302.0)
    g.arc(casing, (220.0, 210.0), 78.0, 35.0, 312.0)
    g.line(casing, (113.0, 126.0), (145.0, 95.0))
    g.line(casing, (305.0, 112.0), (334.0, 156.0))

    # Left suction flange and short stub enter the casing on the shaft axis.
    g.polyline(
        casing,
        [(25.0, 182.0), (40.0, 182.0), (40.0, 196.0), (82.0, 196.0),
         (82.0, 224.0), (40.0, 224.0), (40.0, 238.0), (25.0, 238.0)],
        True,
    )
    g.line(casing, (25.0, 182.0), (25.0, 238.0))
    g.line(casing, (33.0, 187.0), (33.0, 233.0))

    # Short integral discharge neck and horizontal top flange, not process piping.
    g.line(casing, (205.0, 370.0), (205.0, 408.0))
    g.line(casing, (205.0, 408.0), (215.0, 480.0))
    g.line(casing, (285.0, 370.0), (285.0, 408.0))
    g.line(casing, (285.0, 408.0), (275.0, 480.0))
    g.arc(casing, (245.0, 370.0), 40.0, 0.0, 180.0)
    g.polyline(casing, [(200.0, 480.0), (290.0, 480.0), (290.0, 510.0), (200.0, 510.0)], True)
    g.line(casing, (208.0, 495.0), (282.0, 495.0))

    # Pump feet align to the baseline under the casing.
    g.polyline(support, [(120.0, 15.0), (175.0, 15.0), (168.0, 62.0), (128.0, 62.0)], True)
    g.polyline(support, [(270.0, 15.0), (330.0, 15.0), (322.0, 62.0), (278.0, 62.0)], True)
    g.line(support, (128.0, 52.0), (168.0, 52.0))
    g.line(support, (278.0, 52.0), (322.0, 52.0))

    # Compact bearing/coupling zone is deliberately shorter than the motor.
    g.line(coupling, (342.0, 210.0), (460.0, 210.0))
    g.polyline(coupling, [(350.0, 165.0), (410.0, 165.0), (430.0, 182.0),
                          (430.0, 238.0), (410.0, 255.0), (350.0, 255.0)], True)
    g.circle(coupling, (390.0, 210.0), 45.0)
    g.circle(coupling, (410.0, 210.0), 27.0)
    g.line(coupling, (430.0, 176.0), (450.0, 190.0))
    g.line(coupling, (430.0, 244.0), (450.0, 230.0))

    # Long right-half motor with a rounded/boxed rear cap and many visible ribs.
    g.polyline(motor, [(430.0, 105.0), (460.0, 90.0), (700.0, 90.0),
                       (730.0, 105.0), (730.0, 315.0), (700.0, 330.0),
                       (460.0, 330.0), (430.0, 315.0)], True)
    g.arc(motor, (730.0, 210.0), 100.0, -90.0, 90.0)
    g.polyline(motor, [(730.0, 110.0), (785.0, 120.0), (825.0, 158.0),
                       (830.0, 210.0), (825.0, 262.0), (785.0, 300.0),
                       (730.0, 310.0)], True)
    for x in range(472, 701, 18):
        g.line(motor, (float(x), 120.0), (float(x), 300.0))
    g.line(motor, (446.0, 122.0), (446.0, 298.0))
    g.line(motor, (455.0, 112.0), (455.0, 308.0))
    g.line(motor, (430.0, 178.0), (460.0, 178.0))
    g.line(motor, (430.0, 242.0), (460.0, 242.0))
    g.polyline(motor, [(555.0, 330.0), (655.0, 330.0), (655.0, 390.0),
                       (555.0, 390.0)], True)
    g.line(motor, (565.0, 375.0), (645.0, 375.0))
    g.line(motor, (575.0, 390.0), (575.0, 402.0))
    g.line(motor, (635.0, 390.0), (635.0, 402.0))

    # Motor feet remain on the same thin common baseline.
    g.polyline(support, [(455.0, 15.0), (525.0, 15.0), (518.0, 58.0), (462.0, 58.0)], True)
    g.polyline(support, [(675.0, 15.0), (770.0, 15.0), (760.0, 58.0), (685.0, 58.0)], True)

    # Minimal inspection labels; they do not assert installed engineering data.
    g.text(text, "P-7511A/B", (24.0, 500.0), 14.0)
    g.text(text, "NTS / PRELIMINARY / NON-RELEASE", (470.0, 500.0), 10.0)
    g.text(text, "OLD-STYLE HORIZONTAL PUMP BODY", (20.0, 30.0), 10.0)
    g.text(text, "VISUAL RECONSTRUCTION / NO INSTALLED SCALE", (495.0, 30.0), 9.0)
    return g


def _fmt(value: float) -> str:
    return f"{value:.3f}".rstrip("0").rstrip(".")


def _make_dxf(geometry: Geometry, path: Path) -> None:
    doc = ezdxf.new("R2010", setup=False)
    doc.header["$TDCREATE"] = 0.0
    doc.header["$TDUPDATE"] = 0.0
    doc.header["$TDUCREATE"] = 0.0
    doc.header["$TDUUPDATE"] = 0.0
    doc.header["$LASTSAVEDBY"] = CARD_ID
    doc.header["$FINGERPRINTGUID"] = FIXED_FINGERPRINT
    doc.header["$VERSIONGUID"] = FIXED_VERSION
    doc.header["$HANDSEED"] = "FFFF"
    doc.header["$INSUNITS"] = 0
    for name in LAYERS:
        if name not in doc.layers:
            doc.layers.add(name=name)
    msp = doc.modelspace()
    for item in geometry.items:
        if item.kind == "line":
            start, end = item.values
            msp.add_line(start, end, dxfattribs={"layer": item.layer})
        elif item.kind == "polyline":
            points, closed = item.values
            msp.add_lwpolyline(points, close=closed, dxfattribs={"layer": item.layer})
        elif item.kind == "circle":
            center, radius = item.values
            msp.add_circle(center, radius, dxfattribs={"layer": item.layer})
        elif item.kind == "arc":
            center, radius, start, end = item.values
            msp.add_arc(center, radius, start_angle=start, end_angle=end,
                        dxfattribs={"layer": item.layer})
        elif item.kind == "text":
            value, insert, height = item.values
            msp.add_text(
                value, dxfattribs={"layer": item.layer, "height": height}
            ).set_placement(insert)
    audit = doc.audit()
    if audit.errors:
        raise RuntimeError(f"DXF audit errors: {len(audit.errors)}")
    path.parent.mkdir(parents=True, exist_ok=True)
    doc.saveas(path)
    # Normalize text-level volatile header fields for byte-identical regeneration.
    raw = path.read_text(encoding="utf-8")
    class_block = r"\s*0\nCLASS\n\s*1\n(?:ACDBPLACEHOLDER|LAYOUT)\n.*?(?=\s*0\nCLASS\n|\s*0\nENDSEC)"

    def _canonical_class_order(match: re.Match[str]) -> str:
        first = match.group("first")
        second = match.group("second")
        if "ACDBPLACEHOLDER" in first:
            return first + second
        return second + first

    raw = re.sub(
        rf"(?ms)(?P<first>{class_block})(?P<second>{class_block})(?=\s*0\nENDSEC)",
        _canonical_class_order,
        raw,
    )
    raw = re.sub(
        r"(?m)^9\n\$HANDSEED\n5\n[^\n]+",
        "9\n$HANDSEED\n5\nFFFF",
        raw,
    )
    raw = re.sub(
        r"(?m)^(\s*9\n\$(?:FINGERPRINTGUID|VERSIONGUID)\n\s*2\n)[^\n]+",
        lambda match: match.group(1) + FIXED_FINGERPRINT,
        raw,
    )
    raw = re.sub(
        r"(?m)^9\n\$(?:TDCREATE|TDUPDATE|TDUCREATE|TDUUPDATE)\n40\n[^\n]+",
        lambda match: match.group(0).rsplit("\n", 1)[0] + "\n0.0",
        raw,
    )
    raw = re.sub(
        r"1\.4\.4 @ [^\n]+",
        "1.4.4 @ 1970-01-01T00:00:00+00:00",
        raw,
    )
    path.write_text(raw.replace("\r\n", "\n"), encoding="utf-8", newline="\n")


def _arc_points(center: tuple[float, float], radius: float, start: float, end: float) -> str:
    values = []
    count = max(8, int(abs(end - start) / 12.0) + 1)
    for index in range(count + 1):
        angle = math.radians(start + (end - start) * index / count)
        values.append(
            f"{_fmt(center[0] + radius * math.cos(angle))},"
            f"{_fmt(center[1] + radius * math.sin(angle))}"
        )
    return " ".join(values)


def _make_svg(geometry: Geometry, path: Path) -> None:
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 850 510" '
        'width="1700" height="1020" role="img" aria-label="P-7511A/B body-only silhouette">',
        '<rect width="850" height="510" fill="white"/>',
    ]
    for item in geometry.items:
        cls = item.layer.lower().replace("-", "_")
        if item.kind == "line":
            (x1, y1), (x2, y2) = item.values
            parts.append(
                f'<line class="{cls}" x1="{_fmt(x1)}" y1="{_fmt(y1)}" '
                f'x2="{_fmt(x2)}" y2="{_fmt(y2)}"/>'
            )
        elif item.kind == "polyline":
            points, closed = item.values
            coords = " ".join(f"{_fmt(x)},{_fmt(y)}" for x, y in points)
            parts.append(
                f'<polyline class="{cls}" points="{coords}" '
                f'data-closed="{str(closed).lower()}"/>'
            )
        elif item.kind == "circle":
            (cx, cy), radius = item.values
            parts.append(
                f'<circle class="{cls}" cx="{_fmt(cx)}" cy="{_fmt(cy)}" '
                f'r="{_fmt(radius)}"/>'
            )
        elif item.kind == "arc":
            center, radius, start, end = item.values
            parts.append(
                f'<polyline class="{cls}" points="{_arc_points(center, radius, start, end)}"/>'
            )
        elif item.kind == "text":
            value, (x, y), height = item.values
            parts.append(
                f'<text class="{cls}" x="{_fmt(x)}" y="{_fmt(y)}" '
                f'font-size="{_fmt(height)}">{html.escape(value)}</text>'
            )
    parts.append("</svg>")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(parts) + "\n", encoding="utf-8", newline="\n")


def _sha(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _make_report(model: dict, dxf: Path, svg: Path, report: Path) -> None:
    report.parent.mkdir(parents=True, exist_ok=True)
    width = model["reference_envelope"]["width"]
    height = model["reference_envelope"]["height"]
    report.write_text(
        f"""# P-7511 body-only silhouette canary

card: {CARD_ID}
station: P-7511A/B
status: NTS / PRELIMINARY / NON-RELEASE

## Scope

This is a body-only visual reconstruction of the middle side/front elevation. It repairs the old-style horizontal pump silhouette with an asymmetric volute, left suction flange/stub, short integral discharge neck, compact coupling, ribbed motor, terminal box, rear cap, aligned feet, and a thin common baseline.

The prior #26 preview was too generic and process-detail-heavy. This repair removes process-dominated content and adds the pump-body and motor cues required by the live card. It does not promote installed engineering data.

## Geometry contract

- reference envelope: {width} x {height}, visual ratio only
- shaft axis: approximately 0.423 of the reference height
- short integral discharge neck with horizontal top flange
- motor rib/fan-fin lines: 14 visible lines
- support feet: aligned to the common baseline

## Explicit omissions

Instrument bubbles, valve train, long process piping, seal-plan annotation, title block, vertical pumps, manufacturer identity, actual installed dimensions, and pressure/material/class/rating/flow/head/spec values are omitted.

engineering acceptance: false
actual installed dimensions: UNKNOWN

## Artifact hashes

- {dxf.name}: {_sha(dxf)}
- {svg.name}: {_sha(svg)}

This canary is editable vector geometry and a visual owner-review aid only; it is not a final DWG or release artifact.
""",
        encoding="utf-8",
        newline="\n",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--dxf", type=Path, required=True)
    parser.add_argument("--svg", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    model = _validate_model(args.model)
    geometry = build_geometry()
    _make_dxf(geometry, args.dxf)
    _make_svg(geometry, args.svg)
    _make_report(model, args.dxf, args.svg, args.report)
    print(f"generated {args.dxf}")
    print(f"generated {args.svg}")
    print(f"generated {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
