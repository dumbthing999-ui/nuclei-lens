"""Profile BBBC038 raw images without opening annotations or running inference."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
archive_path = ROOT / 'data/raw/BBBC038-stage1_train.zip'
rows = []
with ZipFile(archive_path) as archive:
    for name in sorted(n for n in archive.namelist() if '/images/' in n and n.endswith('.png')):
        payload = archive.read(name)
        with Image.open(BytesIO(payload)) as image:
            pixels = np.asarray(image).copy()
        height, width = pixels.shape[:2]
        opaque = pixels.ndim == 2 or pixels.shape[-1] != 4 or bool(np.all(pixels[..., 3] == 255))
        monochrome = pixels.ndim == 2 or bool(np.all(pixels[..., :3] == pixels[..., :1]))
        gray = pixels if pixels.ndim == 2 else pixels[..., 0]
        median, p99 = [float(x) for x in np.percentile(gray, [50, 99])]
        dimensions = 32 <= min(width, height) and max(width, height) <= 2048 and width * height <= 1048576
        eligible = dimensions and opaque and monochrome and pixels.dtype == np.uint8 and median < 64 and p99 - median >= 16
        rows.append({'id': name.split('/')[0], 'image_path': name, 'width': width, 'height': height,
                     'dtype': str(pixels.dtype), 'monochrome': monochrome, 'opaque': opaque,
                     'median': median, 'p99': p99, 'image_sha256': hashlib.sha256(payload).hexdigest(),
                     'candidate_property_scope': bool(eligible)})
target = ROOT / 'research/external-assessment'
target.mkdir(exist_ok=True)
report = {'generated_at': datetime.now(timezone.utc).isoformat(),
          'dataset': 'BBBC038v1 stage1 labeled training archive',
          'scope_rule': 'uint8 monochrome opaque image,32+ pixels per side,<=2048 per side,<=1048576 total pixels,median<64,p99-minus-median>=16',
          'meaning': 'Image-property subset only; this does not prove fluorescence modality, biological group independence or absence of overlap with BBBC039.',
          'status': 'Raw image profiling only. No annotations opened and no inference performed. Overlap screening and protocol freeze still required before external evaluation.',
          'n_images': len(rows), 'n_property_candidates': sum(r['candidate_property_scope'] for r in rows),
          'images': rows}
(target / 'raw-image-profile.json').write_text(json.dumps(report, indent=2) + '\n')
print(f'Profiled {len(rows)} raw images; {report["n_property_candidates"]} property candidates. No inference/annotations.')
