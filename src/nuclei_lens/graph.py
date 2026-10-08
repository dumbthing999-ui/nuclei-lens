"""Sparse overlap graphs separate count changes from boundary-only changes."""

from __future__ import annotations

from typing import Any

import numpy as np
from scipy import ndimage as ndi


def object_stats(labels: np.ndarray) -> dict[int, dict[str, Any]]:
    areas = np.bincount(labels.ravel())
    ids = np.flatnonzero(areas[1:]) + 1
    if len(ids) == 0:
        return {}
    centroids = ndi.center_of_mass(np.ones(labels.shape, dtype=np.uint8), labels, ids)
    boxes = ndi.find_objects(labels)
    return {
        int(label_id): {
            "area": int(areas[label_id]),
            "x": float(center[1]),
            "y": float(center[0]),
            "bbox": [boxes[label_id - 1][1].start, boxes[label_id - 1][0].start,
                     boxes[label_id - 1][1].stop, boxes[label_id - 1][0].stop],
        }
        for label_id, center in zip(ids, centroids, strict=True)
    }


def overlaps(a: np.ndarray, b: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    if a.shape != b.shape:
        raise ValueError("Instance masks must have identical dimensions.")
    stride = int(b.max()) + 1
    active = (a > 0) & (b > 0)
    if not active.any():
        empty = np.zeros(0, dtype=np.int64)
        return empty, empty, empty
    pairs, intersections = np.unique(
        a[active].astype(np.int64) * stride + b[active], return_counts=True
    )
    return pairs // stride, pairs % stride, intersections


def compare_instances(baseline: np.ndarray, alternate: np.ndarray) -> dict[str, Any]:
    """Compare instance cardinality within connected correspondence components.

    An edge requires >=45% coverage of the smaller object. This avoids linking
    adjacent nuclei through small incidental boundary overlaps. All instances,
    including unmatched alternate objects, enter the graph. Events describe
    disagreement, not which segmentation is correct.
    """
    left = object_stats(baseline)
    right = object_stats(alternate)
    left_ids, right_ids, intersections = overlaps(baseline, alternate)
    nodes = [(0, label_id) for label_id in left] + [(1, label_id) for label_id in right]
    parent = {node: node for node in nodes}

    def find(node: tuple[int, int]) -> tuple[int, int]:
        while parent[node] != node:
            parent[node] = parent[parent[node]]
            node = parent[node]
        return node

    best_iou = {label_id: 0.0 for label_id in left}
    for a_id, b_id, intersection in zip(left_ids, right_ids, intersections, strict=True):
        a_id, b_id, intersection = int(a_id), int(b_id), int(intersection)
        area_a, area_b = left[a_id]["area"], right[b_id]["area"]
        iou = intersection / (area_a + area_b - intersection)
        best_iou[a_id] = max(best_iou[a_id], iou)
        if intersection / min(area_a, area_b) >= 0.45:
            root_a, root_b = find((0, a_id)), find((1, b_id))
            if root_a != root_b:
                parent[root_b] = root_a
    components: dict[tuple[int, int], list[tuple[int, int]]] = {}
    for node in nodes:
        components.setdefault(find(node), []).append(node)
    events = []
    for component in components.values():
        a_ids = sorted(node[1] for node in component if node[0] == 0)
        b_ids = sorted(node[1] for node in component if node[0] == 1)
        if len(a_ids) == len(b_ids):
            continue
        members = [left[label_id] for label_id in a_ids] + [right[label_id] for label_id in b_ids]
        area_sum = sum(obj["area"] for obj in members)
        kind = "split alternative" if len(b_ids) > len(a_ids) else "merge alternative"
        if not a_ids:
            kind = "additional detection"
        elif not b_ids:
            kind = "lost detection"
        events.append({
            "kind": kind,
            "baseline_ids": a_ids,
            "alternate_ids": b_ids,
            "baseline_count": len(a_ids),
            "alternate_count": len(b_ids),
            "magnitude": abs(len(b_ids) - len(a_ids)),
            "x": sum(obj["x"] * obj["area"] for obj in members) / area_sum,
            "y": sum(obj["y"] * obj["area"] for obj in members) / area_sum,
            "bbox": [min(obj["bbox"][0] for obj in members),
                     min(obj["bbox"][1] for obj in members),
                     max(obj["bbox"][2] for obj in members),
                     max(obj["bbox"][3] for obj in members)],
        })
    return {
        "events": events,
        "object_disagreement": [
            {"x": obj["x"], "y": obj["y"], "score": 1 - best_iou[label_id]}
            for label_id, obj in left.items()
        ],
    }
