"""Collect original dependency notices and source locations for the static build."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from urllib.request import urlopen
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / 'frontend/public/licenses'
TARGET.mkdir(exist_ok=True)
rows = []
seen = set()


def npm(name: str) -> None:
    if name in seen:
        return
    seen.add(name)
    package = ROOT / 'frontend/node_modules' / name
    metadata = json.loads((package / 'package.json').read_text())
    notices = []
    for source in package.iterdir():
        if source.is_file() and source.name.lower().startswith(('license', 'licence', 'copying', 'notice')):
            target = TARGET / (name.replace('/', '--') + '-' + source.name)
            target.write_bytes(source.read_bytes())
            notices.append(target.name)
    rows.append({'name': name, 'version': metadata['version'], 'license': metadata.get('license'),
                 'repository': metadata.get('repository'), 'notices': notices})
    for dependency in metadata.get('dependencies', {}):
        npm(dependency)


for name in json.loads((ROOT / 'frontend/package.json').read_text())['dependencies']:
    npm(name)

sources = {
    'Pyodide-MPL-2.0.txt': 'https://raw.githubusercontent.com/pyodide/pyodide/314.0.7/LICENSE',
    'CPython-3.14.2-LICENSE.txt': 'https://raw.githubusercontent.com/python/cpython/v3.14.2/LICENSE',
    'Apache-2.0.txt': 'https://www.apache.org/licenses/LICENSE-2.0.txt',
}
provenance = []
for filename, url in sources.items():
    target = TARGET / filename
    if not target.exists():
        with urlopen(url, timeout=30) as response:
            target.write_bytes(response.read())
    provenance.append({'file': filename, 'source': url, 'sha256': hashlib.sha256(target.read_bytes()).hexdigest()})
# Preserve the actual LERC copyright notice; its package omits a LICENSE file.
lerc = (ROOT / 'frontend/node_modules/lerc/LercDecode.js').read_text(encoding='utf-8-sig')
(TARGET / 'lerc-copyright.txt').write_text(lerc[lerc.index('/*', lerc.index('/*') + 2):lerc.index('*/', lerc.index('/*', lerc.index('/*') + 2)) + 2])
wheel_rows = []
for wheel in sorted((ROOT / 'frontend/public/runtime/pyodide').glob('*.whl')):
    extracted = []
    with ZipFile(wheel) as archive:
        for name in archive.namelist():
            leaf = Path(name).name.lower()
            if leaf.startswith(('license', 'copying', 'notice')) and not name.endswith('/') and not leaf.endswith(('.py', '.pyc')):
                destination = TARGET / 'wheels' / wheel.stem / name
                if '..' in Path(name).parts or Path(name).is_absolute():
                    raise ValueError('Unsafe notice archive path')
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(archive.read(name))
                extracted.append(str(destination.relative_to(TARGET)))
    wheel_rows.append({'file': wheel.name, 'sha256': hashlib.sha256(wheel.read_bytes()).hexdigest(), 'notices': extracted})
manifest = {'npm_production_dependency_inventory': rows, 'upstream_notices': provenance,
            'wheel_notices': wheel_rows,
            'pyodide_source': 'https://github.com/pyodide/pyodide/tree/314.0.7',
            'runtime_lock_change': 'Only scikit-image dependency metadata was narrowed to numerical modules; original wheel contents are unmodified. See scripts/prepare_runtime.mjs for the reproducible modification.'}
(TARGET / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
text = '''# Third-party notices\n\nNucleiLens original project code is MIT licensed. Dependency and dataset licenses\nremain their own; the project license does not replace them.\n\nOriginal dependency notices are available at [/licenses/manifest.json](https://nuclei-lens.dumbthing999.chatgpt.site/licenses/manifest.json)\nand under `frontend/public/licenses/`. The inventory includes npm production\ndependencies; some are tooling dependencies rather than code sent to the browser.\n\nPyodide314.0.7 source: https://github.com/pyodide/pyodide/tree/314.0.7\n(MPL2.0); CPython3.14.2 source: https://github.com/python/cpython/tree/v3.14.2.\nOriginal runtime files are copied without code changes. The runtime lock's\nscikit-image dependency list is narrowed by `scripts/prepare_runtime.mjs`; its\nsource modification is public. Numerical wheels remain unmodified and SHA256\nverified; their bundled notices are preserved and separately extracted.\n\nBBBC039 images/annotations are CC0; citation and source:\nhttps://bbbc.broadinstitute.org/BBBC039.\nBBBC038 images/annotations used in additional-assessment figures are CC0:\nhttps://bbbc.broadinstitute.org/BBBC038.\n\nRegenerate after dependency changes with `python scripts/collect_notices.py`\nafter preparing the pinned browser runtime.\n\n## npm production dependency inventory\n\n|Package|Version|Declared license|\n|---|---|---|\n'''
for row in rows:
    text += f"|{row['name']}|{row['version']}|{row['license']}|\n"
(ROOT / 'THIRD_PARTY_NOTICES.md').write_text(text)
print(f'Collected notices for {len(rows)} npm dependencies and {len(wheel_rows)} original runtime wheels.')
