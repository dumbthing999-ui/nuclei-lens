"""Check source protocol, sample-mask integrity, local doc links and tracked secrets."""
from __future__ import annotations

import base64
import hashlib
import json
import re
import subprocess
import zlib
from pathlib import Path
from urllib.parse import unquote, urlsplit

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
protocol = json.loads((ROOT / 'evaluation/frozen/protocol.json').read_text())
for name, expected in protocol['source_sha256'].items():
    assert hashlib.sha256((ROOT / 'src/nuclei_lens' / name).read_bytes()).hexdigest() == expected, name
manifest = json.loads((ROOT / 'frontend/public/samples/manifest.json').read_text())
for sample in manifest['samples']:
    result = json.loads((ROOT / 'frontend/public' / sample['analysis_url'].lstrip('/')).read_text())
    for run, expected in zip(result['label_maps']['runs'], result['run_counts'], strict=True):
        labels = np.frombuffer(zlib.decompress(base64.b64decode(run)), dtype='<u4')
        assert labels.size == result['width'] * result['height']
        assert np.count_nonzero(np.unique(labels)) == expected

failures = []
for document in [ROOT / 'README.md', *sorted((ROOT / 'docs').rglob('*.md'))]:
    for target in re.findall(r'!?\[[^\]]*\]\(([^\s)]+)\)', document.read_text()):
        parsed = urlsplit(target.strip('<>'))
        if parsed.scheme or not parsed.path:
            continue
        path = document.parent / unquote(parsed.path)
        if not path.exists():
            failures.append(f'{document.relative_to(ROOT)}: missing {target}')

patterns = [re.compile(rb'eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{20,}'),
            re.compile(rb'github_pat_[A-Za-z0-9_]{40,}'), re.compile(rb'gh[pousr]_[A-Za-z0-9]{30,}')]
files = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')
for name in filter(None, files):
    file = ROOT / name
    if not file.is_file():
        continue
    if file.name == '.env':
        failures.append(f'Tracked private env: {name}')
    payload = file.read_bytes()
    if any(pattern.search(payload) for pattern in patterns):
        failures.append(f'Possible credential in tracked file: {name}')
if failures:
    raise SystemExit('\n'.join(failures))
print('PASS: frozen source, all real sample masks, local document links and tracked credential patterns.')
