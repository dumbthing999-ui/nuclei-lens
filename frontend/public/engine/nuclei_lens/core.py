"""Deterministic image analysis. No dataset annotations or network calls here."""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from hashlib import sha256
from time import perf_counter
from typing import Any

import numpy as np
from scipy import ndimage as ndi
from skimage.feature import peak_local_max
from skimage.filters import threshold_otsu
from skimage.measure import regionprops
from skimage.segmentation import find_boundaries, watershed

from .graph import compare_instances, object_stats

MAX_PIXELS = 1_048_576
MAX_SIDE = 2048
GRID_ROWS = 4
GRID_COLS = 5


@dataclass(frozen=True)
class Config:
    threshold_factor: float = 0.85
    min_distance: int = 7
    smoothing: float = 1.0
    min_area: int = 40
    background_sigma: float = 24.0
    threshold_cap: float = 0.8
    minimum_signal_ratio: float = 6.0

    def validate(self) -> None:
        if not 0.4 <= self.threshold_factor <= 1.5:
            raise ValueError("Threshold factor must be between 0.4 and 1.5.")
        if not 3 <= self.min_distance <= 20:
            raise ValueError("Minimum peak distance must be between 3 and 20 pixels.")
        if not 0.3 <= self.smoothing <= 3.0:
            raise ValueError("Smoothing must be between 0.3 and 3.0 pixels.")
        if not 10 <= self.min_area <= 400:
            raise ValueError("Minimum area must be between 10 and 400 pixels.")
        if not 8.0 <= self.background_sigma <= 60.0:
            raise ValueError("Background scale must be between 8 and 60 pixels.")
        if not 0.3 <= self.threshold_cap <= 1.5 or not 0 <= self.minimum_signal_ratio <= 20:
            raise ValueError("Signal quality parameters are outside supported limits.")


def validate_image(image: np.ndarray) -> None:
    if image.ndim != 2 or min(image.shape) < 32:
        raise ValueError("Use a two-dimensional image at least 32 × 32 pixels.")
    if max(image.shape) > MAX_SIDE or image.size > MAX_PIXELS:
        raise ValueError("Image must be at most 1,048,576 pixels and 2,048 pixels per side.")
    if image.dtype.kind not in "buif" or not np.isfinite(image).all():
        raise ValueError("Image pixels must be finite numbers.")


def normalize(image: np.ndarray) -> np.ndarray:
    validate_image(image)
    low, high = np.percentile(image, (1.0, 99.8))
    if high <= low:
        return np.zeros(image.shape, dtype=np.float32)
    return np.clip((image.astype(np.float32) - low) / (high - low), 0, 1).astype(np.float32)


def segment(image: np.ndarray, config: Config, cap_artifacts: bool = False) -> np.ndarray:
    """Background correction, Otsu foreground, distance peaks, and watershed.

    ``image`` is normalized. This is a transparent classical baseline, not a
    claimed state-of-the-art segmentation method.
    """
    config.validate()
    smooth = ndi.gaussian_filter(image, sigma=config.smoothing)
    corrected = np.maximum(smooth - ndi.gaussian_filter(smooth, config.background_sigma), 0)
    if float(corrected.max()) <= 1e-8:
        return np.zeros(image.shape, dtype=np.int32)
    # Bright artifacts can dominate Otsu's two-class histogram. Cap its threshold
    # against the upper-body signal, preserving the original Otsu value otherwise.
    threshold = float(threshold_otsu(corrected))
    if cap_artifacts:
        threshold = min(threshold, float(np.percentile(corrected, 95)) * config.threshold_cap)
    threshold *= config.threshold_factor
    foreground = ndi.binary_fill_holes(corrected > threshold)
    components, _ = ndi.label(foreground)
    areas = np.bincount(components.ravel())
    keep = areas >= config.min_area
    keep[0] = False
    foreground = keep[components]
    components, n_components = ndi.label(foreground)
    if n_components == 0:
        return np.zeros(image.shape, dtype=np.int32)
    distance = ndi.distance_transform_edt(foreground)
    peaks = peak_local_max(
        distance,
        min_distance=config.min_distance,
        threshold_abs=1.0,
        exclude_border=False,
        labels=components,
    )
    markers = np.zeros(image.shape, dtype=np.int32)
    for marker_id, (row, col) in enumerate(peaks, start=1):
        markers[row, col] = marker_id
    # Always give every surviving connected component a seed, including thin
    # objects and objects at image borders.
    seeded = set(int(x) for x in components[markers > 0])
    next_marker = len(peaks) + 1
    for label_id, slices in enumerate(ndi.find_objects(components), start=1):
        if label_id in seeded or slices is None:
            continue
        local_distance = np.where(components[slices] == label_id, distance[slices], -1)
        row, col = np.unravel_index(int(local_distance.argmax()), local_distance.shape)
        markers[row + slices[0].start, col + slices[1].start] = next_marker
        next_marker += 1
    labels = watershed(-distance, markers, mask=foreground).astype(np.int32)
    areas = np.bincount(labels.ravel())
    keep = areas >= config.min_area
    keep[0] = False
    labels = np.where(keep[labels], labels, 0)
    unique = np.unique(labels)
    # Keep zero as background even when a dense image has no background pixels.
    lookup = np.zeros(int(labels.max()) + 1, dtype=np.int32)
    positive = unique[unique > 0]
    lookup[positive] = np.arange(1, len(positive) + 1)
    return lookup[labels]


def probe_specs(config: Config) -> list[tuple[str, Config, float]]:
    """Predeclared sensitivity probes; no ground-truth-dependent perturbations."""
    return [
        ("baseline", config, 1.0),
        ("lower threshold", replace(config, threshold_factor=max(0.4, config.threshold_factor * 0.88)), 1.0),
        ("higher threshold", replace(config, threshold_factor=min(1.5, config.threshold_factor * 1.12)), 1.0),
        ("closer seeds", replace(config, min_distance=max(3, config.min_distance - 2)), 1.0),
        ("wider seeds", replace(config, min_distance=min(20, config.min_distance + 2)), 1.0),
        ("less smoothing", replace(config, smoothing=max(0.3, config.smoothing * 0.7)), 1.0),
        ("more smoothing", replace(config, smoothing=min(3.0, config.smoothing * 1.3)), 1.0),
        ("brighter midtones", config, 0.85),
        ("darker midtones", config, 1.15),
    ]


def tile_id(x: float, y: float, shape: tuple[int, int]) -> int:
    height, width = shape
    col = min(GRID_COLS - 1, max(0, int(x * GRID_COLS / width)))
    row = min(GRID_ROWS - 1, max(0, int(y * GRID_ROWS / height)))
    return row * GRID_COLS + col


def tile_counts(labels: np.ndarray) -> np.ndarray:
    counts = np.zeros(GRID_ROWS * GRID_COLS, dtype=np.int32)
    stats = object_stats(labels)
    for obj in stats.values():
        counts[tile_id(obj["x"], obj["y"], labels.shape)] += 1
    return counts


def tile_mean(values: np.ndarray) -> np.ndarray:
    height, width = values.shape
    means = []
    for row in range(GRID_ROWS):
        y0, y1 = row * height // GRID_ROWS, (row + 1) * height // GRID_ROWS
        for col in range(GRID_COLS):
            x0, x1 = col * width // GRID_COLS, (col + 1) * width // GRID_COLS
            means.append(float(values[y0:y1, x0:x1].mean()))
    return np.asarray(means)


def analyze(image: np.ndarray, config: Config | None = None) -> dict[str, Any]:
    start = perf_counter()
    config = config or Config()
    config.validate()
    normalized = normalize(image)
    # Robust adjacent-pixel noise estimate. This is a scope/quality heuristic,
    # not a calibrated guarantee that an image contains no nuclei.
    raw = image.astype(np.float32)
    noise = float(np.median(np.abs(np.diff(raw, axis=1))) / (0.67448975 * np.sqrt(2)))
    signal = float(np.percentile(raw, 99) - np.median(raw))
    signal_ratio = signal / max(noise, 1e-8)
    weak_signal = bool(signal <= 0 or signal_ratio < config.minimum_signal_ratio)
    saturated_fraction = float(np.mean(raw == raw.max()))
    artifact_cap = saturated_fraction >= 0.002
    specs = probe_specs(config)
    masks = [np.zeros(image.shape, dtype=np.int32) if weak_signal else
             segment(np.power(normalized, gamma), cfg, cap_artifacts=artifact_cap) for _, cfg, gamma in specs]
    baseline = masks[0]
    height, width = image.shape
    n_tiles = GRID_ROWS * GRID_COLS
    count_matrix = np.stack([tile_counts(mask) for mask in masks])
    graph_scores = np.zeros(n_tiles, dtype=float)
    object_disagreement = np.zeros(n_tiles, dtype=float)
    events: list[dict[str, Any]] = []
    for run_id, alternate in enumerate(masks[1:], start=1):
        comparison = compare_instances(baseline, alternate)
        for event in comparison["events"]:
            index = tile_id(event["x"], event["y"], image.shape)
            graph_scores[index] += event["magnitude"] / (len(masks) - 1)
            events.append({**event, "tile_id": index, "run_id": run_id})
        for obj in comparison["object_disagreement"]:
            index = tile_id(obj["x"], obj["y"], image.shape)
            object_disagreement[index] += obj["score"] / (len(masks) - 1)
    # Boundary disagreement includes instance boundaries, unlike foreground
    # entropy which cannot see watershed split/merge changes in a fixed mask.
    boundary_probability = np.mean(
        [ndi.binary_dilation(find_boundaries(mask, mode="inner"), iterations=1) for mask in masks],
        axis=0,
    )
    boundary_uncertainty = 4 * boundary_probability * (1 - boundary_probability)
    pixel_scores = tile_mean(boundary_uncertainty)
    count_variation = np.std(count_matrix, axis=0)
    shape_scores = np.zeros(n_tiles)
    objects = regionprops(baseline)
    median_area = float(np.median([obj.area for obj in objects])) if objects else 1.0
    for obj in objects:
        relative_area = obj.area / median_area
        score = max(0.0, abs(np.log(max(relative_area, 1e-8))) - 0.5)
        score += max(0.0, obj.eccentricity - 0.75) + max(0.0, 0.9 - obj.solidity)
        shape_scores[tile_id(obj.centroid[1], obj.centroid[0], image.shape)] += score
    regions = []
    for index in range(n_tiles):
        row, col = divmod(index, GRID_COLS)
        bbox = [col * width // GRID_COLS, row * height // GRID_ROWS,
                (col + 1) * width // GRID_COLS, (row + 1) * height // GRID_ROWS]
        local_events = [event for event in events if event["tile_id"] == index]
        kinds = sorted({event["kind"] for event in local_events})
        regions.append({
            "id": index,
            "bbox": bbox,
            "baseline_count": int(count_matrix[0, index]),
            "run_counts": [int(value) for value in count_matrix[:, index]],
            "candidate_counts": sorted({int(value) for value in count_matrix[:, index]}),
            "score": round(float(graph_scores[index]), 6),
            "reasons": kinds,
            "events": sorted(local_events, key=lambda event: -event["magnitude"])[:12],
            "comparators": {
                "pixel_disagreement": float(pixel_scores[index]),
                "object_disagreement": float(object_disagreement[index]),
                "count_variation": float(count_variation[index]),
                "shape_flags": float(shape_scores[index]),
            },
        })
    run_counts = [int(np.max(mask)) for mask in masks]
    input_hash = sha256(
        str(image.shape).encode() + str(image.dtype).encode() + np.ascontiguousarray(image).tobytes()
    ).hexdigest()
    return {
        "schema_version": 1,
        "input_hash": input_hash,
        "width": width,
        "height": height,
        "raw_count": run_counts[0],
        "sensitivity_range": [min(run_counts), max(run_counts)],
        "run_counts": run_counts,
        "run_names": [name for name, _, _ in specs],
        "run_configs": [{**asdict(cfg), "gamma": gamma} for _, cfg, gamma in specs],
        "config": asdict(config),
        "quality": {"signal_to_noise_heuristic": round(signal_ratio, 3), "weak_signal": weak_signal,
                    "saturated_fraction": saturated_fraction, "artifact_threshold_cap": artifact_cap,
                    "warning": "Weak nucleus contrast: automated detections were withheld. Inspect the field manually." if weak_signal else None},
        "grid": {"rows": GRID_ROWS, "cols": GRID_COLS},
        "regions": sorted(regions, key=lambda region: (-region["score"], region["id"])),
        "flagged_regions": sum(region["score"] > 0 for region in regions),
        "analysis_ms": round((perf_counter() - start) * 1000, 2),
        "normalized": normalized,
        "masks": masks,
        "boundary_uncertainty": boundary_uncertainty,
    }
