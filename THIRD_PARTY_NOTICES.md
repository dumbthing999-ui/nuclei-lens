# Third-party notices

NucleiLens original project code is MIT licensed. Dependency and dataset licenses
remain their own; the project license does not replace them.

Original dependency notices are available at [/licenses/manifest.json](https://nuclei-lens.dumbthing999.chatgpt.site/licenses/manifest.json)
and under `frontend/public/licenses/`. The inventory includes npm production
dependencies; some are tooling dependencies rather than code sent to the browser.

Pyodide314.0.7 source: https://github.com/pyodide/pyodide/tree/314.0.7
(MPL2.0); CPython3.14.2 source: https://github.com/python/cpython/tree/v3.14.2.
Original runtime files are copied without code changes. The runtime lock's
scikit-image dependency list is narrowed by `scripts/prepare_runtime.mjs`; its
source modification is public. Numerical wheels remain unmodified and SHA256
verified; their bundled notices are preserved and separately extracted.

BBBC039 images/annotations are CC0; citation and source:
https://bbbc.broadinstitute.org/BBBC039.

Regenerate after dependency changes with `python scripts/collect_notices.py`
after preparing the pinned browser runtime.

## npm production dependency inventory

|Package|Version|Declared license|
|---|---|---|
|geotiff|3.0.5|MIT|
|@petamoriken/float16|3.9.3|MIT|
|lerc|3.0.0|Apache-2.0|
|pako|2.2.0|(MIT AND Zlib)|
|parse-headers|2.0.6|MIT|
|quick-lru|6.1.2|MIT|
|web-worker|1.5.0|Apache-2.0|
|xml-utils|1.10.2|CC0-1.0|
|zstddec|0.2.0|MIT AND BSD-3-Clause|
|pyodide|314.0.7|MPL-2.0|
|@types/emscripten|1.41.6|MIT|
|ws|8.22.0|MIT|
|react|19.3.0|MIT|
|react-dom|19.3.0|MIT|
|scheduler|0.28.0|MIT|
