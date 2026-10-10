"""Diagnostic of three existing training-001 masks, never inference or downloads.

The committed protocol pins inputs and the unchanged official decoder/evaluator.
All predictions are verified before the official annotation is decoded. Results
describe annotation agreement on one previously visible development field only.
"""

from __future__ import annotations

import argparse
import base64
import binascii
import json
import re
import sys
import zlib
from hashlib import sha256
from importlib.metadata import version
from io import BytesIO
from itertools import combinations
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import numpy as np  # noqa: E402
import tifffile  # noqa: E402
from PIL import Image  # noqa: E402

from nuclei_lens import __version__  # noqa: E402
from nuclei_lens.data import ARCHIVES  # noqa: E402
from nuclei_lens.data import Dataset as OfficialDataset  # noqa: E402
from nuclei_lens.evaluate import instance_metrics  # noqa: E402

METHODS = ("classical_baseline", "cellpose_nuclei", "stardist_2d_fluo")
PINNED_SOURCES = tuple(f"src/nuclei_lens/{name}.py" for name in ("data", "evaluate", "core", "graph"))
LIMITATIONS = [
    "One preselected development field; masks and counts were previously observable, not a held-out study.",
    "Annotation agreement is not independent biological truth; annotation quality and thresholds affect results.",
    "Pretrained-model training overlap with BBBC039 is unknown; no generalization or general best-model claim.",
    "Merge/split counts are fixed-IoU correspondence hypotheses, not confirmed biological errors.",
    "Equal counts and pairwise differences do not establish correctness of either partition.",
    "No correctness guarantee, human benefit, clinical benefit, scientific novelty or accuracy superiority.",
]
MAX_PIXELS = 1_048_576
MAX_SIDE = 2048
MAX_ASSET_BYTES = 32 * 1024 * 1024


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode()


def digest(payload: bytes) -> str:
    return sha256(payload).hexdigest()


def _hash(value: Any) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
        raise ValueError("Expected a lowercase SHA-256 digest")
    return value


def check_hash(payload: bytes, expected: Any, description: str) -> str:
    actual = digest(payload)
    if actual != _hash(expected):
        raise ValueError(f"SHA-256 mismatch: {description}")
    return actual


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key")
        result[key] = value
    return result


def _nonfinite(value: str) -> None:
    raise ValueError("Nonfinite JSON number")


def read_json(payload: bytes) -> dict[str, Any]:
    try:
        value = json.loads(payload, object_pairs_hook=_pairs, parse_constant=_nonfinite)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("Malformed JSON") from exc
    if not isinstance(value, dict):
        raise ValueError("Expected a JSON object")
    return value


def relative_asset(root: Path, value: Any) -> Path:
    if (not isinstance(value, str) or not value or "\\" in value or ":" in value
            or Path(value).is_absolute() or ".." in Path(value).parts):
        raise ValueError("Asset paths must be relative to the repository")
    path = (root / value).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError("Asset path escapes repository")
    return path


def asset_bytes(root: Path, source: str, expected: str) -> bytes:
    path = relative_asset(root, source)
    if path.stat().st_size > MAX_ASSET_BYTES:
        raise ValueError("Asset exceeds diagnostic size bound")
    payload = path.read_bytes()
    check_hash(payload, expected, source)
    return payload


def _positive_int(value: Any) -> int:
    if type(value) is not int or value < 1:
        raise ValueError("Expected a positive integer")
    return value


def dimensions(value: Any) -> tuple[int, int]:
    if not isinstance(value, dict):
        raise ValueError("Missing dimensions")
    height, width = _positive_int(value.get("height")), _positive_int(value.get("width"))
    if max(height, width) > MAX_SIDE or height * width > MAX_PIXELS:
        raise ValueError("Dimensions exceed diagnostic bounds")
    return height, width


def validate_labels(labels: np.ndarray, shape: tuple[int, int] | None = None) -> np.ndarray:
    """Reject lossy casts, negatives, empty cases and IDs outside uint32."""
    labels = np.asarray(labels)
    if (labels.ndim != 2 or labels.size == 0 or labels.size > MAX_PIXELS
            or max(labels.shape) > MAX_SIDE or (shape is not None and labels.shape != shape)):
        raise ValueError("Instance mask dimensions are invalid")
    if labels.dtype.kind not in "iu":
        raise ValueError("Instance masks require nonnegative integer uint32-compatible IDs")
    if int(labels.min()) < 0 or int(labels.max()) > np.iinfo(np.uint32).max:
        raise ValueError("Instance IDs must be in the uint32 range")
    if not np.any(labels > 0):
        raise ValueError("Empty foreground cases are unsupported")
    return np.ascontiguousarray(labels, dtype="<u4")


def pixel_hash(labels: np.ndarray) -> str:
    return digest(validate_labels(labels).tobytes())


def dense_labels(labels: np.ndarray) -> np.ndarray:
    """Ascending nonzero IDs become 1..N, preserving background and geometry.

    Searchsorted allocates by pixel/object count, never by the largest raw ID.
    """
    labels = validate_labels(labels)
    ids = np.unique(labels[labels > 0])
    result = np.zeros(labels.shape, dtype=np.uint32)
    foreground = labels > 0
    result[foreground] = np.searchsorted(ids, labels[foreground]).astype(np.uint32) + 1
    return result


def partition_equivalent(left: np.ndarray, right: np.ndarray) -> bool:
    """Partitions agree iff foreground agrees and positive IDs map bijectively."""
    left, right = validate_labels(left), validate_labels(right)
    if left.shape != right.shape:
        raise ValueError("Partition dimensions differ")
    active = left > 0
    if not np.array_equal(active, right > 0):
        return False
    pairs = np.unique(np.column_stack((left[active], right[active])), axis=0)
    return bool(len(pairs) == len(np.unique(pairs[:, 0])) == len(np.unique(pairs[:, 1])))


def pairwise_diagnostics(predictions: dict[str, np.ndarray]) -> list[dict[str, Any]]:
    result = []
    for left_name, right_name in combinations(METHODS, 2):
        left, right = predictions[left_name], predictions[right_name]
        if left.shape != right.shape:
            raise ValueError("Pairwise dimensions differ")
        result.append({
            "methods": [left_name, right_name],
            "foreground_differing_pixels": int(np.count_nonzero((left > 0) != (right > 0))),
            "partition_equivalent": partition_equivalent(left, right),
        })
    return result


def agreement_metrics(prediction: np.ndarray, annotation: np.ndarray) -> dict[str, Any]:
    prediction, annotation = dense_labels(prediction), dense_labels(annotation)
    if prediction.shape != annotation.shape:
        raise ValueError("Prediction and annotation dimensions differ")
    n_prediction, n_annotation = int(prediction.max()), int(annotation.max())
    if max(n_prediction, n_annotation) > 4096 or n_prediction * n_annotation > 1_000_000:
        raise ValueError("Matching work exceeds 4096 objects per mask or 1000000 candidate pairs")
    metrics = instance_metrics(prediction, annotation, iou_threshold=0.5)
    keys = ("predicted_count", "annotation_count", "count_error", "count_absolute_error",
            "tp", "fp", "fn", "f1")
    return {
        **{key: metrics[key] for key in keys},
        "precision": metrics["tp"] / metrics["predicted_count"],
        "recall": metrics["tp"] / metrics["annotation_count"],
        "hypothetical_merge_objects": metrics["merge_objects"],
        "hypothetical_split_objects": metrics["split_objects"],
    }


def load_baseline(payload: bytes, shape: tuple[int, int]) -> tuple[np.ndarray, dict[str, Any]]:
    sample = read_json(payload)
    if dimensions(sample) != shape or sample.get("schema_version") != 1:
        raise ValueError("Classical sample dimensions/schema mismatch")
    maps = sample.get("label_maps")
    if not isinstance(maps, dict) or maps.get("encoding") != "zlib-base64-uint32-le":
        raise ValueError("Unsupported classical label encoding")
    runs = maps.get("runs")
    if not isinstance(runs, list) or not runs or not isinstance(runs[0], str):
        raise ValueError("Missing classical baseline run0")
    try:
        compressed = base64.b64decode(runs[0], validate=True)
        decoder = zlib.decompressobj()
        expected = shape[0] * shape[1] * 4
        raw = decoder.decompress(compressed, expected + 1)
        if len(raw) != expected or not decoder.eof or decoder.unused_data or decoder.unconsumed_tail:
            raise ValueError("Classical baseline byte length/compression mismatch")
    except (binascii.Error, zlib.error) as exc:
        raise ValueError("Malformed compressed classical baseline") from exc
    labels = validate_labels(np.frombuffer(raw, dtype="<u4").reshape(shape), shape)
    count = int(np.count_nonzero(np.unique(labels)))
    counts = sample.get("run_counts")
    if (not isinstance(counts, list) or not counts or type(counts[0]) is not int
            or type(sample.get("raw_count")) is not int or counts[0] != count or sample["raw_count"] != count):
        raise ValueError("Classical baseline instance count mismatch")
    return labels, sample


def load_mask_tiff(payload: bytes, shape: tuple[int, int]) -> np.ndarray:
    try:
        with tifffile.TiffFile(BytesIO(payload)) as image:
            if len(image.pages) != 1:
                raise ValueError("Mask TIFF must contain exactly one page")
            page = image.pages[0]
            if page.shape != shape or page.dtype.kind != "u" or page.dtype.itemsize != 4:
                raise ValueError("Mask TIFF must be a matching two-dimensional uint32 raster")
            return validate_labels(page.asarray(), shape)
    except (tifffile.TiffFileError, OSError) as exc:
        raise ValueError("Malformed mask TIFF") from exc


def _public_value(value: Any) -> Any:
    """Only safe structured model/configuration metadata may reach public output."""
    if isinstance(value, str):
        if value.startswith(("/", "~")) or "\\" in value or re.match(r"^[A-Za-z]:", value):
            raise ValueError("Private path in provenance")
    elif isinstance(value, dict):
        return {key: _public_value(item) for key, item in value.items()}
    elif isinstance(value, list):
        return [_public_value(item) for item in value]
    elif value is not None and type(value) not in (int, float, bool):
        raise ValueError("Unsupported provenance value")
    # Also rejects infinity/NaN produced by finite-looking JSON exponents.
    json.dumps(value, allow_nan=False)
    return value


def model_metadata(model: dict[str, Any]) -> dict[str, Any]:
    worker = model.get("worker_provenance")
    if not isinstance(worker, dict):
        raise ValueError("Missing worker provenance")
    for name in ("framework", "framework_version"):
        if not isinstance(worker.get(name), str) or not worker[name]:
            raise ValueError("Missing known model framework/version")
    weights = worker.get("weight_files")
    if not isinstance(weights, list) or not weights:
        raise ValueError("Missing recorded weight provenance")
    public_weights = []
    for weight in weights:
        name = weight["file"]
        if not isinstance(name, str) or Path(name).name != name or name in ("", ".", ".."):
            raise ValueError("Weight provenance must use basenames")
        public_weights.append({"file": _public_value(name), "sha256": _hash(weight["sha256"]),
                               "bytes": _positive_int(weight["bytes"])})
    fields = ("framework", "framework_version", "torch_version", "tensorflow_version", "parameters",
              "model_type", "pretrained_model", "diameter_estimated", "device")
    return {**{name: _public_value(worker[name]) for name in fields if name in worker},
            "weight_files": public_weights,
            "weight_verification": "Recorded provenance only; no weights loaded, downloaded or rehashed"}


def validate_protocol(protocol: dict[str, Any], root: Path) -> tuple[int, int]:
    if (protocol.get("protocol_id") != "nucleilens-existing-training001-annotation-case-v1"
            or protocol.get("sample_id") != "training-001" or protocol.get("split") != "training"
            or type(protocol.get("manifest_position_one_based")) is not int
            or protocol["manifest_position_one_based"] != 1):
        raise ValueError("Only the existing first training-001 development case is supported")
    filename = protocol.get("filename")
    if not isinstance(filename, str) or Path(filename).name != filename or not filename.endswith(".png"):
        raise ValueError("Invalid official annotation filename")
    if not isinstance(protocol.get("declared_at"), str) or not protocol["declared_at"]:
        raise ValueError("Protocol must declare its time")
    matching = protocol.get("matching", {})
    if (type(matching.get("iou_threshold")) not in (int, float) or matching["iou_threshold"] != 0.5
            or type(matching.get("merge_split_hypothesis_iou_threshold")) not in (int, float)
            or matching["merge_split_hypothesis_iou_threshold"] != 0.1):
        raise ValueError("Only fixed IoU thresholds 0.5 and 0.1 are supported")
    if protocol.get("archive_sha256") != ARCHIVES:
        raise ValueError("Protocol archive hashes differ from pinned official Dataset hashes")
    sources = protocol.get("source_sha256")
    if not isinstance(sources, dict) or not set(PINNED_SOURCES).issubset(sources):
        raise ValueError("Protocol must pin the official decoder and frozen evaluator dependencies")
    for path, expected in sources.items():
        asset_bytes(root, path, expected)
    methods = protocol.get("methods")
    if not isinstance(methods, list) or [m.get("id") for m in methods] != list(METHODS):
        raise ValueError("Protocol methods must be exactly the three existing methods in fixed order")
    if type(methods[0].get("run_index")) is not int or methods[0]["run_index"] != 0:
        raise ValueError("Only classical baseline run0 is supported")
    relative_asset(root, protocol.get("output_path"))
    return dimensions(protocol.get("dimensions"))


def build_result(dataset_root: Path, protocol_path: Path, *, root: Path = ROOT) -> dict[str, Any]:
    """Compute only the declared case; caller controls when to execute this function."""
    try:
        return _build_result(Path(dataset_root), Path(protocol_path), Path(root))
    except (KeyError, TypeError, IndexError, AttributeError) as exc:
        raise ValueError("Malformed diagnostic protocol or provenance") from exc


def _build_result(dataset_root: Path, protocol_path: Path, root: Path) -> dict[str, Any]:
    protocol_bytes = protocol_path.read_bytes()
    protocol = read_json(protocol_bytes)
    shape = validate_protocol(protocol, root)
    provenance_bytes = asset_bytes(root, protocol["model_provenance_source"], protocol["model_provenance_sha256"])
    provenance = read_json(provenance_bytes)
    if provenance.get("run_status") != "completed" or set(provenance.get("models", {})) != set(METHODS[1:]):
        raise ValueError("Model provenance does not describe the two completed existing masks")
    image_bytes = asset_bytes(root, protocol["image_source"], protocol["image_file_sha256"])
    with Image.open(BytesIO(image_bytes)) as image_file:
        if image_file.format != "TIFF" or image_file.size != (shape[1], shape[0]) or image_file.n_frames != 1:
            raise ValueError("Image must be the matching single-page TIFF")
        image = np.asarray(image_file).copy()
    image_provenance = provenance["input_image"]
    if (image.shape != shape or image.dtype.kind not in "iu" or dimensions(image_provenance["dimensions"]) != shape
            or image_provenance["dtype"] != str(image.dtype) or image_provenance["pixel_count"] != image.size):
        raise ValueError("Image dimensions/dtype mismatch with model provenance")
    image_raw = np.ascontiguousarray(image).tobytes()
    check_hash(image_bytes, image_provenance["file_sha256"], "model input file")
    check_hash(image_raw, protocol["image_pixel_sha256"], "protocol input pixels")
    check_hash(image_raw, image_provenance["pixel_sha256"], "model input pixels")
    input_hash = digest(str(image.shape).encode() + str(image.dtype).encode() + image_raw)
    if _hash(provenance["nucleilens_input_hash"]) != input_hash:
        raise ValueError("NucleiLens input hash differs from model provenance")

    predictions, mask_records = {}, {}
    for method in protocol["methods"]:
        name = method["id"]
        payload = asset_bytes(root, method["source"], method["sha256"])
        if name == "classical_baseline":
            labels, sample = load_baseline(payload, shape)
            if _hash(sample["input_hash"]) != input_hash:
                raise ValueError("Classical sample input hash mismatch")
            metadata = {"software_version": _public_value(sample["software_version"]),
                        "config": _public_value(sample["config"]), "run_index": 0}
            if "run_configs" in sample:
                metadata["run_config"] = _public_value(sample["run_configs"][0])
        else:
            labels = load_mask_tiff(payload, shape)
            model = provenance["models"][name]
            if model.get("status") != "success" or model.get("mask_tiff_path") != Path(method["source"]).name:
                raise ValueError("Model mask status/source mismatch")
            check_hash(payload, model["mask_file_sha256"], name + " provenance file")
            check_hash(labels.tobytes(), method["pixel_sha256"], name + " protocol pixels")
            check_hash(labels.tobytes(), model["mask_pixel_sha256"], name + " provenance pixels")
            count = int(np.count_nonzero(np.unique(labels)))
            if (_positive_int(model["instance_count"]) != count
                    or _positive_int(method["known_instance_count"]) != count):
                raise ValueError("Model instance count mismatch")
            metadata = model_metadata(model)
        if "pixel_sha256" in method:
            check_hash(labels.tobytes(), method["pixel_sha256"], name + " pixels")
        predictions[name] = labels
        mask_records[name] = {"source": method["source"], "file_sha256": digest(payload),
                              "pixel_sha256": pixel_hash(labels), "dtype": "uint32",
                              "dimensions": protocol["dimensions"],
                              "instance_count": int(np.count_nonzero(np.unique(labels))),
                              "provenance": metadata}

    # All three arrays, file/pixel hashes, counts and model provenance verified.
    # Dataset construction verifies the pinned archives; no inference occurs.
    with OfficialDataset(dataset_root) as dataset:
        if not dataset.filenames("training") or dataset.filenames("training")[0] != protocol["filename"]:
            raise ValueError("Protocol filename is not the first official training field")
        official_image_bytes = dataset.image_bytes(protocol["filename"])
        if official_image_bytes != image_bytes:
            raise ValueError("Official dataset image bytes differ from existing model input")
        official_image = dataset.image(protocol["filename"])
        if official_image.dtype != image.dtype or not np.array_equal(official_image, image):
            raise ValueError("Official image pixels/dtype differ from model input")
        # The only annotation decoding call; strictly after prediction loading.
        annotation = validate_labels(dataset.annotations(protocol["filename"]), shape)
        annotation_bytes = dataset.masks.read("masks/" + protocol["filename"])

    return {
        "schema_version": 1,
        "protocol": {"id": protocol["protocol_id"], "sha256": digest(protocol_bytes),
                     "declared_at": _public_value(protocol["declared_at"])},
        "case": {"sample_id": "training-001", "split": "training", "filename": protocol["filename"],
                 "dimensions": protocol["dimensions"], "inference_performed": False},
        "source_sha256": protocol["source_sha256"],
        "archive_sha256": protocol["archive_sha256"],
        "image": {"source": protocol["image_source"], "file_sha256": digest(image_bytes),
                  "pixel_sha256": digest(image_raw), "dtype": str(image.dtype), "input_hash": input_hash},
        "model_provenance": {"source": protocol["model_provenance_source"],
                             "sha256": digest(provenance_bytes)},
        "annotation": {"decoder": "OfficialDataset.annotations: first-channel equal-value 8-connectivity",
                       "source": "masks.zip:masks/" + protocol["filename"],
                       "file_sha256": digest(annotation_bytes), "pixel_sha256": pixel_hash(annotation),
                       "pixel_hash_encoding": "uint32-le before dense ID remapping",
                       "instance_count": int(np.count_nonzero(np.unique(annotation)))},
        "matching": {"iou_threshold": 0.5, "merge_split_hypothesis_iou_threshold": 0.1,
                     "dense_label_remapping": "Ascending positive IDs to 1..N; background stays 0",
                     "evaluator": "nuclei_lens.evaluate.instance_metrics (unchanged)"},
        "methods": {name: {**mask_records[name], "metrics": agreement_metrics(predictions[name], annotation)}
                    for name in METHODS},
        "pairwise": pairwise_diagnostics(predictions),
        "versions": {"nuclei_lens": __version__, **{name: version(name) for name in
                     ("numpy", "scipy", "scikit-image", "pillow", "tifffile")}},
        "limitations": LIMITATIONS,
    }


def write_result(output: Path, result: dict[str, Any]) -> None:
    """Exclusive creation; an existing byte-identical result is a harmless no-op."""
    payload = canonical_json(result)
    output = Path(output)
    if output.is_symlink():
        raise ValueError("Refusing output symlink")
    if output.exists():
        if output.read_bytes() != payload:
            raise ValueError("Refusing to overwrite differing output")
        return
    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        with output.open("xb") as stream:
            stream.write(payload)
    except FileExistsError:
        if output.is_symlink() or output.read_bytes() != payload:
            raise ValueError("Refusing to overwrite differing output") from None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=ROOT / "data/raw/BBBC039")
    parser.add_argument("--protocol", type=Path, default=ROOT / "evaluation/model-case/protocol.json")
    parser.add_argument("--output", type=Path, default=ROOT / "evaluation/model-case/result.json")
    args = parser.parse_args(argv)
    try:
        write_result(args.output, build_result(args.dataset, args.protocol))
    except (ValueError, OSError) as exc:
        # File-system exceptions can contain private absolute paths. CLI output
        # stays generic; validation messages use public relative asset names.
        print(str(exc) if isinstance(exc, ValueError) else "Required local input/output unavailable", file=sys.stderr)
        return 1
    print("OK: deterministic single development-case annotation diagnostic saved")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
