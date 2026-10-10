"""Synthetic masks/archives only: no actual training-field metrics or inference."""

from __future__ import annotations

import base64
import copy
import sys
import zlib
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

import numpy as np
import pytest
import tifffile
from PIL import Image

from nuclei_lens import data

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts import annotated_model_case as case  # noqa: E402


def tiff_bytes(array):
    stream = BytesIO()
    tifffile.imwrite(stream, array, metadata=None)
    return stream.getvalue()


def png_bytes(array):
    stream = BytesIO()
    Image.fromarray(array).save(stream, format="PNG")
    return stream.getvalue()


def labels():
    result = np.zeros((32, 32), dtype=np.uint32)
    result[3:8, 3:8] = 1
    result[15:20, 15:20] = 2
    return result


@pytest.fixture
def fixture(tmp_path, monkeypatch):
    """An entire synthetic official-format field with supplied hashes."""
    root = tmp_path / "synthetic-repository"
    root.mkdir()
    protocol = {
        "protocol_id": "nucleilens-existing-training001-annotation-case-v1",
        "declared_at": "2026-10-10T00:00:00Z",
        "study_type": "SYNTHETIC SOFTWARE TEST ONLY",
        "sample_id": "training-001", "split": "training", "manifest_position_one_based": 1,
        "filename": "synthetic-training001.png",
        "image_source": "frontend/public/samples/training-001.tif",
        "dimensions": {"height": 32, "width": 32},
        "matching": {"iou_threshold": 0.5, "merge_split_hypothesis_iou_threshold": 0.1},
        "output_path": "evaluation/model-case/result.json",
    }
    protocol["source_sha256"] = {}
    for source in case.PINNED_SOURCES:
        target = root / source
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT / source).read_bytes())
        protocol["source_sha256"][source] = case.digest(target.read_bytes())

    image = np.arange(32 * 32, dtype=np.uint16).reshape(32, 32)
    image_payload = tiff_bytes(image)
    path = root / protocol["image_source"]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(image_payload)
    protocol["image_file_sha256"] = case.digest(image_payload)
    protocol["image_pixel_sha256"] = case.digest(image.tobytes())
    input_hash = case.digest(str(image.shape).encode() + str(image.dtype).encode() + image.tobytes())
    baseline = labels()
    cellpose = np.zeros_like(baseline)
    cellpose[baseline == 1] = np.iinfo(np.uint32).max
    cellpose[baseline == 2] = 7
    stardist = np.zeros_like(baseline)
    stardist[23:26, 23:26] = 10
    stardist[27:30, 27:30] = 500
    sample = {
        "schema_version": 1, "width": 32, "height": 32, "input_hash": input_hash,
        "raw_count": 2, "run_counts": [2], "software_version": "synthetic-fixture",
        "config": {"threshold_factor": 0.85}, "run_configs": [{"gamma": 1.0}],
        "label_maps": {"encoding": "zlib-base64-uint32-le", "runs": [
            base64.b64encode(zlib.compress(baseline.astype("<u4").tobytes())).decode()
        ]},
    }
    sample_path = root / "frontend/public/samples/training-001.json"
    sample_path.write_bytes(case.canonical_json(sample))
    protocol["methods"] = [{"id": case.METHODS[0], "source": str(sample_path.relative_to(root)),
                            "sha256": case.digest(sample_path.read_bytes()), "run_index": 0}]
    provenance = {
        "run_status": "completed", "nucleilens_input_hash": input_hash,
        "input_image": {"file_sha256": case.digest(image_payload),
                        "pixel_sha256": case.digest(image.tobytes()), "dimensions": protocol["dimensions"],
                        "dtype": "uint16", "pixel_count": 1024},
        "models": {},
    }
    for name, prediction in zip(case.METHODS[1:], (cellpose, stardist), strict=True):
        path = root / f"frontend/public/model-examples/training-001/{name}_mask.tif"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(tiff_bytes(prediction))
        file_hash, pixel_hash = case.digest(path.read_bytes()), case.pixel_hash(prediction)
        protocol["methods"].append({"id": name, "source": str(path.relative_to(root)),
                                    "sha256": file_hash, "pixel_sha256": pixel_hash,
                                    "known_instance_count": 2})
        provenance["models"][name] = {
            "status": "success", "instance_count": 2, "mask_tiff_path": path.name,
            "mask_file_sha256": file_hash, "mask_pixel_sha256": pixel_hash,
            "worker_provenance": {"framework": "synthetic-" + name, "framework_version": "fixture-only",
                                  "weight_files": [{"file": "synthetic.bin", "sha256": "a" * 64, "bytes": 4}],
                                  "parameters": {"gpu": False}, "device": "cpu"},
        }
    provenance_path = root / "frontend/public/model-examples/training-001/provenance.json"
    provenance_path.write_bytes(case.canonical_json(provenance))
    protocol["model_provenance_source"] = str(provenance_path.relative_to(root))
    protocol["model_provenance_sha256"] = case.digest(provenance_path.read_bytes())

    dataset_root = tmp_path / "synthetic-official-format"
    dataset_root.mkdir()
    annotation_colors = np.zeros((*baseline.shape, 3), dtype=np.uint8)
    # Reused first-channel color must become two separate instances, not one.
    annotation_colors[baseline > 0, 0] = 3
    contents = {
        "images": {"images/synthetic-training001.tif": image_payload},
        "masks": {"masks/" + protocol["filename"]: png_bytes(annotation_colors)},
        "metadata": {"metadata/training.txt": b"synthetic-training001.png\n",
                     "metadata/validation.txt": b"", "metadata/test.txt": b""},
    }
    protocol["archive_sha256"] = {}
    for name, files in contents.items():
        path = dataset_root / f"{name}.zip"
        with ZipFile(path, "w") as archive:
            for filename, payload in files.items():
                archive.writestr(filename, payload)
        protocol["archive_sha256"][name] = case.digest(path.read_bytes())
    # Only synthetic tests replace the dataset's pinned expected archive hashes.
    monkeypatch.setattr(data, "ARCHIVES", protocol["archive_sha256"].copy())
    monkeypatch.setattr(case, "ARCHIVES", protocol["archive_sha256"].copy())
    protocol_path = root / "evaluation/model-case/protocol.json"
    protocol_path.parent.mkdir(parents=True)
    protocol_path.write_bytes(case.canonical_json(protocol))
    return root, dataset_root, protocol_path, protocol, provenance, sample


def build(fixture):
    root, dataset, protocol_path, *_ = fixture
    return case.build_result(dataset, protocol_path, root=root)


def save_protocol(fixture):
    fixture[2].write_bytes(case.canonical_json(fixture[3]))


def save_provenance(fixture):
    root, _, _, protocol, provenance, _ = fixture
    path = root / protocol["model_provenance_source"]
    path.write_bytes(case.canonical_json(provenance))
    protocol["model_provenance_sha256"] = case.digest(path.read_bytes())
    save_protocol(fixture)


def test_sparse_dense_mapping_and_nonmonotonic_relabel_equivalence():
    original = labels()
    alternate = np.zeros_like(original)
    alternate[original == 1] = np.iinfo(np.uint32).max
    alternate[original == 2] = 7
    dense = case.dense_labels(alternate)
    assert dense[3, 3] == 2 and dense[15, 15] == 1
    assert dense.dtype == np.uint32 and dense.max() == 2
    assert case.partition_equivalent(original, alternate)
    assert not np.array_equal(original, alternate)
    assert case.agreement_metrics(original, alternate)["f1"] == 1


def test_equal_count_wrong_objects():
    truth = labels()
    wrong = np.zeros_like(truth)
    wrong[23:26, 23:26] = 1
    wrong[27:30, 27:30] = 2
    metrics = case.agreement_metrics(wrong, truth)
    assert metrics["count_error"] == metrics["count_absolute_error"] == 0
    assert metrics["tp"] == metrics["f1"] == metrics["precision"] == metrics["recall"] == 0
    assert metrics["fp"] == metrics["fn"] == 2
    assert not case.partition_equivalent(wrong, truth)


def test_partition_background_and_one_to_one_requirement():
    left = labels()
    merged = (left > 0).astype(np.uint32)
    assert np.array_equal(left > 0, merged > 0)
    assert not case.partition_equivalent(left, merged)
    assert not case.partition_equivalent(merged, left)
    changed_background = left.copy()
    changed_background[0, 0] = 1
    assert not case.partition_equivalent(left, changed_background)


def test_exact_iou_half_and_below():
    truth = np.zeros((32, 32), dtype=np.uint32)
    truth[1, 1:5] = 1
    prediction = np.zeros_like(truth)
    prediction[1, 1:3] = 1  # IoU is exactly 0.5, eligible.
    assert case.agreement_metrics(prediction, truth)["tp"] == 1
    prediction[1, 2] = 0  # IoU is now 0.25, ineligible.
    result = case.agreement_metrics(prediction, truth)
    assert result["tp"] == 0 and result["fp"] == result["fn"] == 1


@pytest.mark.parametrize("pixels,expected", [(1, 1), (2, 0)])
def test_merge_split_hypothesis_exact_point_one(pixels, expected):
    truth = np.zeros((32, 32), dtype=np.uint32)
    truth[1, 1:10] = 1  # Nine pixels
    truth[1, 10:10 + pixels] = 2
    merged = (truth > 0).astype(np.uint32)
    # Second object's IoU is 1/10 (inclusive) or 2/11. First object's
    # IoU also exceeds 0.1. Both therefore produce a merge hypothesis.
    assert case.agreement_metrics(merged, truth)["hypothetical_merge_objects"] == 1
    assert case.agreement_metrics(truth, merged)["hypothetical_split_objects"] == 1
    small = np.zeros_like(truth)
    small[1, 1:11] = 1
    small[1, 11:11 + pixels] = 2
    big = (small > 0).astype(np.uint32)
    # One pixel / 11 < 0.1; two / 12 >= 0.1.
    assert case.agreement_metrics(big, small)["hypothetical_merge_objects"] == 1 - expected


@pytest.mark.parametrize("bad", [
    np.zeros((32, 32), dtype=np.uint32), np.ones((32, 32), dtype=float),
    np.ones((32, 32), dtype=bool), -np.ones((32, 32), dtype=np.int32),
    np.full((32, 32), 2**32, dtype=np.uint64), np.ones((2, 2, 2), dtype=np.uint32),
    np.ones((0, 2), dtype=np.uint32),
])
def test_malformed_labels_rejected(bad):
    with pytest.raises(ValueError):
        case.validate_labels(bad)


@pytest.mark.parametrize("objects,side", [(4097, 65), (1025, 33)])
def test_matching_bound_before_evaluator(objects, side, monkeypatch):
    mask = np.zeros((side, side), dtype=np.uint32)
    mask.flat[:objects] = np.arange(1, objects + 1, dtype=np.uint32)

    def forbidden(*args, **kwargs):
        pytest.fail("Evaluator must not allocate an oversized IoU matrix")

    monkeypatch.setattr(case, "instance_metrics", forbidden)
    with pytest.raises(ValueError, match="Matching work exceeds"):
        case.agreement_metrics(mask, mask)


def test_synthetic_case_determinism_provenance_and_official_decoder(fixture):
    first, second = build(fixture), build(fixture)
    assert case.canonical_json(first) == case.canonical_json(second)
    assert first["case"]["inference_performed"] is False
    assert first["annotation"]["instance_count"] == 2
    assert first["methods"]["classical_baseline"]["metrics"]["f1"] == 1
    assert first["methods"]["cellpose_nuclei"]["metrics"]["f1"] == 1
    assert first["methods"]["stardist_2d_fluo"]["metrics"]["f1"] == 0
    assert first["pairwise"][0]["foreground_differing_pixels"] == 0
    assert first["pairwise"][0]["partition_equivalent"] is True
    assert first["pairwise"][1]["foreground_differing_pixels"] > 0
    assert first["pairwise"][1]["partition_equivalent"] is False
    assert first["protocol"]["sha256"] == case.digest(fixture[2].read_bytes())
    assert first["methods"]["cellpose_nuclei"]["provenance"]["framework_version"] == "fixture-only"
    assert str(fixture[0]) not in case.canonical_json(first).decode()
    assert "no generalization" in " ".join(first["limitations"])


def test_prediction_loading_precedes_official_annotation_decoding(fixture, monkeypatch):
    events = []
    baseline_loader, mask_loader = case.load_baseline, case.load_mask_tiff

    def baseline(*args):
        result = baseline_loader(*args)
        events.append("prediction")
        return result

    def mask(*args):
        result = mask_loader(*args)
        events.append("prediction")
        return result

    class RecordingDataset(data.Dataset):
        def annotations(self, filename):
            assert events == ["prediction"] * 3
            events.append("annotation")
            return super().annotations(filename)

    monkeypatch.setattr(case, "load_baseline", baseline)
    monkeypatch.setattr(case, "load_mask_tiff", mask)
    monkeypatch.setattr(case, "OfficialDataset", RecordingDataset)
    build(fixture)
    assert events == ["prediction", "prediction", "prediction", "annotation"]


@pytest.mark.parametrize("target", ["source", "image", "sample", "mask", "provenance", "archive"])
def test_hash_mismatch_prevents_annotation_load(fixture, monkeypatch, target):
    root, dataset, _, protocol, *_ = fixture
    paths = {
        "source": root / case.PINNED_SOURCES[0], "image": root / protocol["image_source"],
        "sample": root / protocol["methods"][0]["source"],
        "mask": root / protocol["methods"][1]["source"],
        "provenance": root / protocol["model_provenance_source"], "archive": dataset / "masks.zip",
    }
    path = paths[target]
    path.write_bytes(path.read_bytes() + b"corruption")
    monkeypatch.setattr(data.Dataset, "annotations", lambda *args: pytest.fail("Annotation loaded on failure"))
    with pytest.raises(ValueError, match="SHA-256"):
        build(fixture)


@pytest.mark.parametrize("change", ["pixel_hash", "count", "dimensions", "image_dtype", "private_path"])
def test_provenance_mismatch_before_annotation(fixture, monkeypatch, change):
    _, _, _, _, provenance, _ = fixture
    model = provenance["models"]["cellpose_nuclei"]
    if change == "pixel_hash":
        model["mask_pixel_sha256"] = "0" * 64
    elif change == "count":
        model["instance_count"] = 3
    elif change == "dimensions":
        provenance["input_image"]["dimensions"]["width"] = 31
    elif change == "image_dtype":
        provenance["input_image"]["dtype"] = "uint8"
    else:
        model["worker_provenance"]["weight_files"][0]["file"] = "/private/weights.bin"
    save_provenance(fixture)
    monkeypatch.setattr(data.Dataset, "annotations", lambda *args: pytest.fail("Annotation loaded on failure"))
    with pytest.raises(ValueError):
        build(fixture)


@pytest.mark.parametrize("change", ["threshold", "hypothesis_threshold", "run", "methods", "first_field"])
def test_protocol_cannot_change_declared_scope(fixture, change):
    protocol = fixture[3]
    if change == "threshold":
        protocol["matching"]["iou_threshold"] = 0.6
    elif change == "hypothesis_threshold":
        protocol["matching"]["merge_split_hypothesis_iou_threshold"] = 0.2
    elif change == "run":
        protocol["methods"][0]["run_index"] = 1
    elif change == "methods":
        protocol["methods"].reverse()
    else:
        protocol["filename"] = "another-field.png"
    save_protocol(fixture)
    with pytest.raises(ValueError):
        build(fixture)


@pytest.mark.parametrize("bad", [b'{} trailing', b'{"a":1,"a":2}', b'{"a":NaN}', b'[]'])
def test_malformed_json(bad):
    with pytest.raises(ValueError):
        case.read_json(bad)


def test_classical_compression_strictness(fixture):
    sample = copy.deepcopy(fixture[5])
    raw = labels().astype("<u4").tobytes()
    for payload in (zlib.compress(raw[:-1]), zlib.compress(raw) + b"tail",
                    zlib.compress(raw + raw), zlib.compress(raw)[:-1]):
        sample["label_maps"]["runs"][0] = base64.b64encode(payload).decode()
        with pytest.raises(ValueError, match="byte length/compression"):
            case.load_baseline(case.canonical_json(sample), (32, 32))
    sample["label_maps"]["runs"][0] = "not-base64!"
    with pytest.raises(ValueError, match="Malformed compressed"):
        case.load_baseline(case.canonical_json(sample), (32, 32))


@pytest.mark.parametrize("array", [np.ones((32, 32), dtype=np.uint16),
                                   np.ones((32, 32), dtype=np.int32),
                                   np.ones((31, 32), dtype=np.uint32)])
def test_mask_tiff_dtype_and_geometry(array):
    with pytest.raises(ValueError, match="uint32 raster"):
        case.load_mask_tiff(tiff_bytes(array), (32, 32))


def test_output_identical_noop_and_different_refused(tmp_path):
    output = tmp_path / "result.json"
    case.write_result(output, {"synthetic": True})
    initial = output.read_bytes()
    case.write_result(output, {"synthetic": True})
    assert output.read_bytes() == initial
    with pytest.raises(ValueError, match="overwrite differing"):
        case.write_result(output, {"synthetic": False})
    assert output.read_bytes() == initial
    link = tmp_path / "symlink.json"
    link.symlink_to(output)
    with pytest.raises(ValueError, match="symlink"):
        case.write_result(link, {"synthetic": True})


def test_private_or_escaping_asset_paths(tmp_path):
    for source in ("/private/mask.tif", "../mask.tif", "C:\\mask.tif", "mask\\name.tif"):
        with pytest.raises(ValueError):
            case.relative_asset(tmp_path, source)
    (tmp_path / "escape").symlink_to(tmp_path.parent)
    with pytest.raises(ValueError, match="escapes"):
        case.relative_asset(tmp_path, "escape/mask.tif")


def test_cli_defaults_are_repo_relative_without_evaluation(monkeypatch, tmp_path):
    captured = []

    def fake_build(dataset, protocol):
        captured.extend((dataset, protocol))
        return {"synthetic_cli_test": True}

    monkeypatch.setattr(case, "build_result", fake_build)
    monkeypatch.setattr(case, "write_result", lambda output, result: captured.append(output))
    assert case.main([]) == 0
    assert captured == [case.ROOT / "data/raw/BBBC039", case.ROOT / "evaluation/model-case/protocol.json",
                        case.ROOT / "evaluation/model-case/result.json"]
    captured.clear()
    assert case.main(["--dataset", str(tmp_path), "--protocol", "synthetic.json", "--output", "result.json"]) == 0
    assert captured == [tmp_path, Path("synthetic.json"), Path("result.json")]
