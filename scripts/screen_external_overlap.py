"""Screen same-sized raw image content; never load instance annotations."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
profile = json.loads((ROOT / 'research/external-assessment/raw-image-profile.json').read_text())
candidates = [row for row in profile['images'] if row['candidate_property_scope']]
references = {}
features = []
keys = []


def feature(array: np.ndarray) -> np.ndarray:
    sampled = array.ravel()[np.linspace(0, array.size - 1, 1024, dtype=np.int64)].astype(np.float64)
    sampled -= sampled.mean()
    return sampled / max(float(np.linalg.norm(sampled)), 1e-12)


def orient(array: np.ndarray, variant: int) -> np.ndarray:
    return array if variant == 0 else np.fliplr(array) if variant == 1 else np.flipud(array) if variant == 2 else array[::-1, ::-1]


with ZipFile(ROOT / 'data/raw/BBBC039/images.zip') as archive:
    for name in sorted(n for n in archive.namelist() if n.startswith('images/') and n.endswith('.tif') and not Path(n).name.startswith('._')):
        with Image.open(BytesIO(archive.read(name))) as image:
            array = np.asarray(image).copy()
        references[name] = array
        for variant in range(4):
            features.append(feature(orient(array, variant)))
            keys.append((name, variant, array.shape))
features = np.asarray(features)
results = []
with ZipFile(ROOT / 'data/raw/BBBC038-stage1_train.zip') as archive:
    for row in candidates:
        with Image.open(BytesIO(archive.read(row['image_path']))) as image:
            array = np.asarray(image)
            if array.ndim == 3:
                array = array[..., 0]
        matches = []
        correlations = features @ feature(array)
        for index in np.flatnonzero(correlations >= .90):
            name, variant, shape = keys[int(index)]
            if shape != array.shape:
                continue
            left = array.ravel().astype(np.float64)
            right = orient(references[name], variant).ravel().astype(np.float64)
            full = float(np.corrcoef(left, right)[0, 1])
            if full >= .95:
                matches.append({'bbbc039_image': name, 'orientation': variant,
                                'sample_pearson': float(correlations[index]), 'full_pearson': full})
        results.append({'id': row['id'], 'potential_same_size_overlap': bool(matches), 'matches': matches})
report = {'generated_at': datetime.now(timezone.utc).isoformat(),
          'method': '1024 evenly spaced raw intensity samples; candidate Pearson>=0.90; same-size full-image Pearson>=0.95; original/horizontal/vertical/both flips.',
          'scope': 'Conservative content-overlap screening, not proof of biological independence. Cropped/resampled images, shared experiments or source groups may remain. No annotations/inference read.',
          'n_candidates': len(candidates), 'n_excluded_potential_overlap': sum(r['potential_same_size_overlap'] for r in results),
          'bbbc039_reference_fields': len(references), 'results': results}
(ROOT / 'research/external-assessment/content-overlap-screen.json').write_text(json.dumps(report, indent=2) + '\n')
print(f'Screened {len(candidates)} candidates against {len(references)} BBBC039 raw fields; potential same-size overlaps: {report["n_excluded_potential_overlap"]}.')
