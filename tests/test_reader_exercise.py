"""Synthetic software fixtures only; never participant sessions or benefit evidence."""

import copy
import json
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from prepare_reader_exercise import prepare, write_json  # noqa: E402
from score_reader_exercise import score  # noqa: E402

DATA = Path(os.environ.get("NUCLEILENS_READER_DATASET", str(ROOT / "data/raw/BBBC039")))


@pytest.fixture(scope="module")
def bundle(tmp_path_factory):
    root = tmp_path_factory.mktemp("reader-synthetic")
    served, private = root / "served", root / "private"
    ui = root / "synthetic-ui"
    ui.mkdir()
    for name in ("index.html", "app.js", "style.css"):
        (ui / name).write_text("SYNTHETIC SOFTWARE FIXTURE ONLY")
    manifest = prepare(DATA, served, private, assets_directory=ui)
    return root, served, private, manifest


def synthetic_record(bundle):
    _, served, _, manifest = bundle
    tasks = []
    for assignment in manifest["assignments"]["P01"]:
        asset = json.loads((served / f"{assignment['field_id']}-{assignment['arm_id']}.json").read_text())
        baseline = {r["id"]: r["baseline_count"] for r in asset["regions"]}
        tasks.append(
            {
                **assignment,
                "started_at": "2026-10-09T00:00:00Z",
                "ended_at": "2026-10-09T00:00:01Z",
                "elapsed_ms": 1000,
                "visibility_interruptions_ms": [200],
                "status": "completed",
                "reason": "",
                "comprehension": "SYNTHETIC FIXTURE",
                "regions": [
                    {
                        "tile_id": tile,
                        "baseline_count": baseline[tile],
                        "entered_count": baseline[tile],
                        "uncertainty": 1,
                        "confirmed": True,
                        "status": "completed",
                        "reason": "",
                    }
                    for tile in assignment["tile_ids"]
                ],
            }
        )
    return {
        "schema_version": 1,
        "protocol_hash": manifest["protocol_hash"],
        "participant_id": "P01",
        "synthetic_test": True,
        "experience_band": "unspecified",
        "retention_choice": "retain",
        "consent_acknowledged": True,
        "tasks": tasks,
    }


def run_record(bundle, record, allow=True):
    root, served, private, _ = bundle
    path = root / "SYNTHETIC-export.json"
    write_json(path, record)
    return score(private, served, [path], allow)


def test_deterministic_bundle(bundle, tmp_path):
    _, served, private, _ = bundle
    prepare(DATA, tmp_path / "served", tmp_path / "private", assets_directory=bundle[0] / "synthetic-ui")
    for original, second in [(served, tmp_path / "served"), (private, tmp_path / "private")]:
        assert {p.name: p.read_bytes() for p in original.iterdir()} == {
            p.name: p.read_bytes() for p in second.iterdir()
        }


def test_balanced_assignments_and_no_leaks(bundle):
    _, served, _, manifest = bundle
    for tasks in manifest["assignments"].values():
        assert len({t["field_id"] for t in tasks}) == 4
        assert [t["arm_id"] for t in tasks].count("A") == 2
        assert all(len(set(t["tile_ids"])) == 4 for t in tasks)
    for index in range(4):
        assert sum(tasks[index]["arm_id"] == "A" for tasks in manifest["assignments"].values()) == 3
    forbidden = {
        "reference_count",
        "f1",
        "annotation_count",
        "benchmark",
        "filename",
        "comparators",
        "analysis_ms",
    }

    def walk(value):
        if isinstance(value, dict):
            assert not forbidden.intersection(value)
            for child in value.values():
                walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)

    for path in served.glob("*.json"):
        walk(json.loads(path.read_text()))
    for path in served.glob("F*-A.json"):
        asset = json.loads(path.read_text())
        assert set(asset["regions"][0]) == {"id", "bbox", "baseline_count"}
        assert "alternative_outline_pngs" not in asset


def test_synthetic_default_rejection_and_label(bundle):
    record = synthetic_record(bundle)
    with pytest.raises(ValueError, match="Synthetic export rejected"):
        run_record(bundle, record, False)
    output = run_record(bundle, record)
    assert output["synthetic_test"] is True
    assert "NOT HUMAN OBSERVATIONS" in output["evidence_label"]
    assert len(output["participants"]) == 1


def test_incomplete_and_missing_retained(bundle):
    record = synthetic_record(bundle)
    record["tasks"].pop()
    task = record["tasks"][0]
    task.update(status="failed", reason="Synthetic interruption")
    task["regions"][0].update(
        status="unresolved",
        entered_count=None,
        uncertainty=None,
        confirmed=False,
        reason="Synthetic unresolved",
    )
    tasks = run_record(bundle, record)["participants"][0]["tasks"]
    assert tasks[0]["status"] == "failed"
    assert tasks[0]["regions"][0]["absolute_error"] is None
    assert tasks[-1]["status"] == "missing"


@pytest.mark.parametrize(
    "mutation",
    [
        "protocol",
        "participant",
        "field",
        "tile",
        "input",
        "config",
        "assignment",
        "count",
        "uncertainty",
        "status",
        "duplicate",
        "baseline",
        "synthetic_type",
    ],
)
def test_invalid_export_rejected(bundle, mutation):
    record = synthetic_record(bundle)
    task = record["tasks"][0]
    region = task["regions"][0]
    if mutation == "protocol":
        record["protocol_hash"] = "bad"
    elif mutation == "participant":
        record["participant_id"] = "P07"
    elif mutation == "field":
        task["field_id"] = "Q01"
    elif mutation == "tile":
        region["tile_id"] = 20
    elif mutation == "input":
        task["input_hash"] = "bad"
    elif mutation == "config":
        task["config_hash"] = "bad"
    elif mutation == "assignment":
        task["assignment_hash"] = "bad"
    elif mutation == "count":
        region["entered_count"] = True
    elif mutation == "uncertainty":
        region["uncertainty"] = 4
    elif mutation == "status":
        region["status"] = "invented"
    elif mutation == "duplicate":
        record["tasks"][1] = copy.deepcopy(task)
    elif mutation == "baseline":
        region["baseline_count"] += 1
    elif mutation == "synthetic_type":
        record["synthetic_test"] = 1
    with pytest.raises(ValueError):
        run_record(bundle, record)


def test_duplicate_exports_and_tampered_assets(bundle):
    root, served, private, _ = bundle
    record = synthetic_record(bundle)
    path = root / "SYNTHETIC-export.json"
    write_json(path, record)
    with pytest.raises(ValueError, match="Duplicate participant"):
        score(private, served, [path, path], True)
    asset = served / "F01-A.json"
    original = asset.read_bytes()
    try:
        asset.write_bytes(original + b" ")
        with pytest.raises(ValueError, match="Served integrity"):
            score(private, served, [path], True)
    finally:
        asset.write_bytes(original)


def test_duplicate_json_keys_rejected(tmp_path):
    from score_reader_exercise import load

    path = tmp_path / "duplicate.json"
    path.write_text('{"synthetic_test":true,"synthetic_test":false}')
    with pytest.raises(ValueError, match="Duplicate JSON"):
        load(path)


def test_withdrawal_rejected_before_reference_decode(bundle, monkeypatch):
    from PIL import Image

    def forbidden(*args, **kwargs):
        raise AssertionError("Reference must not decode for withdrawn record")

    monkeypatch.setattr(Image, "open", forbidden)
    record = synthetic_record(bundle)
    record["retention_choice"] = "delete"
    with pytest.raises(ValueError, match="Withdrawn export"):
        run_record(bundle, record)


def test_size_bound(tmp_path):
    from score_reader_exercise import load

    path = tmp_path / "oversize.json"
    with path.open("wb") as stream:
        stream.truncate(10 * 1024 * 1024 + 1)
    with pytest.raises(ValueError, match="10 MB"):
        load(path)


def test_frozen_guard(tmp_path):
    from hashlib import sha256

    from prepare_reader_exercise import validate_frozen

    (tmp_path / "evaluation/frozen").mkdir(parents=True)
    (tmp_path / "src/nuclei_lens").mkdir(parents=True)
    source = tmp_path / "src/nuclei_lens/core.py"
    source.write_text("synthetic source")
    protocol = {
        "config": {"threshold_factor": 0.85},
        "source_sha256": {"core.py": sha256(source.read_bytes()).hexdigest()},
    }
    write_json(tmp_path / "evaluation/frozen/protocol.json", protocol)
    write_json(tmp_path / "evaluation/frozen/config.json", protocol["config"])
    assert validate_frozen(tmp_path) == protocol["config"]
    source.write_text("changed synthetic source")
    with pytest.raises(ValueError, match="Frozen source"):
        validate_frozen(tmp_path)
    write_json(tmp_path / "evaluation/frozen/config.json", {"threshold_factor": 0.9})
    with pytest.raises(ValueError, match="Frozen configuration"):
        validate_frozen(tmp_path)


def test_secondary_metrics_same_tiles_and_complete_pair_gate(bundle):
    record = synthetic_record(bundle)
    record["tasks"][0]["regions"][0]["entered_count"] += 1
    output = run_record(bundle, record)
    participant = output["participants"][0]
    assert participant["paired_data_complete"]
    assert participant["paired_descriptive_B_minus_A"] is not None
    for arm in ("A", "B"):
        summary = participant["descriptive_by_arm"][arm]
        regions = [r for t in participant["tasks"] if t["arm_id"] == arm for r in t["regions"]]
        assert (
            summary["same_assigned_tile_baseline_mae"]
            == sum(r["baseline_absolute_error"] for r in regions) / 8
        )
        assert summary["mean_baseline_minus_entered_error_reduction"] == pytest.approx(
            summary["same_assigned_tile_baseline_mae"] - summary["mean_absolute_local_count_error"]
        )
        assert all(
            r["error_reduction"] == r["baseline_absolute_error"] - r["absolute_error"] for r in regions
        )
    record["tasks"].pop()
    participant = run_record(bundle, record)["participants"][0]
    assert not participant["paired_data_complete"]
    assert participant["paired_descriptive_B_minus_A"] is None
    arm = participant["descriptive_by_arm"]["B"]
    assert arm["observed_region_count"] == 4 and arm["scheduled_region_count"] == 8
    assert arm["mean_absolute_local_count_error"] is None
    assert arm["mean_baseline_minus_entered_error_reduction"] is None
    assert arm["partial_observed_only"] is not None
    assert arm["missing_tasks"] == 1 and arm["not_started_regions"] == 4
    assert "different tiles" in output["selection_difficulty_caveat"]
