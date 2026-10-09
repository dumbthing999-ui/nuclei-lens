# Security review

Updated October 8, 2026. Scope: this project's browser, scientific core, optional local API, dependencies, and release artifacts.

## Threat model

Assets: local image bytes, manual review records, availability of the user's browser, source integrity, and account credentials used only by publishing tools. Untrusted inputs: image files, filenames, malformed headers, manual counts, and arbitrary web origins. The hosted application is a static client, with no project analysis backend or LLM actions.

## Implemented controls and evidence

| Surface | Control | Evidence |
|---|---|---|
| Image files | 10 MB bound; single-frame and dimension/pixel limits; finite numeric arrays | `raster.py`, `engine-worker.js`, core tests |
| Browser decoding | TIFF metadata checked before raster allocation; PNG/JPEG header bounds before bitmap decode | `engine-worker.js`; actual TIFF browser/native parity check |
| Browser compute | Dedicated worker; 90-second watchdog; cancellation terminates worker | `main.tsx`; browser workflow |
| Native decoder | Pillow upgraded from vulnerable 12.2 to 12.3; browser runtime excludes Pillow | `pyproject.toml`, `prepare_runtime.mjs`, audit JSON |
| Local API | Loopback-only documented; allowed Host; same-origin analysis; 2 slots acquired before body read; 5-second body timeout; killable90-second compute child | `api.py`; tests for origin/host/body/type rejection |
| Injection / file paths | Raw bytes, no filename-derived file writes, URL fetch, HTML injection, shell/model actions, or database | Manual source review |
| Review input | Bounded whole-number counts; notes truncated; React escapes text | `review.ts`, Vitest |
| Secrets | Environment excluded from Git; no application API keys required | `.gitignore`, `.env.example`; pre-publication scan |
| Network | Scientific assets and hosting challenge requests occur; application image processing stays in worker. No anonymity guarantee | Production browser workflow; network observations are scoped to tested path |

## Dependency findings

Initial native audit found known Pillow 12.2 advisories. Upgrading to 12.3 and rerunning the native audit produced zero known findings. The browser now uses GeoTIFF.js and browser bitmap decoding; its pinned scientific runtime contains no Pillow wheel. The installed npm dependency audit also returned zero known findings. Reports: `evaluation/checks/python-audit.json` and `npm-audit.json`. These are timestamped snapshots, not security guarantees.

## Remaining limitations

- Native CPU jobs now execute in bounded child processes. Timeout and task cancellation kill/drain the child before slot release. A disconnected HTTP client may leave its task running until the deadline; disconnect is not guaranteed to cancel the ASGI task. This does not establish safety for public exposure, which remains unsupported.
- Complex images can consume significant browser CPU/memory despite bounds. Cancelling terminates the worker; queued main-thread operations and library bugs remain possible.
- The browser and native PNG decoder have different precision semantics. Exact parity is verified for the bundled 16-bit TIFF, not every supported file encoding.
- Bandit1.9.4 Python AST security scan completed across src with zero findings and scanner errors. This covers common Python patterns, not JavaScript or an independent security assessment. No parser fuzzing, independent penetration test, authentication audit or regulatory compliance assessment has been performed.
- Hosting requests reveal normal connection metadata; no promise of anonymous web use or institutional compliance is made.
- Manual review is decision support. It does not validate segmentation masks or make clinical diagnoses.

## Reproduce

```bash
.venv/bin/pip-audit --strict --no-deps -r requirements.lock --format json
npm audit --prefix frontend --json
.venv/bin/pytest
npm test --prefix frontend
```

Only this project's own inputs and infrastructure were examined. No third-party security testing was performed.


## Explicit mask replacement review — October8

Lossless assets decode into exactly4bytes per image pixel for each declared run,
with bounded compressed input and streamed expansion checks. Reported instance
counts must match actual label sets. Component IDs must be unique, positive,
integer and present in the source maps. Replacement rejects edited source geometry
and retained-object overlap, assigns fresh IDs and checks the count delta.
Undo history is bounded to20 entries and1,048,576 changed pixels. TIFF is a fixed
single-channel uint32 encoding; independent GeoTIFF.js readback matches exact
values, including high unsigned IDs. The browser smoke checks the TIFF's label
hash against the audit and restores the exact baseline through undo. No upload,
server persistence or arbitrary tool execution is added. This is software integrity
validation, not proof of scientific correction or a formal parser security audit.


## Python AST security check

Bandit1.9.4 ran against the complete `src/` directory without rule suppression or
baseline waivers. Zero findings and zero scanner errors. Raw report:
`evaluation/checks/bandit.json`. The isolated security tool dependencies are pinned
in `security-tools.lock`; CI repeats the scan and dependency audit.

```bash
python3 -m venv .firecrawl/security-tools
.firecrawl/security-tools/bin/pip install -r security-tools.lock
.firecrawl/security-tools/bin/bandit -r src -f json -o evaluation/checks/bandit.json
```

This automated AST check is not an independent penetration test, parser fuzzing,
complete JavaScript analysis or proof that the application has no vulnerabilities.

## External masks and optional local models — October8

Label imports are restricted to10MB,1MP, one unsigned8/16/32-bit channel, oneIFD,
top-left orientation and uncompressed bounded tiles/strips. No automatic resampling,
remote input URL, user-supplied code or automatic correction is added. Processing
stays in tab memory; exports are explicit downloads. Source strings render as
React text and CSV rows contain numeric geometry and hexadecimal hashes.
Correspondence is bounded at10,000objects per mask,200,000intersecting pairs,
2,000differing components and three imported masks. Editing components with over
32total IDs is disabled. Exceeding current-mask comparison bounds preserves
measurements/hashes with an explicit unavailable-comparison statement.

Bundled actual-model masks are checked against pinned file and decoded-label
hashes and the source field's decoded input hash. Ordinary imports do not certify
model identity, source alignment or correctness. Inspected alternatives still pass
existing retained-object/overlapping-edit rejection, fresh-ID and undo checks.

The optional local neural runner uses a separate Python3.12 environment, canonical
validated input TIFFs, argument arrays and killable child process groups. A trusted
model package/official weight download is executable local software, not a sandbox.
No user-selected weights, public inference endpoint or credentials are accepted.
Output directories are ignored to avoid accidentally publishing private fields.
The full optional dependency audit is separate from main application audits; do
not interpret a green application CI as clearance of neural dependencies.

Optional-model audit remediation: the initial environment returned61advisory
records across Torch/Pillow/setuptools, including duplicate IDs. Upgraded to
Torch2.13.0+cpu/Pillow12.3.0/setuptools83.0.0; the separate pinned audit returns
no known records. CPU Torch is mapped to upstream2.13.0 for advisory lookup; its
binary artifact is not independently audited. Before/after reports are retained.

A separate Bandit scan of `scripts/run_model_masks.py` reports two low-severity
findings,B404/B603, for importing/using subprocess. They are retained without
suppressions in `evaluation/checks/model-runner-bandit.json`: execution is the
intentional trusted local interpreter/fixed-adapter boundary, uses argument arrays
with no shell, canonical bounded input and process-group deadlines. This does not
make arbitrary user-selected interpreters or downloaded code safe. CI's zero
`src/` findings must not be described as zero findings across every script. CI
also audits the separately pinned neural environment without installing models,
with explicit upstream Torch CPU-version normalization.

## External-mask alignment judgment — October 9

Dimensions and file/pixel hashes do not establish field identity or alignment.
Each loaded source now requires an explicit visual alignment acknowledgment before
component replacement, including bundled model examples. The overlay can return
to the full field. Acknowledgment records the current input hash, timestamp and
visual-user-judgment kind in exports and applied patches. Clearing the checkbox
blocks further replacements; it does not undo earlier confirmed edits. Removal or
field change clears the loaded acknowledgment. This is a user safeguard, not an
automated registration test or certification of correctness. A deliberately
misaligned reversed-pixel fixture tests blocking and cancellation; no person’s
ability to detect misalignment is measured. Parser fuzzing remains unperformed.
