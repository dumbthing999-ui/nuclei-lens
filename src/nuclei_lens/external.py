"""Additional BBBC038 image assessment; separate from frozen BBBC039 inference."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from typing import Any
from zipfile import ZipFile

import numpy as np
from PIL import Image


class ExternalField:
    """Three-method adapter consumed by the unchanged partition evaluator."""

    def __init__(self, archive: ZipFile, row: dict[str, Any]):
        self.archive = archive
        self.row = row

    def filenames(self, split: str) -> list[str]:
        if split != 'additional-images':
            raise ValueError('Unexpected assessment partition')
        return [self.row['id']]

    def image(self, filename: str) -> np.ndarray:
        if filename != self.row['id']:
            raise ValueError('Image is outside the frozen field manifest')
        payload = self.archive.read(self.row['image_path'])
        if hashlib.sha256(payload).hexdigest() != self.row['image_sha256']:
            raise ValueError('Image differs from the frozen raw-image profile')
        with Image.open(BytesIO(payload)) as image:
            array = np.asarray(image).copy()
        if array.ndim == 3:
            if not np.all(array[..., :3] == array[..., :1]):
                raise ValueError('Expected monochrome image')
            if array.shape[2] == 4 and not np.all(array[..., 3] == 255):
                raise ValueError('Nonopaque image is outside this assessment')
            array = array[..., 0]
        if array.dtype != np.uint8 or array.shape != (self.row['height'], self.row['width']):
            raise ValueError('Image dtype/dimensions differ from the frozen profile')
        return np.ascontiguousarray(array)

    def annotations(self, filename: str) -> np.ndarray:
        # Called by evaluate_partition only after analyze has returned.
        if filename != self.row['id']:
            raise ValueError('Annotation is outside the frozen field manifest')
        names = sorted(name for name in self.archive.namelist()
                       if name.startswith(filename + '/masks/') and name.endswith('.png'))
        if not names or len(names) > 10000:
            raise ValueError('Missing or excessive reference instance masks')
        truth = np.zeros((self.row['height'], self.row['width']), dtype=np.int32)
        for index, name in enumerate(names, start=1):
            with Image.open(BytesIO(self.archive.read(name))) as image:
                foreground = np.asarray(image.convert('L')) > 0
            if foreground.shape != truth.shape or not np.any(foreground):
                raise ValueError('Reference mask is empty or has the wrong dimensions')
            if np.any(foreground & (truth > 0)):
                raise ValueError('Reference instance masks overlap; no silent adjudication')
            # Dataset specifies exactly one nucleus per mask file. Preserve its
            # instance identity even if its annotated pixels are disconnected.
            truth[foreground] = index
        return truth


def summarize_additional(records: list[dict[str, Any]], protocol: dict[str, Any], protocol_hash: str) -> dict[str, Any]:
    valid = [record for record in records if record['status'] == 'evaluated']
    failed = [record for record in records if record['status'] == 'failed']
    if not valid:
        raise ValueError('No fields have valid assessment records')
    methods = list(valid[0]['capture_curves'])
    losses = np.asarray([r['error_mass'] for r in valid], dtype=np.float64)
    total_loss = float(losses.sum())
    rng = np.random.default_rng(20261008)
    bootstrap = rng.integers(0, len(valid), size=(2000, len(valid)))
    boot_denominators = losses[bootstrap].sum(axis=1)
    comparisons = {}
    for method in methods:
        curves = np.asarray([r['capture_curves'][method] for r in valid])
        fixed = curves[:, 4]
        boot = np.divide(fixed[bootstrap].sum(axis=1), boot_denominators,
                         out=np.zeros(2000), where=boot_denominators > 0)
        comparisons[method] = {'capture_at_20_percent': float(fixed.sum() / total_loss) if total_loss else 0,
                               'capture_ci95_image_resampling': np.percentile(boot, [2.5, 97.5]).tolist(),
                               'review_curve': (curves.sum(axis=0) / total_loss).tolist() if total_loss else [0.] * 21}
    return {'schema_version': 1, 'generated_at': datetime.now(timezone.utc).isoformat(),
            'dataset': protocol['dataset'], 'protocol_sha256': protocol_hash,
            'selected_images': len(protocol['images']), 'n_images': len(valid), 'failed_images': len(failed),
            'complete_selected_manifest': len(records) == len(protocol['images']),
            'archive_sha256': {'BBBC038-stage1_train.zip': protocol['archive_sha256']},
            'config': protocol['config'], 'source_sha256': protocol['source_sha256'],
            'count_mae': float(np.mean([r['count_absolute_error'] for r in valid])),
            'mean_f1': float(np.mean([r['f1'] for r in valid])),
            'micro_f1': 2 * sum(r['tp'] for r in valid) / max(1, sum(r['predicted_count'] + r['annotation_count'] for r in valid)),
            'total_error_mass': total_loss, 'iou_threshold': .5, 'review_budget': '4 of20 fixed centroid tiles',
            'methods': comparisons, 'median_analysis_ms': float(np.median([r['analysis_ms'] for r in valid])),
            'failures': [{'filename': r['filename'], 'error': r['error']} for r in failed],
            'limitations': protocol['limitations'],
            'interval_scope': 'Image-wise resampling conditional on this property-filtered set; not biological-group independence or population-generalization intervals.'}


def write_json_atomic(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, indent=2) + '\n')
    temporary.replace(path)
