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
| Local API | Loopback-only documented; allowed Host; same-origin analysis; 2 slots acquired before body read; 5-second body timeout | `api.py`; tests for origin/host/body/type rejection |
| Injection / file paths | Raw bytes, no filename-derived file writes, URL fetch, HTML injection, shell/model actions, or database | Manual source review |
| Review input | Bounded whole-number counts; notes truncated; React escapes text | `review.ts`, Vitest |
| Secrets | Environment excluded from Git; no application API keys required | `.gitignore`, `.env.example`; pre-publication scan |
| Network | Scientific assets downloaded; application image processing stays in worker | Production browser workflow; network observations are scoped to tested path |

## Dependency findings

Initial native audit found known Pillow 12.2 advisories. Upgrading to 12.3 and rerunning the native audit produced zero known findings. The browser now uses GeoTIFF.js and browser bitmap decoding; its pinned scientific runtime contains no Pillow wheel. The installed npm dependency audit also returned zero known findings. Reports: `evaluation/checks/python-audit.json` and `npm-audit.json`. These are timestamped snapshots, not security guarantees.

## Remaining limitations

- Native CPU jobs execute in a thread pool without a killable subprocess deadline. Public exposure of the optional companion remains unsupported.
- Complex images can consume significant browser CPU/memory despite bounds. Cancelling terminates the worker; queued main-thread operations and library bugs remain possible.
- The browser and native PNG decoder have different precision semantics. Exact parity is verified for the bundled 16-bit TIFF, not every supported file encoding.
- No parser fuzzing, formal SAST security scan, independent penetration test, authentication audit, or regulatory compliance assessment has been performed.
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
