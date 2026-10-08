"""Packaging boundary checks with deliberately tiny fake runtime fixtures, not inference."""
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
FILES = ['pyodide.js', 'pyodide.mjs', 'pyodide.asm.mjs', 'pyodide.asm.wasm',
         'python_stdlib.zip', 'pyodide-lock.json']


@pytest.fixture
def package(tmp_path):
    for directory in ['scripts', 'frontend/dist/runtime/pyodide',
                      'frontend/dist/engine/nuclei_lens', 'src/nuclei_lens', 'evaluation', 'dist']:
        (tmp_path / directory).mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / 'scripts/copy_site_dist.mjs', tmp_path / 'scripts/copy_site_dist.mjs')
    (tmp_path / 'frontend/dist/index.html').write_text('fixture, not a functioning application')
    (tmp_path / 'dist/previous.txt').write_text('preserve on validation failure')
    records = []
    for filename in [*FILES, 'test-wheel.whl']:
        data = ('test-only fixture: ' + filename).encode()
        (tmp_path / 'frontend/dist/runtime/pyodide' / filename).write_bytes(data)
        records.append({'file': filename, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()})
    (tmp_path / 'evaluation/runtime-manifest.json').write_text(json.dumps({
        'runtime_files': records[:6], 'packages': records[6:]}))
    for filename in ['__init__.py', 'core.py', 'graph.py', 'raster.py']:
        for directory in ['src/nuclei_lens', 'frontend/dist/engine/nuclei_lens']:
            (tmp_path / directory / filename).write_text('# test-only engine fixture')
    return tmp_path


def run_copy(package):
    return subprocess.run(['node', str(package / 'scripts/copy_site_dist.mjs')],
                          capture_output=True, text=True, timeout=15, check=False)


def test_complete_static_fixture_copies(package):
    result = run_copy(package)
    assert result.returncode == 0, result.stderr
    assert (package / 'dist/index.html').exists()
    assert not (package / 'dist/previous.txt').exists()


@pytest.mark.parametrize('failure', ['missing-loader', 'changed-wheel', 'stale-engine'])
def test_bad_static_inputs_preserve_previous_dist(package, failure):
    if failure == 'missing-loader':
        (package / 'frontend/dist/runtime/pyodide/pyodide.mjs').unlink()
    elif failure == 'changed-wheel':
        (package / 'frontend/dist/runtime/pyodide/test-wheel.whl').write_text('tampered')
    else:
        (package / 'frontend/dist/engine/nuclei_lens/core.py').write_text('# stale')
    result = run_copy(package)
    assert result.returncode != 0
    assert (package / 'dist/previous.txt').read_text() == 'preserve on validation failure'
