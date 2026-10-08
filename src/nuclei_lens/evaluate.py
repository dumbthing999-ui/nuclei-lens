"""Equal-budget review comparison. Run inference before loading annotations."""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any

import numpy as np
from scipy.optimize import linear_sum_assignment

from .core import Config, analyze, tile_counts, tile_id
from .data import ARCHIVES, Dataset
from .graph import object_stats, overlaps

METHODS = ["graph", "pixel_disagreement", "object_disagreement", "count_variation", "shape_flags", "random"]


def instance_metrics(prediction: np.ndarray, truth: np.ndarray, iou_threshold: float = 0.5) -> dict[str, Any]:
    p_stats, t_stats = object_stats(prediction), object_stats(truth)
    p_ids, t_ids, intersections = overlaps(prediction, truth)
    n_p, n_t = int(prediction.max()), int(truth.max())
    iou = np.zeros((n_p, n_t), dtype=float)
    for p_id, t_id, intersection in zip(p_ids, t_ids, intersections, strict=True):
        union = p_stats[int(p_id)]["area"] + t_stats[int(t_id)]["area"] - intersection
        iou[p_id - 1, t_id - 1] = intersection / union
    # Cardinality-first objective: eligible match count dominates total IoU.
    reward = (iou >= iou_threshold).astype(float) + iou / (min(n_p, n_t) + 1)
    matched_p, matched_t = linear_sum_assignment(reward, maximize=True)
    eligible = iou[matched_p, matched_t] >= iou_threshold
    matched_p, matched_t = matched_p[eligible] + 1, matched_t[eligible] + 1
    unmatched_p = set(p_stats) - set(int(x) for x in matched_p)
    unmatched_t = set(t_stats) - set(int(x) for x in matched_t)
    losses = np.zeros(20, dtype=float)
    for label_id in unmatched_p:
        obj = p_stats[label_id]
        losses[tile_id(obj["x"], obj["y"], prediction.shape)] += 1
    for label_id in unmatched_t:
        obj = t_stats[label_id]
        losses[tile_id(obj["x"], obj["y"], prediction.shape)] += 1
    tp = len(matched_p)
    return {
        "predicted_count": n_p,
        "annotation_count": n_t,
        "count_error": n_p - n_t,
        "count_absolute_error": abs(n_p - n_t),
        "tp": tp,
        "fp": n_p - tp,
        "fn": n_t - tp,
        "f1": 2 * tp / (n_p + n_t) if n_p + n_t else 1.0,
        "merge_objects": int(np.sum(np.sum(iou >= 0.1, axis=1) > 1)),
        "split_objects": int(np.sum(np.sum(iou >= 0.1, axis=0) > 1)),
        "tile_error_mass": losses,
        "tile_count_difference": tile_counts(prediction) - tile_counts(truth),
    }


def review_capture(scores: np.ndarray, losses: np.ndarray, k: int) -> float:
    """Expected loss captured, averaging ties rather than cherry-picking order."""
    if not 0 <= k <= len(scores):
        raise ValueError("Review budget is outside the available tile count.")
    order = np.argsort(-scores, kind="stable")
    captured, remaining, index = 0.0, k, 0
    while remaining and index < len(order):
        end = index + 1
        while end < len(order) and np.isclose(scores[order[end]], scores[order[index]], rtol=0, atol=1e-12):
            end += 1
        group = order[index:end]
        take = min(remaining, len(group))
        captured += float(losses[group].sum()) * take / len(group)
        remaining -= take
        index = end
    return captured


def evaluate_partition(
    dataset: Dataset, split: str, config: Config, limit: int | None = None
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    names = dataset.filenames(split)
    if limit is not None:
        names = names[:limit]
    records = []
    for index, filename in enumerate(names):
        result = analyze(dataset.image(filename), config)
        # Labels are read only after inference has returned.
        truth = dataset.annotations(filename)
        metrics = instance_metrics(result["masks"][0], truth)
        losses = metrics.pop("tile_error_mass")
        count_difference = metrics.pop("tile_count_difference")
        regions = sorted(result["regions"], key=lambda region: region["id"])
        curves = {}
        local_count_curves = {}
        oracle_count_curves = {}
        for method in METHODS:
            scores = np.asarray([
                region["score"] if method == "graph" else
                0 if method == "random" else region["comparators"][method]
                for region in regions
            ])
            curves[method] = [review_capture(scores, losses, k) for k in range(21)]
            local_count_curves[method] = [review_capture(scores, np.abs(count_difference), k) for k in range(21)]
            # This secondary simulation uses deterministic seeded tie-breaking.
            # It can initially INCREASE field-level count error when one member
            # of a compensating split/merge pair is corrected first.
            rng = np.random.default_rng(17 + index)
            tie_order = rng.permutation(20)
            order = tie_order[np.argsort(-scores[tie_order], kind="stable")]
            correction = np.concatenate(([0], np.cumsum(count_difference[order])))
            oracle_count_curves[method] = np.abs(metrics["count_error"] - correction).tolist()
        records.append({
            "filename": filename,
            **metrics,
            "analysis_ms": result["analysis_ms"],
            "flagged_regions": result["flagged_regions"],
            "error_mass": float(losses.sum()),
            "tile_error_mass": losses.tolist(),
            "local_count_error_mass": float(np.abs(count_difference).sum()),
            "tile_count_difference": count_difference.tolist(),
            "capture_curves": curves,
            "local_count_capture_curves": local_count_curves,
            "region_scores": [{"graph": region["score"], **region["comparators"]} for region in regions],
            "oracle_count_error_curves": oracle_count_curves,
        })
        print(f"{split} {index + 1}/{len(names)}: count {metrics['predicted_count']}, "
              f"reference {metrics['annotation_count']}, F1 {metrics['f1']:.3f}, "
              f"{result['analysis_ms']:.0f} ms", flush=True)
    if not records:
        raise ValueError("Partition evaluation requires at least one image.")
    total_loss = sum(record["error_mass"] for record in records)
    local_count_loss = sum(record["local_count_error_mass"] for record in records)
    rng = np.random.default_rng(20261008)
    bootstrap = rng.integers(0, len(records), size=(2000, len(records)))
    denominators = np.asarray([record["error_mass"] for record in records])
    boot_denominators = denominators[bootstrap].sum(axis=1)
    summary_methods = {}
    for method in METHODS:
        captures = np.asarray([record["capture_curves"][method] for record in records])
        curves = captures.sum(axis=0) / total_loss if total_loss else np.zeros(21)
        fixed_capture = captures[:, 4]
        boot_values = np.divide(
            fixed_capture[bootstrap].sum(axis=1), boot_denominators,
            out=np.zeros(2000), where=boot_denominators > 0,
        )
        summary_methods[method] = {
            "capture_at_20_percent": float(curves[4]),
            "capture_ci95": [float(x) for x in np.percentile(boot_values, [2.5, 97.5])],
            "review_curve": curves.tolist(),
            "local_count_capture_at_20_percent": float(sum(record["local_count_capture_curves"][method][4] for record in records) / local_count_loss) if local_count_loss else 0,
            "local_count_review_curve": (np.sum([record["local_count_capture_curves"][method] for record in records], axis=0) / local_count_loss).tolist() if local_count_loss else [0.0] * 21,
            "oracle_count_mae_curve": np.mean([record["oracle_count_error_curves"][method] for record in records], axis=0).tolist(),
        }
    graph = np.asarray([record["capture_curves"]["graph"][4] for record in records])
    paired_differences = {}
    for method in METHODS[1:]:
        other = np.asarray([record["capture_curves"][method][4] for record in records])
        delta = graph - other
        boot_delta = np.divide(delta[bootstrap].sum(axis=1), boot_denominators,
                               out=np.zeros(2000), where=boot_denominators > 0)
        paired_differences[method] = {
            "difference": float(delta.sum() / total_loss) if total_loss else 0,
            "ci95": [float(x) for x in np.percentile(boot_delta, [2.5, 97.5])],
        }
    summary = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "split": split,
        "n_images": len(records),
        "partial_partition": len(records) != len(dataset.filenames(split)),
        "config": asdict(config),
        "source_sha256": {name: sha256((Path(__file__).parent / name).read_bytes()).hexdigest()
                          for name in ["core.py", "graph.py", "evaluate.py"]},
        "archive_sha256": ARCHIVES,
        "iou_threshold": 0.5,
        "review_units": "20 fixed nonoverlapping image-grid tiles; counts assigned by object centroid",
        "primary_loss": "FP + FN from cardinality-first IoU>=0.5 matching",
        "secondary_loss": "Sum of absolute tile count differences; added after initial validation to assess count-specific behavior, not replace the primary metric",
        "tie_policy": "Expected capture under uniform selection within tied score groups",
        "oracle_correction": "Simulation only; not human review or time savings",
        "total_error_mass": total_loss,
        "count_mae": float(np.mean([record["count_absolute_error"] for record in records])),
        "mean_f1": float(np.mean([record["f1"] for record in records])),
        "micro_f1": 2 * sum(record["tp"] for record in records) / max(1, sum(record["predicted_count"] + record["annotation_count"] for record in records)),
        "median_analysis_ms": float(np.median([record["analysis_ms"] for record in records])),
        "p95_analysis_ms": float(np.percentile([record["analysis_ms"] for record in records], 95)),
        "methods": summary_methods,
        "graph_paired_difference": paired_differences,
    }
    return summary, records


def save_evaluation(summary: dict[str, Any], records: list[dict[str, Any]], out: str | Path) -> None:
    target = Path(out)
    target.mkdir(parents=True, exist_ok=True)
    (target / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    (target / "per-image.json").write_text(json.dumps(records, indent=2) + "\n")
