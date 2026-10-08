"""Verify full coverage, frozen provenance, arithmetic and all saved review curves."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'evaluation/additional'


def check() -> None:
    protocol = json.loads((OUT / 'frozen-protocol.json').read_text())
    protocol_hash = hashlib.sha256((OUT / 'frozen-protocol.json').read_bytes()).hexdigest()
    records = json.loads((OUT / 'per-image.json').read_text())
    summary = json.loads((OUT / 'summary.json').read_text())
    expected = {row['id'] for row in protocol['images']}
    assert len(records) == len(expected) == summary['selected_images']
    assert {row['filename'] for row in records} == expected
    assert summary['complete_selected_manifest']
    assert summary['protocol_sha256'] == protocol_hash
    for name, key in [('raw-image-profile.json', 'profile_sha256'),
                      ('content-overlap-screen.json', 'overlap_screen_sha256')]:
        path = ROOT / 'research/external-assessment' / name
        assert hashlib.sha256(path.read_bytes()).hexdigest() == protocol[key], name
    for name, expected_hash in protocol['source_sha256'].items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected_hash, name
    valid = [row for row in records if row['status'] == 'evaluated']
    failed = [row for row in records if row['status'] == 'failed']
    assert len(valid) == summary['n_images']
    assert len(failed) == summary['failed_images']
    assert len(valid) + len(failed) == len(records)
    assert {r['filename']: r['error'] for r in failed} == {
        r['filename']: r['error'] for r in summary['failures']}
    checks = 0
    for row in records:
        assert row['protocol_sha256'] == protocol_hash
        if row['status'] == 'failed':
            assert row['error']
            continue
        assert row['predicted_count'] == row['tp'] + row['fp']
        assert row['annotation_count'] == row['tp'] + row['fn']
        assert row['count_error'] == row['predicted_count'] - row['annotation_count']
        assert row['count_absolute_error'] == abs(row['count_error'])
        denominator = row['predicted_count'] + row['annotation_count']
        assert np.isclose(row['f1'], 2 * row['tp'] / denominator if denominator else 1)
        losses = np.asarray(row['tile_error_mass'])
        assert losses.shape == (20,)
        assert np.all(losses >= 0)
        assert losses.sum() == row['error_mass'] == row['fp'] + row['fn']
        assert sum(row['tile_count_difference']) == row['count_error']
        assert len(row['region_scores']) == 20
        assert np.isfinite(row['analysis_ms']) and row['analysis_ms'] >= 0
        for method, curve in row['capture_curves'].items():
            scores = np.asarray([0 if method == 'random' else tile[method]
                                 for tile in row['region_scores']])
            assert np.isfinite(scores).all()
            assert len(curve) == 21
            assert np.all(np.diff(curve) >= -1e-9)
            assert np.isclose(curve[0], 0) and np.isclose(curve[-1], losses.sum())
            # A cutoff calculation independent of the evaluator's iterative
            # grouping loop. No reference-based reranking within tied scores.
            for k in range(1, 20):
                cutoff = np.sort(scores)[-k]
                equal = np.isclose(scores, cutoff, rtol=0, atol=1e-12)
                higher = (scores > cutoff) & ~equal
                expected_capture = losses[higher].sum() + losses[equal].sum() * (
                    k - np.count_nonzero(higher)) / np.count_nonzero(equal)
                assert np.isclose(curve[k], expected_capture), (row['filename'], method, k)
                checks += 1
    total = sum(row['error_mass'] for row in valid)
    assert total == summary['total_error_mass']
    assert np.isclose(summary['count_mae'], np.mean([r['count_absolute_error'] for r in valid]))
    assert np.isclose(summary['mean_f1'], np.mean([r['f1'] for r in valid]))
    for method, values in summary['methods'].items():
        curve = np.sum([row['capture_curves'][method] for row in valid], axis=0)
        normalized = curve / total if total else np.zeros(21)
        assert np.allclose(values['review_curve'], normalized)
        assert np.isclose(values['capture_at_20_percent'], normalized[4])
    report = {'checked_at': datetime.now(timezone.utc).isoformat(), 'passed': True,
              'protocol_sha256': protocol_hash, 'selected_fields': len(records),
              'evaluated_fields': len(valid), 'retained_failures': len(failed),
              'independent_cutoff_capture_checks': checks,
              'scope': 'Saved-record arithmetic, complete manifest and unchanged source hashes; not an independent annotation, biological accuracy or human benefit study.'}
    (OUT / 'integrity-check.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))


if __name__ == '__main__':
    check()
