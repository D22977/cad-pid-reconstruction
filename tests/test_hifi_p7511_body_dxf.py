"""Acceptance tests for the P-7511 old-style horizontal body repair."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

import ezdxf
import pytest

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "data" / "hifi" / "p7511-body-reference-v1.json"
GENERATOR = ROOT / "src" / "generate_hifi_p7511_body_dxf.py"


def _run_generator(tmp_path: Path) -> dict[str, Path]:
    outputs = {
        "dxf": tmp_path / "body.dxf",
        "svg": tmp_path / "body.svg",
        "report": tmp_path / "body.md",
    }
    result = subprocess.run(
        [
            sys.executable,
            str(GENERATOR),
            "--model",
            str(MODEL),
            "--dxf",
            str(outputs["dxf"]),
            "--svg",
            str(outputs["svg"]),
            "--report",
            str(outputs["report"]),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert all(path.is_file() for path in outputs.values())
    return outputs


def _entity_points(doc: ezdxf.document.Drawing) -> list[tuple[float, float]]:
    points: list[tuple[float, float]] = []
    for entity in doc.modelspace():
        kind = entity.dxftype()
        if kind == "LINE":
            points.extend(
                [(entity.dxf.start.x, entity.dxf.start.y),
                 (entity.dxf.end.x, entity.dxf.end.y)]
            )
        elif kind in {"CIRCLE", "ARC"}:
            center = entity.dxf.center
            radius = float(entity.dxf.radius)
            points.extend(
                [(center.x - radius, center.y - radius),
                 (center.x + radius, center.y + radius)]
            )
        elif kind == "LWPOLYLINE":
            points.extend((float(x), float(y)) for x, y, *_ in entity.get_points())
    return points


def _text_entities(doc: ezdxf.document.Drawing) -> list[str]:
    values: list[str] = []
    for entity in doc.modelspace():
        if entity.dxftype() == "TEXT":
            values.append(str(entity.dxf.text))
        elif entity.dxftype() == "MTEXT":
            values.append(str(entity.text))
    return values


def test_reference_model_declares_body_only_contract() -> None:
    model = json.loads(MODEL.read_text(encoding="utf-8"))
    assert model["protocol"] == "CADPID_HIFI_P7511_BODY_REFERENCE_V1"
    assert model["card_id"] == "CADPID-HIFI-P7511-BODY-REPAIR-01"
    assert model["station"] == "P-7511A/B"
    assert model["drawing_status"] == ["NTS", "PRELIMINARY", "NON-RELEASE"]
    envelope = model["reference_envelope"]
    assert envelope["width"] == 850
    assert envelope["height"] == 520
    assert envelope["ratio"] == pytest.approx(850 / 520)
    contract = model["geometry_contract"]
    assert contract["main_view"] == "middle side/front elevation"
    assert contract["discharge"] == "short integral neck with horizontal top flange"
    assert contract["motor"]["minimum_visible_rib_lines"] >= 8
    raw = MODEL.read_text(encoding="utf-8")
    assert "DN50" not in raw and "PN16" not in raw


def test_body_dxf_is_editable_audited_and_contains_required_silhouette(tmp_path: Path) -> None:
    outputs = _run_generator(tmp_path)
    doc = ezdxf.readfile(outputs["dxf"])
    audit = doc.audit()
    assert not audit.errors
    kinds = {entity.dxftype() for entity in doc.modelspace()}
    assert {"LWPOLYLINE", "LINE", "CIRCLE", "ARC", "TEXT"} <= kinds
    assert not kinds.intersection({"INSERT", "IMAGE", "RASTERIMAGE"})
    layers = {entity.dxf.layer for entity in doc.modelspace()}
    allowed = {
        "EQUIP-CASING", "EQUIP-SUPPORT", "EQUIP-MOTOR",
        "EQUIP-COUPLING", "TEXT", "CENTERLINE",
    }
    assert layers <= allowed
    assert {"EQUIP-CASING", "EQUIP-SUPPORT", "EQUIP-MOTOR"} <= layers
    motor_lines = [
        entity for entity in doc.modelspace()
        if entity.dxftype() == "LINE" and entity.dxf.layer == "EQUIP-MOTOR"
    ]
    assert len(motor_lines) >= 8
    motor_polylines = [
        entity for entity in doc.modelspace()
        if entity.dxftype() == "LWPOLYLINE" and entity.dxf.layer == "EQUIP-MOTOR"
    ]
    assert any(max(float(y) for _, y, *_ in entity.get_points()) > 330 for entity in motor_polylines)
    assert any(
        entity.dxftype() in {"ARC", "CIRCLE"} and entity.dxf.layer == "EQUIP-MOTOR"
        for entity in doc.modelspace()
    )


def test_body_preview_has_envelope_and_no_process_content(tmp_path: Path) -> None:
    outputs = _run_generator(tmp_path)
    doc = ezdxf.readfile(outputs["dxf"])
    points = _entity_points(doc)
    assert points
    xs, ys = zip(*points)
    assert min(xs) >= -2 and max(xs) <= 852
    assert min(ys) >= -2 and max(ys) <= 522
    assert (max(xs) - min(xs)) / (max(ys) - min(ys)) == pytest.approx(
        850 / 520, rel=0.03
    )
    exact_text = _text_entities(doc)
    assert "P-7511A/B" in exact_text
    assert "NTS / PRELIMINARY / NON-RELEASE" in exact_text
    assert not {value.upper() for value in exact_text}.intersection({"PI", "FI", "LI"})
    assert not any("valve" in value.lower() for value in exact_text)
    assert not {"PIPING", "INSTRUMENT"}.intersection(
        {entity.dxf.layer for entity in doc.modelspace()}
    )
    svg = outputs["svg"].read_text(encoding="utf-8")
    assert "<svg" in svg and "</svg>" in svg
    assert not re.search(r"<text[^>]*>\s*(?:PI|FI|LI)\s*</text>", svg, re.I)
    assert "valve" not in svg.lower()
    assert "DN50" not in svg and "PN16" not in svg
    report = outputs["report"].read_text(encoding="utf-8")
    assert "body-only" in report
    assert "short integral discharge neck" in report
    assert "too generic and process-detail-heavy" in report


def test_body_generation_is_byte_deterministic(tmp_path: Path) -> None:
    first = _run_generator(tmp_path / "first")
    second = _run_generator(tmp_path / "second")
    for key in first:
        assert hashlib.sha256(first[key].read_bytes()).digest() == hashlib.sha256(
            second[key].read_bytes()
        ).digest()


def test_outputs_make_no_unsupported_engineering_claims(tmp_path: Path) -> None:
    outputs = _run_generator(tmp_path)
    content = "\n".join(path.read_text(encoding="utf-8", errors="ignore") for path in outputs.values())
    assert not re.search(r"\b(?:DN50|PN16|300#|150#|MPa|bar|m3/h)\b", content, re.I)
    assert "engineering acceptance: false" in content
    assert "actual installed dimensions: UNKNOWN" in content

