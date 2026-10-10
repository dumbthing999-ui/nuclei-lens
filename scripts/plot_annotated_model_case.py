#!/usr/bin/env python3
"""Plot the declared single-field diagnostic; no new inference or annotation access."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
from pathlib import Path

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
METHODS = ('classical_baseline', 'cellpose_nuclei', 'stardist_2d_fluo')
NAMES = ('Classical baseline', 'Cellpose', 'StarDist')


def render(result_path: Path, protocol_path: Path, output_directory: Path) -> None:
    result = json.loads(result_path.read_text())
    protocol_hash = hashlib.sha256(protocol_path.read_bytes()).hexdigest()
    if (result['protocol']['sha256'] != protocol_hash
            or result['case']['sample_id'] != 'training-001'
            or result['matching']['iou_threshold'] != .5
            or result['case']['inference_performed'] is not False
            or set(result['methods']) != set(METHODS)):
        raise ValueError('Plot requires the declared, complete development-case result')
    metrics = [result['methods'][name]['metrics'] for name in METHODS]
    reference = result['annotation']['instance_count']
    for m in metrics:
        if (m['annotation_count'] != reference
                or m['tp'] + m['fp'] != m['predicted_count']
                or m['tp'] + m['fn'] != reference
                or any(type(m[k]) is not int or m[k] < 0 for k in ('tp', 'fp', 'fn'))
                or type(reference) is not int or reference <= 0
                or not math.isfinite(m['f1'])
                or abs(m['f1'] - 2*m['tp']/(m['predicted_count']+reference)) > 1e-12):
            raise ValueError('Inconsistent instance metrics')
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11,
                         'svg.hashsalt': 'nucleilens-annotation-case-v1'})
    fig, axes = plt.subplots(1, 2, figsize=(11.2, 4.8))
    x = np.arange(3)
    counts = [m['predicted_count'] for m in metrics]
    bars = axes[0].bar(x, counts, color=['#244a67', '#16857d', '#ae681d'], width=.55)
    axes[0].axhline(reference, color='#536371', linestyle='--', linewidth=1.4,
                    label=f'Annotation: {reference}')
    for bar, count in zip(bars, counts, strict=True):
        axes[0].text(bar.get_x() + bar.get_width()/2, count + 1.5, str(count), ha='center')
    axes[0].set_ylim(0, max(counts + [reference]) * 1.18)
    axes[0].set_title('Total count')
    axes[0].set_ylabel('Instances')
    axes[0].legend(frameon=False, loc='lower right')
    fp, fn = [m['fp'] for m in metrics], [m['fn'] for m in metrics]
    axes[1].bar(x, fp, width=.55, color='#bc7232', label='Unmatched prediction (FP)')
    axes[1].bar(x, fn, width=.55, bottom=fp, color='#397591', label='Unmatched annotation (FN)')
    for i, m in enumerate(metrics):
        axes[1].text(i, fp[i] + fn[i] + .35, f"{fp[i]+fn[i]} · F1 {m['f1']:.3f}", ha='center')
    axes[1].set_ylim(0, max(sum(p) for p in zip(fp, fn, strict=True)) * 1.6 + 1)
    axes[1].set_title('One-to-one overlap matching, IoU ≥ 0.5')
    axes[1].set_ylabel('Unmatched instances')
    axes[1].legend(frameon=False, loc='upper right', fontsize=9)
    for ax in axes:
        ax.set_xticks(x, NAMES)
        ax.spines[['top', 'right']].set_visible(False)
        ax.set_axisbelow(True)
        ax.grid(axis='y', color='#d9e0e5', alpha=.7)
    fig.suptitle('NucleiLens · existing model masks and annotation agreement', fontsize=15, x=.06, ha='left')
    fig.text(.06, .91, 'One preselected BBBC039 training field · descriptive development case', color='#536371')
    fig.text(.06, .055, 'Matching errors are threshold-dependent; not confirmed biological split/merge diagnoses.', fontsize=9)
    fig.text(.06, .02, 'No general model ranking, clinical accuracy or human benefit is established.', fontsize=9)
    fig.tight_layout(rect=(.015, .095, .99, .885))
    payloads = {}
    for extension in ('png', 'svg'):
        buffer = io.BytesIO()
        metadata = {'Date': None} if extension == 'svg' else {}
        fig.savefig(buffer, format=extension, dpi=180, metadata=metadata)
        payloads[extension] = buffer.getvalue()
    plt.close(fig)
    # Validate every existing destination before making any writes.
    for extension, payload in payloads.items():
        path = output_directory / f'annotation-agreement.{extension}'
        if path.exists() and path.read_bytes() != payload:
            raise ValueError('Refusing to replace a differing diagnostic figure')
    output_directory.mkdir(parents=True, exist_ok=True)
    for extension, payload in payloads.items():
        path = output_directory / f'annotation-agreement.{extension}'
        if not path.exists():
            path.write_bytes(payload)
    print('Rendered single-case PNG/SVG; no new inference or reference access')


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--result', type=Path, default=ROOT/'evaluation/model-case/result.json')
    parser.add_argument('--protocol', type=Path, default=ROOT/'evaluation/model-case/protocol.json')
    parser.add_argument('--output-directory', type=Path, default=ROOT/'evaluation/model-case/figures')
    args = parser.parse_args()
    render(args.result, args.protocol, args.output_directory)


if __name__ == '__main__':
    main()
