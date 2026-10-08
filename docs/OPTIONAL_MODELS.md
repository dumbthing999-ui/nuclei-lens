# Optional local Cellpose / StarDist masks

This optional CLI runs two established pretrained models in an isolated local
Python environment. Its outputs are hypotheses for review, not ground truth.
It does not alter NucleiLens's frozen watershed, graph or evaluation source.
The browser imports their already aligned label TIFFs; it does not run these
neural networks. Consensus and model aggregation are established prior art.

## Setup

Use a separate Python3.12 environment. Do not add heavy neural dependencies to
our frozen Python3.14 application environment. These selected versions exist
in their primary PyPI records, checked October8,2026. Installation and actual
model execution status must be recorded separately from adapter tests.

```bash
python3.12 -m venv .venv-models
.venv-models/bin/python -m pip install torch==2.13.0 --index-url https://download.pytorch.org/whl/cpu
.venv-models/bin/python -m pip install cellpose==3.1.1.2 tensorflow-cpu==2.18.0 csbdeep==0.8.2 stardist==0.9.2 numpy==1.26.4 tifffile==2024.9.20 pillow==12.3.0 setuptools==83.0.0
```

The complete observed Linux x86_64 / Python3.12.11 environment is pinned in
`requirements.models.lock`. After the official CPU Torch installation above,
install it with `python -m pip install -r requirements.models.lock`. This is an
observed environment, not a hash-locked or cross-platform installation guarantee. Models download official
pretrained weights on first use. Record actual weight hashes and environment
versions; do not invent runtime or download-size estimates.

## Run and inspect

Run the parent from the ordinary project environment and point `--python` at
the separate model interpreter. An empty output directory is required.

```bash
.venv/bin/python scripts/run_model_masks.py frontend/public/samples/training-001.tif --output-dir model_output/training-001 --python .venv-models/bin/python --timeout 90
```

The two adapters are Cellpose3 `nuclei` (CPU, diameter estimation, grayscale
channels) and StarDist `2D_versatile_fluo` (percentile1/99.8 normalization).
The timeout includes loading/download work and is configurable from0.1–600s.
This is a local CLI boundary, not a sandbox or public remote inference service.

Input is limited to one finite numeric2D field,10MB,1,048,576pixels and2048px
per side. Color is converted to grayscale. The validated pixel array is copied
into a temporary canonical TIFF before a model reads it. Each worker has its own
process group; timeout/interruption kills that group. Model outputs must have
matching dimensions, integer IDs, background0 and IDs within uint32.

Successful masks and `provenance.json` include input file/pixel hashes, actual
model/framework/configuration metadata, discovered weight hashes and output
file/uint32-LE pixel hashes. A failed model is recorded honestly; completed
outputs from an earlier model remain marked partial, never a successful full
run. Output directories stay ignored by Git to avoid publishing private images.

In the browser, expand **Compare masks from another model or editor**, import
the label TIFF and describe its source. Check the actual overlaid outlines,
then explicitly confirm a component if justified. Shape measurements recalculate
after edits/undo; the QA report links original/reviewed masks and source hashes.
Dimension equality does not verify alignment, model identity or correctness.

## Verification boundary

`tests/test_model_masks.py` uses explicitly simulated adapters for plumbing,
validation, provenance and timeout checks. These are not neural-model results.
Actual CPU execution completed on the CC0 BBBC039 training001 field on
October8,2026. Cellpose3.1.1.2 and StarDist0.9.2 each returned68instances. Their
foreground assignments differ at3,738pixels;69correspondence components differ,
including boundary hypotheses. These are disagreements, not69verified errors.
No reference annotations were passed to either model. The browser loads the
actual masks with verified file and uint32-LE pixel hashes, and the bundled
`frontend/public/model-examples/training-001/provenance.json` records the input,
parameters, downloaded weight hashes and observed runtimes. Cellpose setup/
prediction took39.62s and StarDist4.56s in this first local execution; framework
imports are excluded and uncached downloads may be included. These are not
controlled speed benchmarks or claims about browser performance. No pretrained-model accuracy comparison or human
benefit is inferred from this optional integration.

## Primary sources

- Cellpose3 source/version: https://pypi.org/project/cellpose/3.1.1.2/ and https://github.com/MouseLand/cellpose
- Cellpose output IDs/TIFF: https://cellpose.readthedocs.io/en/latest/outputs.html
- StarDist pretrained models: https://github.com/stardist/stardist and https://pypi.org/project/stardist/0.9.2/
- TensorFlow CPU selected version: https://pypi.org/project/tensorflow-cpu/2.18.0/
- PyTorch CPU installation: https://pytorch.org/get-started/locally/
- Existing consensus: https://doi.org/10.3389/fgene.2025.1547788

## Dependency remediation

The first real run used Torch2.6.0+cpu, Pillow11.0.0 and setuptools78.1.0. The
separate optional audit returned61advisory records across those three packages
(including duplicate identifiers), so they were upgraded to Torch2.13.0+cpu,
Pillow12.3.0 and setuptools83.0.0. The observed full environment is pinned in
`requirements.models.lock`. The remediated audit returned no known records.
CPU Torch versions were mapped to their upstream public version for the advisory
lookup; this does not independently audit the CPU wheel. Original/remediated
reports are retained in `evaluation/checks/models-audit-before.json` and
`models-audit.json`. A green application CI alone does not audit this environment.
Primary version records: https://pypi.org/project/torch/2.13.0/,
https://pypi.org/project/pillow/12.3.0/, https://pypi.org/project/setuptools/83.0.0/.

Both actual models completed again after remediation. Counts remain68/68and
output pixel hashes are identical to the first run. Repeat metadata and timings
are retained in `evaluation/checks/model-remediation-rerun.json`; the browser's
original-run provenance remains unchanged. This one-field repeat does not prove
cross-platform determinism or held-out model accuracy.

CI audits these optional dependency pins without installing neural frameworks;
actual model execution is retained local evidence, not a CI neural inference test.
