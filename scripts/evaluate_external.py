"""Freeze/resume an additional image assessment without tuning inference."""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import cast
from zipfile import ZipFile

from nuclei_lens.core import Config
from nuclei_lens.data import Dataset
from nuclei_lens.evaluate import evaluate_partition
from nuclei_lens.external import ExternalField, summarize_additional, write_json_atomic

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'evaluation/additional'
PROTOCOL = OUT / 'frozen-protocol.json'
ARCHIVE = ROOT / 'data/raw/BBBC038-stage1_train.zip'
SOURCES = ['src/nuclei_lens/core.py', 'src/nuclei_lens/graph.py', 'src/nuclei_lens/evaluate.py',
           'src/nuclei_lens/external.py', 'scripts/evaluate_external.py',
           'scripts/inspect_external_images.py', 'scripts/screen_external_overlap.py']


def digest(path: Path) -> str:
    with path.open('rb') as source:
        return hashlib.file_digest(source, 'sha256').hexdigest()


def freeze() -> None:
    if PROTOCOL.exists():
        raise ValueError('Protocol already frozen; do not overwrite it or tune against its results')
    profile_path = ROOT / 'research/external-assessment/raw-image-profile.json'
    overlap_path = ROOT / 'research/external-assessment/content-overlap-screen.json'
    profile = json.loads(profile_path.read_text())
    overlap = json.loads(overlap_path.read_text())
    excluded = {r['id'] for r in overlap['results'] if r['potential_same_size_overlap']}
    candidates = [r for r in profile['images'] if r['candidate_property_scope']]
    if {r['id'] for r in overlap['results']} != {r['id'] for r in candidates}:
        raise ValueError('Overlap screening does not cover the complete candidate manifest')
    rows = [{key: row[key] for key in ['id', 'image_path', 'image_sha256', 'width', 'height']}
            for row in candidates if row['id'] not in excluded]
    original = json.loads((ROOT / 'evaluation/frozen/protocol.json').read_text())
    protocol = {'frozen_at': datetime.now(timezone.utc).isoformat(),
                'dataset': 'BBBC038v1 additional assessment of the public labeled stage1 training archive; not its official competition test set',
                'source_record': 'https://bbbc.broadinstitute.org/BBBC038', 'license': 'CC0',
                'archive_sha256': digest(ARCHIVE), 'config': original['config'],
                'source_sha256': {name: digest(ROOT / name) for name in SOURCES},
                'profile_sha256': digest(profile_path), 'overlap_screen_sha256': digest(overlap_path),
                'total_archive_images': profile['n_images'], 'property_candidates': len(candidates),
                'excluded_potential_same_size_overlap': sorted(excluded), 'images': rows,
                'selection': profile['scope_rule'] + '; exclude potential same-sized content overlap before inference/annotation reading; evaluate every remaining image, sorted by ImageId.',
                'primary': 'Frozen FP+FN cardinality-first IoU>=0.5 matching, expected tie capture,4 of20 centroid tiles; object disagreement preselected. All6 comparators retained.',
                'annotation_policy': 'One original PNG mask per reference instance; preserve disconnected identity. Empty/wrong-shaped/overlapping masks are recorded as annotation failures, never silently clipped or fixed.',
                'failures': 'Retain every selected image as evaluated or failed. Report failures separately; no post-result exclusion or parameter change.',
                'bootstrap': '2000 image-wise resamples,seed20261008; conditional descriptive intervals only.',
                'secondary_oracle_curves': 'Discarded from this additional report; they are not human behavior.',
                'limitations': [
                    'Selection is based on raw image properties, not independently verified fluorescence modality or per-image cell/source metadata.',
                    'Same-sized affine-intensity/flip overlap screening does not remove every crop/resample, shared experiment or related biological source.',
                    'BBBC038 contains mixed modalities and source groups; this assessment does not prove biological-group independence or universal generalization.',
                    'Original public annotations have documented imperfections. Reference integrity failures are retained, not manually adjudicated.',
                    'No additional images are used to tune inference. Original BBBC039 frozen test results/code remain unchanged.',
                    'Error concentration is not human review accuracy/time savings or automatic mask-correction benefit.',
                ]}
    write_json_atomic(PROTOCOL, protocol)
    print(f'Frozen {len(rows)} images; excluded {len(excluded)} potential overlaps. No real annotations or inference read.')


def run(resume: bool) -> None:
    protocol = json.loads(PROTOCOL.read_text())
    protocol_hash = digest(PROTOCOL)
    if digest(ARCHIVE) != protocol['archive_sha256']:
        raise ValueError('Archive differs from the frozen local checksum')
    for name, expected in protocol['source_sha256'].items():
        if digest(ROOT / name) != expected:
            raise ValueError(f'Frozen assessment source changed: {name}')
    cache = ROOT / 'data/cache/BBBC038-assessment' / protocol_hash
    if cache.exists() and any(cache.glob('*.json')) and not resume:
        raise ValueError('Existing checkpoints require explicit --resume; never silently restart/tune')
    config = Config(**protocol['config'])
    records = []
    with ZipFile(ARCHIVE) as archive:
        for index, row in enumerate(protocol['images'], start=1):
            checkpoint = cache / (row['id'] + '.json')
            if checkpoint.exists():
                record = json.loads(checkpoint.read_text())
                if record['protocol_sha256'] != protocol_hash or record['filename'] != row['id']:
                    raise ValueError('Checkpoint provenance mismatch')
            else:
                try:
                    # Structural adapter implements exactly the methods used by
                    # the unchanged nominal Dataset interface. Discard its BBBC039
                    # summary metadata; aggregate with actual external provenance.
                    _, result = evaluate_partition(cast(Dataset, ExternalField(archive, row)), 'additional-images', config)
                    record = result[0]
                    record.pop('oracle_count_error_curves', None)
                    record.update(status='evaluated', protocol_sha256=protocol_hash)
                except Exception as error:
                    record = {'filename': row['id'], 'status': 'failed', 'protocol_sha256': protocol_hash,
                              'error': type(error).__name__ + ': ' + str(error)}
                write_json_atomic(checkpoint, record)
            records.append(record)
            print(f'additional {index}/{len(protocol["images"])}: {row["id"][:12]} {record["status"]}', flush=True)
    write_json_atomic(OUT / 'per-image.json', records)
    summary = summarize_additional(records, protocol, protocol_hash)
    write_json_atomic(OUT / 'summary.json', summary)
    print(json.dumps({key: summary[key] for key in ['selected_images', 'n_images', 'failed_images', 'count_mae', 'mean_f1']}), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--freeze', action='store_true')
    parser.add_argument('--run', action='store_true')
    parser.add_argument('--resume', action='store_true')
    args = parser.parse_args()
    if args.freeze == args.run:
        parser.error('Choose exactly one of --freeze or --run')
    if args.freeze:
        freeze()
    else:
        run(args.resume)
