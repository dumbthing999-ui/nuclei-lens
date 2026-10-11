from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.evaluate_bbbc007 import (  # noqa: E402
    binary_outline_to_instances,
    candidate_pairs,
    image_to_grayscale,
)


def test_binary_outline_conversion_keeps_distinct_closed_interiors() -> None:
    outline = np.zeros((32, 32), dtype=np.uint8)
    outline[3:10, 3] = outline[3:10, 9] = 255
    outline[3, 3:10] = outline[9, 3:10] = 255
    outline[17:26, 17] = outline[17:26, 25] = 255
    outline[17, 17:26] = outline[25, 17:26] = 255

    labels, count = binary_outline_to_instances(outline)

    assert count == 2
    assert set(np.unique(labels)) == {0, 1, 2}
    assert labels[5, 5] != 0 and labels[20, 20] != 0
    assert labels[3, 5] == 0


def test_open_outline_is_a_hard_annotation_failure() -> None:
    outline = np.zeros((32, 32), dtype=np.uint8)
    outline[3:20, 3] = 255
    outline[3, 3:20] = 255
    outline[19, 3:10] = 255

    with pytest.raises(ValueError, match="No closed outline interiors"):
        binary_outline_to_instances(outline)


def test_rgb_conversion_matches_browser_luminance_rounding() -> None:
    rgb = np.zeros((32, 32, 3), dtype=np.uint8)
    rgb[0, 0] = [100, 50, 0]
    rgb[0, 1] = [0, 0, 255]

    gray = image_to_grayscale(rgb)

    assert gray[0, :2].tolist() == [59, 29]


def test_selection_uses_all_explicit_dna_paths_and_excludes_actin() -> None:
    images = [
        "BBBC007_v1_images/a/one_D_1UL.tif",
        "BBBC007_v1_images/a/one_F_2UL.tif",
        "BBBC007_v1_images/a/legacy-d0.tif",
    ]
    outlines = [
        "BBBC007_v1_outlines/a/one_D_1UL.tif",
        "BBBC007_v1_outlines/a/one_F_2UL.tif",
        "BBBC007_v1_outlines/a/legacy-d0.tif",
    ]

    assert candidate_pairs(images, outlines) == [{
        "image_path": "BBBC007_v1_images/a/one_D_1UL.tif",
        "outline_path": "BBBC007_v1_outlines/a/one_D_1UL.tif",
    }]
