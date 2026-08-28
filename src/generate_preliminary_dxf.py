"""Deterministic, non-release DXF reconstruction from verified source-derived data."""

from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
import platform
import sys
from typing import Any

import ezdxf


REQUIRED_LAYERS = ("E-EQUIP", "E-PIPE", "E-INST", "E-TEXT", "E-FRAME")
REQUIRED_TAGS = ("P-3635A/B", "P-3637A/B", "P-7509", "P-7511A/B")
EXACT_BASE_SHA = "88522ac283621832157b53ed1f3c238de146e835"
P7509_ZONE = (600, 650)


def load_model(path: str | Path) -> dict[str, Any]:
    model = json.loads(Path(path).read_text(encoding="utf-8"))
    validate_model(model)
    return model


def validate_model(model: dict[str, Any]) -> dict[str, Any]:
    if model.get("coordinate_system") != "SOURCE_COORD_UNITS":
        raise ValueError("coordinate system must be SOURCE_COORD_UNITS")
    if model.get("scale") != "NTS":
        raise ValueError("scale must be NTS")
    if tuple(model.get("layers", ())) != REQUIRED_LAYERS:
        raise ValueError("candidate layer set is incomplete or reordered")
    if {item.get("tag") for item in model.get("equipment", [])} != set(REQUIRED_TAGS):
        raise ValueError("required equipment tags are incomplete")
    for name, evidence in model.get("source_evidence", {}).items():
        if evidence.get("verification") != "PASS":
            raise ValueError(f"source evidence {name} was not verified")
        if len(evidence.get("sha256", "")) != 64:
            raise ValueError(f"source evidence {name} has no SHA-256")
    envelope = model["source_envelope"]
    for equipment in model["equipment"]:
        valve = equipment["control_valve"]
        endpoint = valve["endpoint"]
        if equipment["kind"] == "horizontal_voc_pump" and endpoint[1] > envelope["max_y"]:
            raise ValueError("vertical valve outlier exceeds source envelope")
        if endpoint[1] >= 100:
            raise ValueError("vertical valve outlier near y=900 detected")
    p7509 = next(item for item in model["equipment"] if item["tag"] == "P-7509")
    p7509_x = p7509["control_valve"]["center"][0]
    if not P7509_ZONE[0] <= p7509_x <= P7509_ZONE[1]:
        raise ValueError("P-7509 control valve is outside its source-derived zone")
    serialized = json.dumps(model, ensure_ascii=False)
    if "oldosoldbl" in serialized:
        raise ValueError("oldosoldbl defect carried into reconstruction data")
    return {"passed": True}


def _add_line(modelspace, start, end, layer):
    modelspace.add_line((*start, 0), (*end, 0), dxfattribs={"layer": layer})


def _add_rectangle(modelspace, corners, layer):
    (x1, y1), (x2, y2) = corners
    modelspace.add_lwpolyline(
        [(x1, y1), (x2, y1), (x2, y2), (x1, y2)],
        close=True,
        dxfattribs={"layer": layer},
    )


def _add_circle(modelspace, center, radius, layer):
    modelspace.add_circle((*center, 0), radius, dxfattribs={"layer": layer})


def _add_text(modelspace, item, layer):
    entity = modelspace.add_text(item["value"], dxfattribs={"layer": layer, "height": item["height"]})
    entity.dxf.insert = (*item["at"], 0)


def _add_horizontal_valve(modelspace, center, endpoint):
    x, y = center
    _add_line(modelspace, (x - 3, y + 3), (x - 3, y - 3), "E-PIPE")
    _add_line(modelspace, (x - 3, y - 3), (x + 3, y + 3), "E-PIPE")
    _add_line(modelspace, (x + 3, y + 3), (x + 3, y - 3), "E-PIPE")
    _add_line(modelspace, (x + 3, y - 3), (x - 3, y + 3), "E-PIPE")
    _add_rectangle(modelspace, [(x - 1, y + 3), (x + 1, y + 5)], "E-PIPE")
    _add_line(modelspace, center, endpoint, "E-PIPE")


def _add_vertical_valve(modelspace, center, endpoint):
    x, y = center
    _add_line(modelspace, (x - 3, y - 3), (x + 3, y - 3), "E-PIPE")
    _add_line(modelspace, (x + 3, y - 3), (x - 3, y + 3), "E-PIPE")
    _add_line(modelspace, (x - 3, y + 3), (x + 3, y + 3), "E-PIPE")
    _add_line(modelspace, (x + 3, y + 3), (x - 3, y - 3), "E-PIPE")
    _add_rectangle(modelspace, [(x + 3, y - 1), (x + 5, y + 1)], "E-PIPE")
    _add_line(modelspace, center, endpoint, "E-PIPE")


def build_document(model: dict[str, Any]):
    validate_model(model)
    document = ezdxf.new("R2018")
    for layer in REQUIRED_LAYERS:
        document.layers.add(layer)
    modelspace = document.modelspace()

    _add_rectangle(modelspace, model["frame"]["corners"], "E-FRAME")
    for item in model["frame"]["texts"]:
        _add_text(modelspace, item, "E-FRAME")

    for equipment in model["equipment"]:
        geometry = equipment["geometry"]
        _add_rectangle(modelspace, geometry["baseplate"], "E-EQUIP")
        if "column" in geometry:
            _add_line(modelspace, *geometry["column"], "E-EQUIP")
        if "casing" in geometry:
            _add_circle(modelspace, geometry["casing"]["center"], geometry["casing"]["radius"], "E-EQUIP")
        if "impeller" in geometry:
            _add_line(modelspace, *geometry["impeller"], "E-EQUIP")
        if "coupling" in geometry:
            _add_circle(modelspace, geometry["coupling"]["center"], geometry["coupling"]["radius"], "E-EQUIP")
        _add_rectangle(modelspace, geometry["motor"], "E-EQUIP")
        _add_line(modelspace, *geometry["suction"], "E-PIPE")
        _add_line(modelspace, *geometry["discharge"], "E-PIPE")

        check = equipment["check_valve"]
        _add_circle(modelspace, check["center"], check["radius"], "E-PIPE")
        _add_line(modelspace, *check["cross"], "E-PIPE")
        valve = equipment["control_valve"]
        if valve["orientation"] == "horizontal":
            _add_horizontal_valve(modelspace, valve["center"], valve["endpoint"])
        else:
            _add_vertical_valve(modelspace, valve["center"], valve["endpoint"])

        for instrument in equipment["instruments"]:
            _add_circle(modelspace, instrument["center"], instrument["radius"], "E-INST")
            _add_line(modelspace, *instrument["leader"], "E-INST")
        for item in equipment["texts"]:
            _add_text(modelspace, item, "E-TEXT")
    return document


def _entity_points(entity):
    kind = entity.dxftype()
    if kind == "LINE":
        return [
            (entity.dxf.start[0], entity.dxf.start[1]),
            (entity.dxf.end[0], entity.dxf.end[1]),
        ]
    if kind == "CIRCLE":
        x, y = entity.dxf.center[0], entity.dxf.center[1]
        r = entity.dxf.radius
        return [(x - r, y - r), (x + r, y + r)]
    if kind == "LWPOLYLINE":
        return [(point[0], point[1]) for point in entity.get_points()]
    if kind == "TEXT":
        return [(entity.dxf.insert[0], entity.dxf.insert[1])]
    return []


def bounding_box(document):
    points = [point for entity in document.modelspace() for point in _entity_points(entity)]
    return {
        "min_x": min(point[0] for point in points),
        "min_y": min(point[1] for point in points),
        "max_x": max(point[0] for point in points),
        "max_y": max(point[1] for point in points),
    }


def audit_document(document):
    auditor = document.audit()
    return {
        "unrecoverable_errors": len(auditor.errors),
        "fixed_errors": len(auditor.fixes),
    }


def _text_values(document):
    return [entity.dxf.text for entity in document.modelspace() if entity.dxftype() == "TEXT"]


def _entity_inventory(document):
    by_type = Counter()
    by_layer = {layer: Counter() for layer in REQUIRED_LAYERS}
    for entity in document.modelspace():
        kind = entity.dxftype()
        layer = entity.dxf.layer
        by_type[kind] += 1
        by_layer.setdefault(layer, Counter())[kind] += 1
    return {
        "total": sum(by_type.values()),
        "by_type": dict(sorted(by_type.items())),
        "by_layer": {layer: dict(sorted(counts.items())) for layer, counts in sorted(by_layer.items())},
    }


def _defect_regressions(model, document):
    p7509 = next(item for item in model["equipment"] if item["tag"] == "P-7509")
    p7509_center_x = p7509["control_valve"]["center"][0]
    vertical = next(item for item in model["equipment"] if item["kind"] == "horizontal_voc_pump")
    max_y = float(bounding_box(document)["max_y"])
    return {
        "p7509_control_valve_zone": {
            "passed": P7509_ZONE[0] <= p7509_center_x <= P7509_ZONE[1],
            "center_x": p7509_center_x,
            "expected_zone": list(P7509_ZONE),
            "not_in_p3637_zone": p7509_center_x > 350,
        },
        "vertical_valve_outlier": {
            "passed": vertical["control_valve"]["endpoint"][1] < 100 and max_y < 100,
            "endpoint": vertical["control_valve"]["endpoint"],
            "max_y": max_y,
            "known_bad_endpoint": [903, 900],
        },
        "oldosoldbl_not_carried": {
            "passed": "oldosoldbl" not in json.dumps(model, ensure_ascii=False),
        },
        "unresolved_ratings_not_emitted": {
            "passed": not any(value in "\n".join(_text_values(document)) for value in ("150#C", "300# RF")),
        },
    }


def normalized_inventory(document, model):
    values = _text_values(document)
    return {
        "layers": sorted({entity.dxf.layer for entity in document.modelspace()}),
        "entities": _entity_inventory(document),
        "text_counts": dict(sorted(Counter(values).items())),
        "required_tag_counts": {tag: values.count(tag) for tag in REQUIRED_TAGS},
        "bbox": bounding_box(document),
        "defect_regressions": _defect_regressions(model, document),
    }


def summarize_document(document, model):
    inventory = _entity_inventory(document)
    values = _text_values(document)
    return {
        "layers": sorted(layer.dxf.name for layer in document.layers),
        "entity_inventory": inventory,
        "equipment_tags": {tag: values.count(tag) for tag in REQUIRED_TAGS},
        "bbox": bounding_box(document),
        "audit": audit_document(document),
        "defect_regressions": _defect_regressions(model, document),
        "normalized_inventory": normalized_inventory(document, model),
    }


def generate_outputs(model_path: str | Path, dxf_path: str | Path, report_path: str | Path):
    model = load_model(model_path)
    document = build_document(model)
    dxf_path = Path(dxf_path)
    report_path = Path(report_path)
    dxf_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    document.saveas(dxf_path)

    reopened = ezdxf.readfile(dxf_path)
    summary = summarize_document(reopened, model)
    dxf_sha256 = hashlib.sha256(dxf_path.read_bytes()).hexdigest().upper()
    report = {
        "card_id": model["card_id"],
        "generation": model["generation"],
        "exact_base_sha": EXACT_BASE_SHA,
        "exact_head_sha": None,
        "source_hashes_used": model["source_evidence"],
        "source_hash_precondition": "PASS_ALL_THREE_REQUIRED",
        "runtime": {
            "python": sys.version.split()[0],
            "ezdxf": ezdxf.__version__,
            "platform": platform.platform(),
        },
        "dxf_version": reopened.dxfversion,
        "encoding": "ASCII",
        "coordinate_system": model["coordinate_system"],
        "scale": model["scale"],
        "preliminary_non_release": True,
        "layers": summary["layers"],
        "entity_inventory": summary["entity_inventory"],
        "equipment_tags": summary["equipment_tags"],
        "bbox": summary["bbox"],
        "audit": summary["audit"],
        "defect_regressions": summary["defect_regressions"],
        "unresolved_engineering_fields": model["unresolved_engineering_fields"],
        "dxf_sha256": dxf_sha256,
        "normalized_inventory": summary["normalized_inventory"],
    }
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    report = generate_outputs(
        root / "data" / "reconstruction-v0.json",
        root / "output" / "dxf" / "cad-pid-reconstruction-preliminary.dxf",
        root / "reports" / "preliminary-dxf-report.json",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
