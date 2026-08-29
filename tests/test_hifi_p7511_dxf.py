"""Acceptance tests for the bounded P-7511A/B HIFI canary."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

import ezdxf


ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "data" / "hifi" / "p7511-anchor-model.json"
GENERATOR = ROOT / "src" / "generate_hifi_p7511_dxf.py"


def _run_generator(tmp_path: Path) -> tuple[Path, Path, Path]:
    dxf_path = tmp_path / "p7511-hifi-canary.dxf"
    svg_path = tmp_path / "p7511-hifi-canary.svg"
    report_path = tmp_path / "p7511-hifi-canary-report.md"
    result = subprocess.run(
        [
            sys.executable,
            str(GENERATOR),
            "--model",
            str(MODEL),
            "--dxf",
            str(dxf_path),
            "--svg",
            str(svg_path),
            "--report",
            str(report_path),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr or result.stdout
    assert dxf_path.exists()
    assert svg_path.exists()
    assert report_path.exists()
    return dxf_path, svg_path, report_path


def test_anchor_model_declares_normalized_visual_provenance() -> None:
    model = json.loads(MODEL.read_text(encoding="utf-8"))
    assert model["card_id"] == "CADPID-HIFI-P7511-CANARY-01"
    assert model["station"] == "P-7511A/B"
    assert model["drawing_status"] == ["NTS", "PRELIMINARY", "NON-RELEASE"]
    assert model["normalized_envelope"]["D_units"] == 20
    assert model["provenance_classes"] == [
        "VERIFIED_PUBLISHED_DIMENSION",
        "FAMILY_PROPORTION_INFERENCE",
        "VISUAL_REFERENCE_INFERENCE",
        "SOURCE_TEXT_EVIDENCE",
    ]
    assert model["engineering_unknowns"]


def test_canary_has_required_editable_visual_inventory(tmp_path: Path) -> None:
    dxf_path, _, _ = _run_generator(tmp_path)
    doc = ezdxf.readfile(dxf_path)
    auditor = doc.audit()
    assert not auditor.has_errors

    entities = list(doc.modelspace())
    types = {entity.dxftype() for entity in entities}
    assert {"LWPOLYLINE", "LINE", "CIRCLE", "ARC", "TEXT"} <= types
    assert "IMAGE" not in types
    assert "RASTERIMAGE" not in types

    layer_names = {entity.dxf.layer for entity in entities}
    assert {
        "EQUIP-CASING",
        "EQUIP-SUPPORT",
        "EQUIP-MOTOR",
        "EQUIP-COUPLING",
        "PIPING",
        "PIPING-VALVE",
        "INSTRUMENT",
        "TEXT",
        "NOTES",
    } <= layer_names

    inserts = [entity for entity in entities if entity.dxftype() == "INSERT"]
    assert any(entity.dxf.name == "HIFI_DOUBLE_TRIANGLE_VALVE" for entity in inserts)
    assert any(entity.dxf.name == "HIFI_VOLUTE_CASING" for entity in inserts)


def test_canary_contains_only_p7511_text_and_required_labels(tmp_path: Path) -> None:
    dxf_path, svg_path, report_path = _run_generator(tmp_path)
    doc = ezdxf.readfile(dxf_path)
    text = "\n".join(
        entity.dxf.text
        for entity in doc.modelspace()
        if entity.dxftype() in {"TEXT", "MTEXT"}
    )
    for required in (
        "P-7511A/B",
        "VOC KO Drum Pump",
        "FROM D-7511 BTM",
        "Seal Plan 11/52",
        "NTS",
        "PRELIMINARY",
        "NON-RELEASE",
        "PI",
        "FI",
        "LI",
    ):
        assert required in text
    for forbidden_station in ("P-3635", "P-3637", "P-7509"):
        assert forbidden_station not in text
    assert "P-7511A/B" in svg_path.read_text(encoding="utf-8")
    report = report_path.read_text(encoding="utf-8")
    assert "VISUAL_REFERENCE_INFERENCE" in report
    assert "not installed-dimension authority" in report


def test_canary_geometry_is_bounded_and_has_double_triangle_valve(tmp_path: Path) -> None:
    dxf_path, _, _ = _run_generator(tmp_path)
    doc = ezdxf.readfile(dxf_path)
    entities = list(doc.modelspace())
    points = []
    for entity in entities:
        if entity.dxftype() == "LINE":
            points.extend([entity.dxf.start, entity.dxf.end])
        elif entity.dxftype() in {"CIRCLE", "ARC"}:
            points.append(entity.dxf.center)
            radius = entity.dxf.radius
            points.extend(
                [
                    (entity.dxf.center.x - radius, entity.dxf.center.y),
                    (entity.dxf.center.x + radius, entity.dxf.center.y),
                ]
            )
        elif entity.dxftype() == "LWPOLYLINE":
            points.extend((x, y) for x, y, *_ in entity.get_points())
        elif entity.dxftype() == "INSERT":
            points.append(entity.dxf.insert)
    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    assert min(xs) >= -45
    assert max(xs) <= 85
    assert min(ys) >= -12
    assert max(ys) <= 70

    valve = next(
        entity
        for entity in entities
        if entity.dxftype() == "INSERT"
        and entity.dxf.name == "HIFI_DOUBLE_TRIANGLE_VALVE"
    )
    valve_block = doc.blocks[valve.dxf.name]
    valve_polylines = [entity for entity in valve_block if entity.dxftype() == "LWPOLYLINE"]
    assert len(valve_polylines) == 2
    assert all(entity.dxf.layer == "PIPING-VALVE" for entity in valve_polylines)


def test_canary_generation_is_byte_deterministic(tmp_path: Path) -> None:
    first = _run_generator(tmp_path / "first")
    second = _run_generator(tmp_path / "second")
    for left, right in zip(first, second):
        assert hashlib.sha256(left.read_bytes()).digest() == hashlib.sha256(
            right.read_bytes()
        ).digest()


def test_canary_has_no_unsupported_engineering_claims(tmp_path: Path) -> None:
    dxf_path, _, report_path = _run_generator(tmp_path)
    doc = ezdxf.readfile(dxf_path)
    text = "\n".join(
        entity.dxf.text
        for entity in doc.modelspace()
        if entity.dxftype() in {"TEXT", "MTEXT"}
    )
    report = report_path.read_text(encoding="utf-8")
    for unsupported in ("300#", "150#", "DN", "MPa", "bar", "mm", "m3/h"):
        assert not re.search(rf"(?<![A-Za-z0-9]){re.escape(unsupported)}(?![A-Za-z0-9])", text)
        assert not re.search(rf"(?<![A-Za-z0-9]){re.escape(unsupported)}(?![A-Za-z0-9])", report)
    assert "actual installed model identity: UNKNOWN" in report
    assert "engineering acceptance: false" in report

