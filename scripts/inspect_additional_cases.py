"""Post-assessment, deterministic difficult/median cases; no inference tuning."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from zipfile import ZipFile

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from skimage.segmentation import find_boundaries

from nuclei_lens.core import Config, analyze
from nuclei_lens.evaluate import instance_metrics
from nuclei_lens.external import ExternalField

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'evaluation/additional'


def inspect() -> None:
    protocol = json.loads((OUT / 'frozen-protocol.json').read_text())
    summary = json.loads((OUT / 'summary.json').read_text())
    if not summary['complete_selected_manifest']:
        raise ValueError('Wait for the complete assessment')
    for name, expected in protocol['source_sha256'].items():
        if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != expected:
            raise ValueError('Frozen source changed: ' + name)
    records = [row for row in json.loads((OUT / 'per-image.json').read_text())
               if row['status'] == 'evaluated']
    by_f1 = sorted(records, key=lambda row: (row['f1'], row['filename']))
    choices = [('Lowest instance F1', by_f1[0]),
               ('Largest absolute count error', sorted(records, key=lambda row: (
                   -row['count_absolute_error'], row['filename']))[0]),
               ('Middle field by instance F1', by_f1[len(by_f1) // 2])]
    manifest = {row['id']: row for row in protocol['images']}
    fig, axes = plt.subplots(3, 3, figsize=(12, 11), layout='constrained')
    case_records = []
    with ZipFile(ROOT / 'data/raw/BBBC038-stage1_train.zip') as archive:
        for index, (reason, record) in enumerate(choices):
            field = ExternalField(archive, manifest[record['filename']])
            image = field.image(record['filename'])
            result = analyze(image, Config(**protocol['config']))
            # Reference read strictly after inference, including this illustrative rerun.
            truth = field.annotations(record['filename'])
            prediction = result['masks'][0]
            measured = instance_metrics(prediction, truth)
            for name in ['predicted_count', 'annotation_count', 'tp', 'fp', 'fn', 'f1']:
                if not np.isclose(measured[name], record[name]):
                    raise ValueError('Illustrative rerun differs from saved assessment: ' + name)
            for column, (title, labels, color) in enumerate([
                    ('Raw image', None, None),
                    (f'Prediction · {record["predicted_count"]} instances', prediction, '#34d399'),
                    (f'Original reference · {record["annotation_count"]} '
                     f'{"instance" if record["annotation_count"] == 1 else "instances"}', truth, '#ffb454')]):
                axis = axes[index, column]
                axis.imshow(image, cmap='gray', vmin=0, vmax=255)
                if labels is not None:
                    boundary = find_boundaries(labels, mode='inner')
                    rgba = np.zeros((*image.shape, 4))
                    rgba[boundary] = matplotlib.colors.to_rgba(color)
                    axis.imshow(rgba)
                axis.set_title(title, fontsize=10)
                axis.set_axis_off()
            axes[index, 0].text(0, -.06, f'{reason}\n{record["filename"][:12]} · F1 {record["f1"]:.3f}',
                                transform=axes[index, 0].transAxes, fontsize=9, va='top')
            case_records.append({'selection_reason': reason, 'filename': record['filename'],
                                 'f1': record['f1'], 'count_absolute_error': record['count_absolute_error'],
                                 'prediction_reference_counts': [record['predicted_count'], record['annotation_count']],
                                 'exact_metric_rerun_verified': True})
    fig.suptitle('Post-assessment case inspection · deterministic selection, no tuning\n'
                 'Reference outlines are benchmark annotations, not adjudicated biological truth.', fontsize=12)
    (OUT / 'figures').mkdir(exist_ok=True)
    fig.savefig(OUT / 'figures/case-inspection.png', dpi=160)
    plt.close(fig)
    (OUT / 'case-inspection.json').write_text(json.dumps({
        'selection': 'Post-hoc descriptive cases: minimum F1, maximum absolute count error, upper middle sorted F1; filename breaks ties. Cases may coincide.',
        'cases': case_records, 'scope': 'Inspectability and deterministic reproducibility, not a corrected annotation, failure-cause diagnosis or human validation.'}, indent=2) + '\n')
    print('Verified unchanged-source reruns for all three declared illustrative selections.')


if __name__ == '__main__':
    inspect()
