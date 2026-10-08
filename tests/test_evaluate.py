import numpy as np
import pytest
from skimage.measure import label

from nuclei_lens.evaluate import instance_metrics, review_capture


def test_reused_annotation_colors_and_touching_different_colors():
    colors = np.zeros((32, 32), dtype=np.uint8)
    colors[2:5, 2:5] = 1
    colors[15:18, 15:18] = 1
    colors[15:18, 18:21] = 2
    assert label(colors, connectivity=2, background=0).max() == 3


def test_perfect_and_empty_matches():
    labels = np.zeros((64, 64), dtype=np.int32)
    labels[5:15, 5:15] = 1
    assert instance_metrics(labels, labels)["f1"] == 1
    empty = np.zeros_like(labels)
    assert instance_metrics(empty, labels)["fn"] == 1
    assert instance_metrics(labels, empty)["fp"] == 1
    assert instance_metrics(empty, empty)["f1"] == 1


def test_count_accuracy_can_hide_detection_errors():
    prediction = np.zeros((64, 64), dtype=np.int32)
    truth = prediction.copy()
    prediction[5:15, 5:15] = 1
    truth[45:55, 45:55] = 1
    result = instance_metrics(prediction, truth)
    assert result["count_absolute_error"] == 0
    assert result["fp"] == result["fn"] == 1
    assert result["tile_error_mass"].sum() == 2


def test_ties_have_expected_capture_instead_of_favorable_order():
    scores = np.zeros(20)
    losses = np.arange(20, dtype=float)
    assert review_capture(scores, losses, 4) == pytest.approx(losses.sum() * .2)
    assert review_capture(scores, losses, 0) == 0
    assert review_capture(scores, losses, 20) == losses.sum()
    with pytest.raises(ValueError):
        review_capture(scores, losses, 21)
