import numpy as np
import pytest

from nuclei_lens.graph import compare_instances, object_stats, overlaps


def cancellation_masks():
    baseline = np.zeros((64, 100), dtype=np.int32)
    baseline[10:30, 5:25] = 1
    baseline[10:30, 55:65] = 2
    baseline[10:30, 65:75] = 3
    alternate = baseline.copy()
    alternate[10:30, 5:15] = 1
    alternate[10:30, 15:25] = 2
    alternate[10:30, 55:75] = 3
    return baseline, alternate


def test_cancelling_merge_and_split_are_both_visible():
    baseline, alternate = cancellation_masks()
    assert baseline.max() == alternate.max() == 3
    events = compare_instances(baseline, alternate)["events"]
    assert {event["kind"] for event in events} == {"split alternative", "merge alternative"}
    assert sum(event["magnitude"] for event in events) == 2


def test_boundary_jitter_does_not_become_count_disagreement():
    baseline = np.zeros((64, 64), dtype=np.int32)
    baseline[10:30, 10:30] = 1
    alternate = np.roll(baseline, 1, axis=1)
    result = compare_instances(baseline, alternate)
    assert result["events"] == []
    assert 0 < result["object_disagreement"][0]["score"] < 1


def test_unmatched_objects_and_noncontiguous_ids():
    baseline = np.zeros((64, 64), dtype=np.int32)
    alternate = baseline.copy()
    baseline[5:15, 5:15] = 8
    alternate[40:50, 40:50] = 12
    assert set(object_stats(baseline)) == {8}
    assert {e["kind"] for e in compare_instances(baseline, alternate)["events"]} == {
        "lost detection", "additional detection"
    }


def test_relabeling_preserves_events():
    baseline, alternate = cancellation_masks()
    first = compare_instances(baseline, alternate)["events"]
    second = compare_instances(baseline * 3, alternate * 7)["events"]
    assert [(x["kind"], x["magnitude"], x["bbox"]) for x in first] == [
        (x["kind"], x["magnitude"], x["bbox"]) for x in second
    ]


def test_different_shapes_rejected():
    with pytest.raises(ValueError, match="identical"):
        overlaps(np.zeros((2, 3), dtype=int), np.zeros((3, 2), dtype=int))
