import copy
import json
from pathlib import Path

import pytest

from src.generate_preliminary_dxf import (
    REQUIRED_LAYERS,
    REQUIRED_TAGS,
    audit_document,
    build_document,
    generate_outputs,
    load_model,
    summarize_document,
    validate_model,
)


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "reconstruction-v0.json"


def text_values(document):
    return [entity.dxf.text for entity in document.modelspace() if entity.dxftype() == "TEXT"]


def test_source_bound_model_contains_required_tags_and_safe_unresolved_fields():
    model = load_model(DATA_PATH)
    assert model["coordinate_system"] == "SOURCE_COORD_UNITS"
    assert model["scale"] == "NTS"
    assert set(model["source_evidence"]) == {"docx", "pdf", "png"}
    assert validate_model(model)["passed"] is True

    document = build_document(model)
    values = text_values(document)
    assert values.count("PRELIMINARY - NOT FOR ENGINEERING RELEASE") == 1
    assert values.count("SOURCE_COORD_UNITS / NTS") == 1
    for tag in REQUIRED_TAGS:
        assert values.count(tag) == 1
    assert all(layer in document.layers for layer in REQUIRED_LAYERS)
    assert "150#C" not in "\n".join(values)
    assert "300# RF" not in "\n".join(values)


def test_defect_regressions_bind_p7509_valve_and_reject_vertical_outlier():
    model = load_model(DATA_PATH)
    summary = summarize_document(build_document(model), model)
    regressions = summary["defect_regressions"]
    assert regressions["p7509_control_valve_zone"]["passed"] is True
    assert regressions["p7509_control_valve_zone"]["center_x"] == 625
    assert regressions["p7509_control_valve_zone"]["not_in_p3637_zone"] is True
    assert regressions["vertical_valve_outlier"]["passed"] is True
    assert regressions["vertical_valve_outlier"]["max_y"] < 100

    bad_model = copy.deepcopy(model)
    bad_model["equipment"][3]["control_valve"]["endpoint"] = [903, 900]
    with pytest.raises(ValueError, match="vertical valve outlier"):
        validate_model(bad_model)


def test_audit_bbox_inventory_and_deterministic_normalized_regeneration(tmp_path):
    model = load_model(DATA_PATH)
    first = generate_outputs(
        DATA_PATH,
        tmp_path / "one.dxf",
        tmp_path / "one-report.json",
    )
    second = generate_outputs(
        DATA_PATH,
        tmp_path / "two.dxf",
        tmp_path / "two-report.json",
    )
    assert first["audit"]["unrecoverable_errors"] == 0
    assert first["entity_inventory"]["total"] > 0
    assert first["bbox"]["min_x"] <= -25
    assert first["bbox"]["max_x"] >= 940
    assert first["bbox"]["max_y"] <= model["source_envelope"]["max_y"]
    assert first["normalized_inventory"] == second["normalized_inventory"]
    report = json.loads((tmp_path / "one-report.json").read_text(encoding="utf-8"))
    assert report["card_id"] == "CADPID-DXF-CANARY-02"
    assert report["preliminary_non_release"] is True
    assert report["dxf_sha256"]
    assert report["source_hashes_used"]["docx"]["sha256"] == (
        "C92BB1312FEC2080CBD97A352FFADA1EEC40DA01C2C41BF0B3BF560BB458F934"
    )
