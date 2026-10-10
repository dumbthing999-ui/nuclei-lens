"""Synthetic chart plumbing only; not real model or user evidence."""
from __future__ import annotations

import importlib.util
import json
from hashlib import sha256
from pathlib import Path

import pytest

FILE = Path(__file__).resolve().parents[1]/'scripts/plot_annotated_model_case.py'
spec = importlib.util.spec_from_file_location('case_plot', FILE)
assert spec and spec.loader
plot = importlib.util.module_from_spec(spec)
spec.loader.exec_module(plot)


def fixture(tmp_path: Path) -> tuple[Path, Path]:
    protocol = tmp_path/'protocol.json'
    protocol.write_text('{}')
    result = {'protocol': {'sha256': sha256(protocol.read_bytes()).hexdigest()},
              'case': {'sample_id': 'training-001', 'inference_performed': False},
              'matching': {'iou_threshold': .5}, 'annotation': {'instance_count': 5},
              'methods': {name: {'metrics': {'tp': 4, 'fp': 1, 'fn': 1,
                          'predicted_count': 5, 'annotation_count': 5, 'f1': .8}}
                          for name in plot.METHODS}}
    path = tmp_path/'result.json'
    path.write_text(json.dumps(result))
    return path, protocol


def test_synthetic_render_is_repeatable_and_preserves_differing_files(tmp_path):
    result, protocol = fixture(tmp_path)
    output = tmp_path/'figures'
    plot.render(result, protocol, output)
    first = {p.name: p.read_bytes() for p in output.iterdir()}
    plot.render(result, protocol, output)
    assert first == {p.name: p.read_bytes() for p in output.iterdir()}
    assert set(first) == {'annotation-agreement.png', 'annotation-agreement.svg'}
    (output/'annotation-agreement.png').write_bytes(b'previous-artifact')
    with pytest.raises(ValueError, match='Refusing'):
        plot.render(result, protocol, output)
    assert (output/'annotation-agreement.png').read_bytes() == b'previous-artifact'


def test_plot_rejects_hash_and_metric_corruption_before_writes(tmp_path):
    result, protocol = fixture(tmp_path)
    output = tmp_path/'figures'
    protocol.write_text('{"changed":true}')
    with pytest.raises(ValueError, match='declared'):
        plot.render(result, protocol, output)
    assert not output.exists()
    result, protocol = fixture(tmp_path)
    data = json.loads(result.read_text())
    data['methods'][plot.METHODS[0]]['metrics']['f1'] = float('nan')
    result.write_text(json.dumps(data))
    with pytest.raises(ValueError, match='Inconsistent'):
        plot.render(result, protocol, output)
    assert not output.exists()
