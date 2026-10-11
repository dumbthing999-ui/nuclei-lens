"""Run corrected-v2 frozen BBBC007 external-data evaluation; v1 retained separately."""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

import numpy as np
import tifffile
from scipy import ndimage as ndi

from nuclei_lens.core import Config
from nuclei_lens.evaluate import evaluate_partition

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "evaluation/independent/bbbc007-v2"
PROTOCOL = OUT / "frozen-protocol.json"
IMAGES = ROOT / "data/raw/BBBC007_v1_images.zip"
OUTLINES = ROOT / "data/raw/BBBC007_v1_outlines.zip"
SOURCE_FILES = (
    "src/nuclei_lens/core.py",
    "src/nuclei_lens/graph.py",
    "src/nuclei_lens/evaluate.py",
    "evaluation/frozen/protocol.json",
    "scripts/evaluate_bbbc007_v2.py",
)
IMAGE_ROOT = "BBBC007_v1_images/"
OUTLINE_ROOT = "BBBC007_v1_outlines/"
DNA_SUFFIX = "_D_1UL.tif"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def binary_outline_to_instances(outline: np.ndarray) -> tuple[np.ndarray, int]:
    """Fill manually drawn closed contours; leave contour pixels out of objects."""
    values = np.asarray(outline)
    if values.ndim != 2 or values.dtype.kind not in "buif":
        raise ValueError("Reference outlines must be a two-dimensional numeric raster")
    if not np.isfinite(values).all():
        raise ValueError("Reference outline contains non-finite pixels")
    foreground = values > 0
    if not np.any(foreground):
        raise ValueError("Reference outline is empty")
    inside = ndi.binary_fill_holes(foreground) & ~foreground
    instances, count = ndi.label(inside, structure=ndi.generate_binary_structure(2, 1))
    if count == 0:
        raise ValueError("No closed outline interiors could be reconstructed")
    return instances.astype(np.int32, copy=False), int(count)


def image_to_grayscale(image: np.ndarray) -> np.ndarray:
    """Use the browser's RGB luminance conversion for multichannel TIFF samples."""
    values = np.asarray(image)
    if values.dtype != np.uint8 or not np.isfinite(values).all():
        raise ValueError("BBBC007 input must be finite uint8 image data")
    if values.ndim == 2:
        gray = values
    elif values.ndim == 3 and values.shape[2] in (3, 4):
        rgb = values[..., :3].astype(np.float32)
        gray = np.rint(0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2])
        gray = np.clip(gray, 0, 255).astype(np.uint8)
    else:
        raise ValueError("Expected a grayscale, RGB, or RGBA image")
    if min(gray.shape) < 32 or gray.size > 1_048_576:
        raise ValueError("Image dimensions fall outside the frozen engine bounds")
    return np.ascontiguousarray(gray)


def candidate_pairs(image_names: list[str], outline_names: list[str]) -> list[dict[str, str]]:
    """Select every explicit DNA-channel filename with a matching outline."""
    by_relative = {
        name.removeprefix(OUTLINE_ROOT): name
        for name in outline_names
        if name.startswith(OUTLINE_ROOT) and name.endswith(".tif")
    }
    rows = []
    for name in sorted(image_names):
        if not name.startswith(IMAGE_ROOT) or not name.endswith(DNA_SUFFIX):
            continue
        relative = name.removeprefix(IMAGE_ROOT)
        outline_name = by_relative.get(relative)
        if outline_name is None:
            raise ValueError(f"Selected DNA image has no same-path outline: {relative}")
        rows.append({"image_path": name, "outline_path": outline_name})
    if not rows:
        raise ValueError("No explicitly marked DNA-channel image/outline pairs found")
    return rows


def freeze() -> None:
    if PROTOCOL.exists():
        raise ValueError("Protocol already frozen; do not overwrite or tune against results")
    for path in (IMAGES, OUTLINES):
        if not path.is_file():
            raise FileNotFoundError(f"Place the official archive at {path}")
    with ZipFile(IMAGES) as image_zip, ZipFile(OUTLINES) as outline_zip:
        pairs = candidate_pairs(image_zip.namelist(), outline_zip.namelist())
        image_info = {item.filename: item.file_size for item in image_zip.infolist()}
        outline_info = {item.filename: item.file_size for item in outline_zip.infolist()}
        manifest = []
        for pair in pairs:
            image_bytes = image_zip.read(pair["image_path"])
            outline_bytes = outline_zip.read(pair["outline_path"])
            manifest.append({
                **pair,
                "image_sha256": sha256_bytes(image_bytes),
                "outline_sha256": sha256_bytes(outline_bytes),
                "image_archive_bytes": image_info[pair["image_path"]],
                "outline_archive_bytes": outline_info[pair["outline_path"]],
            })
    original = json.loads((ROOT / "evaluation/frozen/protocol.json").read_text())
    protocol = {
        "frozen_at": datetime.now(timezone.utc).isoformat(),
        "dataset": "BBBC007v1 Drosophila Kc167 fluorescence images; exploratory external-data evaluation, not an official test split",
        "source_record": "https://bbbc.broadinstitute.org/BBBC007",
        "license": "CC0 waiver stated by the official BBBC record",
        "recommended_citation": "Jones et al., CVBIA 2005; BBBC007v1 via Ljosa et al., Nature Methods 2012",
        "archives": {
            "BBBC007_v1_images.zip": sha256_file(IMAGES),
            "BBBC007_v1_outlines.zip": sha256_file(OUTLINES),
        },
        "source_sha256": {name: sha256_file(ROOT / name) for name in SOURCE_FILES},
        "inference_config": original["config"],
        "selection": "Every archive member under BBBC007_v1_images whose relative filename ends exactly in _D_1UL.tif and has a same-relative-path member in BBBC007_v1_outlines. This selects explicitly marked DNA-channel fields and excludes actin (_F_2UL) and legacy filenames without channel markers. No image-content or result-based sampling.",
        "n_selected": len(manifest),
        "images": manifest,
        "rgb_conversion": "For RGB/RGBA images use the browser luminance equation round(0.299 R + 0.587 G + 0.114 B); grayscale uint8 is unchanged. No learned color deconvolution or per-image tuning.",
        "reference_conversion": "Treat nonzero pixels as the manually drawn outline. Fill enclosed holes, remove contour pixels, and label interior components with 4-connectivity. No contour repair, manual correction, or threshold tuning. Any conversion failure remains a failed manifest row.",
        "primary_metrics": ["count MAE", "macro instance F1 at IoU >= 0.5", "object-disagreement error-mass capture at 4 of 20 fixed centroid tiles"],
        "comparators": "Keep the six existing evaluation comparators and tie handling unchanged; report only the preselected object-disagreement queue as the primary queue result.",
        "failures": "Retain all selected fields; no post-result exclusions. Report conversion/inference errors separately.",
        "independence_limit": "BBBC007 is a different Drosophila Kc167 assay from BBBC039 U2OS chemical-screen images, but this small subset does not establish laboratory independence, broad biological generalization, or human benefit.",
        "feasibility_note": "Before protocol freeze, one _D_1UL outline was inspected for raster format/closed-loop feasibility. No model inference or benchmark outcome was computed during that feasibility check.",
    }
    OUT.mkdir(parents=True, exist_ok=True)
    PROTOCOL.write_text(json.dumps(protocol, indent=2) + "\n")
    print(f"Frozen protocol with {len(manifest)} path-selected fields; no inference run.")


class BBBC007Field:
    def __init__(self, image_zip: ZipFile, outline_zip: ZipFile, row: dict[str, str]):
        self.image_zip = image_zip
        self.outline_zip = outline_zip
        self.row = row
        self.image_shape: tuple[int, int] | None = None

    def filenames(self, split: str) -> list[str]:
        if split != "bbbc007-external":
            raise ValueError("Unexpected dataset split")
        return [self.row["image_path"]]

    def image(self, filename: str) -> np.ndarray:
        if filename != self.row["image_path"]:
            raise ValueError("Image is outside the frozen manifest")
        payload = self.image_zip.read(filename)
        if sha256_bytes(payload) != self.row["image_sha256"]:
            raise ValueError("Image bytes differ from the frozen manifest")
        image = image_to_grayscale(tifffile.imread(BytesIO(payload)))
        self.image_shape = image.shape
        return image

    def annotations(self, filename: str) -> np.ndarray:
        if filename != self.row["image_path"]:
            raise ValueError("Annotation is outside the frozen manifest")
        payload = self.outline_zip.read(self.row["outline_path"])
        if sha256_bytes(payload) != self.row["outline_sha256"]:
            raise ValueError("Outline bytes differ from the frozen manifest")
        reference = tifffile.imread(BytesIO(payload))
        if reference.ndim != 2:
            raise ValueError("Reference outline must be a single-channel raster")
        labels, _ = binary_outline_to_instances(reference)
        if self.image_shape is None:
            raise ValueError("Image must be loaded before its outline")
        if labels.shape != self.image_shape:
            raise ValueError("Image and converted outline dimensions differ")
        return labels


def run() -> None:
    protocol = json.loads(PROTOCOL.read_text())
    for name, expected in protocol["source_sha256"].items():
        if sha256_file(ROOT / name) != expected:
            raise ValueError(f"Frozen source changed: {name}")
    for path in (IMAGES, OUTLINES):
        if sha256_file(path) != protocol["archives"][path.name]:
            raise ValueError(f"Dataset archive changed: {path.name}")
    protocol_hash = sha256_file(PROTOCOL)
    config = Config(**protocol["inference_config"])
    records = []
    with ZipFile(IMAGES) as image_zip, ZipFile(OUTLINES) as outline_zip:
        for index, row in enumerate(protocol["images"], start=1):
            try:
                field = BBBC007Field(image_zip, outline_zip, row)
                _, record_list = evaluate_partition(field, "bbbc007-external", config)
                record = record_list[0]
                record.pop("oracle_count_error_curves", None)
                record.update(status="evaluated", protocol_sha256=protocol_hash)
            except Exception as error:
                record = {
                    "filename": row["image_path"],
                    "status": "failed",
                    "protocol_sha256": protocol_hash,
                    "error": f"{type(error).__name__}: {error}",
                }
            records.append(record)
            print(f"BBBC007 {index}/{len(protocol['images'])}: {row['image_path']} {record['status']}", flush=True)
    valid = [record for record in records if record["status"] == "evaluated"]
    error_mass = sum(record["error_mass"] for record in valid)
    capture = {}
    methods = list(valid[0]["capture_curves"]) if valid else []
    for method in methods:
        numerator = sum(record["capture_curves"][method][4] for record in valid)
        capture[method] = numerator / error_mass if error_mass else None
    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "dataset": protocol["dataset"],
        "protocol_sha256": protocol_hash,
        "selected_fields": len(protocol["images"]),
        "evaluated_fields": len(valid),
        "failed_fields": len(records) - len(valid),
        "complete_manifest_retained": len(records) == len(protocol["images"]),
        "count_mae": float(np.mean([record["count_absolute_error"] for record in valid])) if valid else None,
        "macro_instance_f1_iou_0_5": float(np.mean([record["f1"] for record in valid])) if valid else None,
        "total_fp_plus_fn": int(error_mass),
        "error_mass_capture_at_4_of_20_tiles": capture,
        "aggregation_note": "Sum captured error mass across fields, then divide by total error mass; each per-image capture value is already an absolute error-mass amount.",
        "median_analysis_ms": float(np.median([record["analysis_ms"] for record in valid])) if valid else None,
        "failures": [record for record in records if record["status"] == "failed"],
        "limitations": [
            protocol["independence_limit"],
            protocol["reference_conversion"],
            "Small, incomplete channel-marked subset; not a probability sample or held-out official challenge partition.",
            "Results evaluate a classical intensity-based workflow against reconstructed manual outline interiors, not a claim of model superiority or reader benefit.",
        ],
    }
    (OUT / "per-image.json").write_text(json.dumps(records, indent=2) + "\n")
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({key: summary[key] for key in ("selected_fields", "evaluated_fields", "failed_fields", "count_mae", "macro_instance_f1_iou_0_5", "total_fp_plus_fn")}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze", action="store_true", help="Create protocol; do not infer")
    parser.add_argument("--run", action="store_true", help="Run exactly the frozen protocol")
    args = parser.parse_args()
    if args.freeze == args.run:
        parser.error("Choose exactly one of --freeze or --run")
    freeze() if args.freeze else run()
