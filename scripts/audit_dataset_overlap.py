"""Audit same-size pixel overlap across the complete BBBC038 stage1 archive.

This reads raw image pixels and aggregate metadata only. It never opens label
masks or runs segmentation inference. See the dated provenance note for scope.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
BBBC038_ARCHIVE = ROOT / "data/raw/BBBC038-stage1_train.zip"
BBBC039_ARCHIVE = ROOT / "data/raw/BBBC039/images.zip"
METADATA = ROOT / "data/raw/BBBC038-metadata.xlsx"
PROFILE = ROOT / "research/external-assessment/raw-image-profile.json"
FROZEN_SCREEN = ROOT / "research/external-assessment/content-overlap-screen.json"
DEFAULT_OUTPUT = ROOT / "research/external-assessment/overlap-audit-all-stage1-2026-10-11.json"
SAMPLE_THRESHOLD = 0.90
FULL_THRESHOLD = 0.95


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def feature(array: np.ndarray) -> np.ndarray:
    sampled = array.ravel()[np.linspace(0, array.size - 1, 1024, dtype=np.int64)].astype(np.float64)
    sampled -= sampled.mean()
    return sampled / max(float(np.linalg.norm(sampled)), 1e-12)


def orient(array: np.ndarray, variant: int) -> np.ndarray:
    return (
        array
        if variant == 0
        else np.fliplr(array)
        if variant == 1
        else np.flipud(array)
        if variant == 2
        else array[::-1, ::-1]
    )


def read_metadata_groups() -> list[dict[str, object]]:
    namespace = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    tag = "{" + namespace["m"] + "}"

    def column_index(reference: str) -> int:
        letters = "".join(character for character in reference if character.isalpha())
        index = 0
        for character in letters:
            index = index * 26 + ord(character.upper()) - ord("A") + 1
        return index

    with ZipFile(METADATA) as archive:
        strings = [
            "".join(node.text or "" for node in item.iter(tag + "t"))
            for item in ET.fromstring(archive.read("xl/sharedStrings.xml")).findall("m:si", namespace)
        ]
        rows = ET.fromstring(archive.read("xl/worksheets/sheet1.xml")).findall(
            ".//m:sheetData/m:row", namespace
        )
    headers: dict[int, str] = {}
    groups = []
    for index, row in enumerate(rows):
        values: dict[int, str] = {}
        for cell in row.findall("m:c", namespace):
            value_node = cell.find("m:v", namespace)
            value = "" if value_node is None else value_node.text or ""
            if cell.attrib.get("t") == "s" and value:
                value = strings[int(value)]
            values[column_index(cell.attrib["r"])] = value
        if index == 0:
            headers = values
            continue
        record = {headers[column]: value for column, value in values.items() if column in headers}
        if record.get("project_id") == "bbbc022":
            groups.append(
                {
                    "image_set": record.get("image_set"),
                    "num_images": int(float(record.get("num_images") or 0)),
                }
            )
    return groups


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    for path in (BBBC038_ARCHIVE, BBBC039_ARCHIVE, METADATA, PROFILE, FROZEN_SCREEN):
        if not path.is_file():
            raise FileNotFoundError(path)

    profile = json.loads(PROFILE.read_text())
    rows = profile["images"]
    existing_candidates = {
        row["id"] for row in rows if row.get("candidate_property_scope")
    }

    references: dict[str, np.ndarray] = {}
    features: list[np.ndarray] = []
    keys: list[tuple[str, int, tuple[int, ...]]] = []
    with ZipFile(BBBC039_ARCHIVE) as archive:
        for name in sorted(
            item
            for item in archive.namelist()
            if item.startswith("images/")
            and item.endswith(".tif")
            and not Path(item).name.startswith("._")
        ):
            with Image.open(BytesIO(archive.read(name))) as image:
                array = np.asarray(image).copy()
            references[name] = array
            for variant in range(4):
                features.append(feature(orient(array, variant)))
                keys.append((name, variant, array.shape))
    feature_matrix = np.asarray(features)

    matches = []
    with ZipFile(BBBC038_ARCHIVE) as archive:
        for row in rows:
            with Image.open(BytesIO(archive.read(row["image_path"]))) as image:
                array = np.asarray(image).copy()
                if array.ndim == 3:
                    array = array[..., 0]
            correlations = feature_matrix @ feature(array)
            image_matches = []
            for index in np.flatnonzero(correlations >= SAMPLE_THRESHOLD):
                name, variant, shape = keys[int(index)]
                if shape != array.shape:
                    continue
                full_correlation = float(
                    np.corrcoef(
                        array.ravel().astype(np.float64),
                        orient(references[name], variant).ravel().astype(np.float64),
                    )[0, 1]
                )
                if np.isfinite(full_correlation) and full_correlation >= FULL_THRESHOLD:
                    image_matches.append(
                        {
                            "bbbc039_image": name,
                            "orientation": variant,
                            "sample_correlation": float(correlations[index]),
                            "full_correlation": full_correlation,
                        }
                    )
            if image_matches:
                matches.append(
                    {
                        "bbbc038_image_id": row["id"],
                        "in_existing_539_candidates": row["id"] in existing_candidates,
                        "matches": image_matches,
                    }
                )

    old = json.loads(FROZEN_SCREEN.read_text())
    old_matches = {
        row["id"]: row["matches"]
        for row in old["results"]
        if row["potential_same_size_overlap"]
    }
    new_matches = {row["bbbc038_image_id"]: row["matches"] for row in matches}
    same_candidate_set = set(old_matches) == set(new_matches)
    same_reference_map = same_candidate_set and all(
        [item["bbbc039_image"] for item in old_matches[key]]
        == [item["bbbc039_image"] for item in new_matches[key]]
        for key in old_matches
    )

    groups = read_metadata_groups()
    matched_reference_names = [
        item["bbbc039_image"] for row in matches for item in row["matches"]
    ]
    full_correlations = [
        item["full_correlation"] for row in matches for item in row["matches"]
    ]
    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "dataset_file_sha256": {
            "BBBC038_stage1_archive": sha256(BBBC038_ARCHIVE),
            "BBBC039_image_archive": sha256(BBBC039_ARCHIVE),
            "BBBC038_metadata_workbook": sha256(METADATA),
        },
        "scope": (
            "All BBBC038 stage1 raw image arrays against all BBBC039 raw image fields. "
            "No annotation masks, labels, segmentation inference, or metric calculation. "
            "Same-size pixel screen; it does not detect all crops/resampling or establish "
            "biological-source independence."
        ),
        "method": {
            "sample_points": 1024,
            "sample_pearson_threshold": SAMPLE_THRESHOLD,
            "full_image_same_size_pearson_threshold": FULL_THRESHOLD,
            "orientations": ["original", "horizontal flip", "vertical flip", "both flips"],
        },
        "counts": {
            "stage1_images_scanned": len(rows),
            "bbbc039_images_scanned": len(references),
            "pixel_matches": len(matches),
            "matches_from_existing_539_candidates": sum(
                row["in_existing_539_candidates"] for row in matches
            ),
            "unique_bbbc039_fields_matched": len(set(matched_reference_names)),
            "match_records": len(matched_reference_names),
            "full_correlation_min": min(full_correlations, default=None),
            "full_correlation_max": max(full_correlations, default=None),
            "metadata_bbbc022_groups": groups,
            "metadata_bbbc022_training_images": sum(
                item["num_images"] for item in groups if item["image_set"] == "training"
            ),
            "same_candidate_set_as_original_screen": same_candidate_set,
            "same_reference_map_as_original_screen": same_reference_map,
            "one_to_one_candidate_reference_matches": (
                len(matches) == len(set(matched_reference_names)) == len(matched_reference_names)
                and all(len(row["matches"]) == 1 for row in matches)
            ),
        },
        "matches": matches,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps(output["counts"]))


if __name__ == "__main__":
    main()
