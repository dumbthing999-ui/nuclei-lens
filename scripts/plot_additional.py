"""Plot every completed additional field; never rerun or tune inference."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'evaluation/additional'
COLORS = {'object_disagreement': '#2255db', 'graph': '#d97822',
          'pixel_disagreement': '#65758e', 'count_variation': '#567c53',
          'shape_flags': '#9a699a', 'random': '#aaaeb8'}


def render() -> None:
    summary = json.loads((OUT / 'summary.json').read_text())
    records = json.loads((OUT / 'per-image.json').read_text())
    protocol = json.loads((OUT / 'frozen-protocol.json').read_text())
    protocol_hash = hashlib.sha256((OUT / 'frozen-protocol.json').read_bytes()).hexdigest()
    expected = {row['id'] for row in protocol['images']}
    actual = {row['filename'] for row in records}
    if (expected != actual or len(records) != len(expected)
            or not summary['complete_selected_manifest']
            or summary['protocol_sha256'] != protocol_hash
            or any(row['protocol_sha256'] != protocol_hash for row in records)):
        raise ValueError('Only the complete, unchanged assessment can be plotted')
    valid = [row for row in records if row['status'] == 'evaluated']
    failed = [row for row in records if row['status'] == 'failed']
    if len(valid) != summary['n_images'] or len(failed) != summary['failed_images']:
        raise ValueError('Summary/record coverage mismatch')
    figures = OUT / 'figures'
    figures.mkdir(exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.6), layout='constrained')
    for name, color in COLORS.items():
        method = summary['methods'][name]
        axes[0].plot(np.arange(21) * 5, np.asarray(method['review_curve']) * 100,
                     color=color, label=name.replace('_', ' '),
                     linewidth=2.4 if name == 'object_disagreement' else 1.5)
    axes[0].set(xlabel='Regions reviewed (% of 20 fixed tiles)',
                ylabel='Annotated FP+FN error mass captured (%)',
                xlim=(0, 100), ylim=(0, 100), title='All evaluated fields · equal tile budget')
    axes[0].axvline(20, color='#8690a2', linestyle=':', linewidth=1)
    axes[0].legend(fontsize=8, loc='lower right')
    names = list(COLORS)
    values = np.asarray([summary['methods'][n]['capture_at_20_percent'] for n in names]) * 100
    intervals = np.asarray([summary['methods'][n]['capture_ci95_image_resampling']
                            for n in names]) * 100
    axes[1].barh([n.replace('_', ' ') for n in names], values,
                 color=[COLORS[n] for n in names], alpha=.85)
    axes[1].errorbar(values, np.arange(len(names)),
                     xerr=[np.maximum(0, values - intervals[:, 0]),
                           np.maximum(0, intervals[:, 1] - values)],
                     fmt='none', ecolor='#172333', capsize=3)
    axes[1].invert_yaxis()
    axes[1].set(xlabel='Annotated error mass captured (%) · 4/20 tiles',
                title='Conditional image-resampling 95% intervals',
                xlim=(0, min(100, max(intervals[:, 1]) + 10)))
    for index, value in enumerate(values):
        axes[1].text(intervals[index, 1] + 1.5, index, f'{value:.1f}%', va='center', fontsize=9)
    for axis in axes:
        axis.grid(alpha=.15)
        axis.set_axisbelow(True)
    fig.suptitle(f'BBBC038 property-filtered additional assessment · {len(valid)} evaluated / '
                 f'{len(records)} selected · {len(failed)} failures', fontsize=12)
    for suffix in ['png', 'svg']:
        fig.savefig(figures / f'review-comparison.{suffix}', dpi=180)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.6), layout='constrained')
    truth = np.asarray([row['annotation_count'] for row in valid])
    predicted = np.asarray([row['predicted_count'] for row in valid])
    f1 = np.asarray([row['f1'] for row in valid])
    points = axes[0].scatter(truth, predicted, c=f1, cmap='viridis', s=18, alpha=.65,
                             vmin=0, vmax=1, edgecolors='none')
    fig.colorbar(points, ax=axes[0], label='Instance F1', shrink=.8)
    limit = max(truth.max(), predicted.max()) * 1.04
    axes[0].plot([0, limit], [0, limit], linestyle='--', linewidth=1, color='#77808e')
    axes[0].set(xlabel='Reference instance count', ylabel='Predicted instance count',
                xlim=(0, limit), ylim=(0, limit), title='Every evaluated field · diagonal = equal count')
    axes[1].hist(f1, bins=np.linspace(0, 1, 21), color='#2255db', edgecolor='white')
    axes[1].set(xlabel='Instance F1 (IoU ≥ 0.5)', ylabel='Number of fields', xlim=(0, 1),
                title=f'Macro F1 {summary["mean_f1"]:.3f} · count MAE {summary["count_mae"]:.2f}')
    for axis in axes:
        axis.grid(alpha=.15)
        axis.set_axisbelow(True)
    fig.suptitle('Additional images, not an independent biological-group test · '
                 'reference-integrity failures reported separately', fontsize=11)
    for suffix in ['png', 'svg']:
        fig.savefig(figures / f'all-fields.{suffix}', dpi=180)
    plt.close(fig)
    print(f'Rendered all {len(valid)} evaluated fields and retained {len(failed)} failure records.')


if __name__ == '__main__':
    render()
