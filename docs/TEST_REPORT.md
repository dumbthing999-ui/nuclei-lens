# Test report

Updated October8,2026. Explicit mask editing is locally verified; production deployment and remote CI for that new feature remain pending.

| Check | Actual result | Evidence / scope |
|---|---|---|
| Python unit/integration suite |27 passed | `pytest`; core, graph, matching, decoding, bounded local API |
| Frontend unit suite |10 passed | `npm test --prefix frontend`; count validation, audit semantics, compatible review preservation, real equal-total witness conditions |
| Ruff | Passed | `ruff check src tests scripts` |
| TypeScript / Vite production build | Passed | `npm run build --prefix frontend` |
| Pinned native dependency audit |Zero known findings | `pip-audit --strict --no-deps -r requirements.lock`; JSON in `evaluation/checks/python-audit.json` |
| npm dependency audit |Zero known findings in saved snapshot | `evaluation/checks/npm-audit.json` |
| Public production browser path | Passed | `evaluation/checks/browser-smoke.json`; actual local count74, same-total inspection, confirm/undo/export, compatible reruns, no page exceptions |
| Mobile layout |No horizontal page overflow at390×844 | Chromium viewport emulation; not a physical-device test |
| Frozen scientific assessment |50/50 officialtest fields | MAE5.12, meanF1 0.827, selected object-queue capture45.8% at4/20 tiles; all failures retained |
| First remote CI | Failed at audit configuration | GitHub run37740678643: `--strict --skip-editable` rejects the editable local distribution. Scientific tests/Ruff passed; browser steps skipped. No vulnerability finding implied. |

## Audit correction

The release workflow now audits the complete pinned project dependency manifest with strict failure handling. It does not ask PyPI to identify the unpublished editable NucleiLens distribution. This retains all pinned transitive dependencies; no vulnerability is ignored or allowed. Remote run37743698558 passed all checks on commit ea0d558; PR1 was merged into main. The new mask feature requires its own subsequent run.

## Performance and network limits

The latest production Chromium observation was22,712 ms cold browser analysis and3,473 ms warm on this machine. These are single-run wall-clock observations, not population percentiles. Native test-set median analysis was3,454.62 ms under the recorded environment. Hosting injected a Cloudflare challenge POST; application image processing stayed in the worker. No promise of anonymous web use or zero hosting requests is made.

## Not yet verified

Remote CI and deployed browser checks for the new mask feature; physical mobile devices; Firefox/Safari; formal accessibility compliance; parser fuzzing; an independent security assessment; real reader-time/accuracy benefits; a separate backup production origin; rendered Devpost submission (authenticated draft readback passed); required video.

## Reproduce

```bash
.venv/bin/pytest
.venv/bin/ruff check src tests scripts
npm test --prefix frontend
npm run build --prefix frontend
.venv/bin/pip-audit --strict --no-deps -r requirements.lock
npm audit --prefix frontend --audit-level=moderate
NUCLEILENS_DEMO_URL=https://nuclei-lens.dumbthing999.chatgpt.site node frontend/tests/browser-smoke.mjs
```

## Second CI run

Run37741357081 passed the pinned dependency audit, Python/Ruff checks, npm audit/tests, shared engine sync, runtime preparation, and production build. Its development-server browser inference timed out. The local development path then passed with actual count74 (13,290ms cold;3,648ms warm). The next CI revision tests the production preview, records failure diagnostics, prevents reuse of stale checked-in pass artifacts, and makes a watchdog expiry visible as an error. Run37743698558 subsequently passed the production-preview workflow and was merged via PR1. The exact reason for the earlier Vite-development timeout was not isolated; local dev and production tests passed.


## Real mask-edit workflow — local production build

Bundled Playwright Chromium153 check passed: real training-field mask count
74→75→74, exported TIFF contains changed pixels, independently decoded uint32
labels match the audit SHA256, compatible cold/warm reruns preserve exact TIFF
bytes, and two undos restore the exact baseline pixel stream. Unit tests reject
retained-object conflicts, repeated/overlapping components, missing/invalid IDs,
wrong dimensions and expansion/count mismatches. Native lossless serialization
roundtrip is exact. Fixtures are software interaction evidence, not biological
correction or reader-study results. Latest CI-mode evidence is written separately
from checked-in public deployment evidence, preventing stale-pass reuse.


## Mask-feature clean-install CI repair

Run37745238514 passed scientific/frontend tests, both audits, runtime preparation
and notice collection, then TypeScript failed because the new test imports
`node:zlib`/`Buffer` and the package manifest lacked `@types/node`. Explicitly pin
that development dependency; verify with fresh `npm ci`, tests and build. This is
a dependency-declaration defect, not a segmentation or scientific-result change.
The feature is not released until its next actual remote run passes.


Automated axe-core4.14 WCAG A/AA checks passed in desktop, expanded-benchmark and
mobile viewport states. Incomplete checks are recorded for manual review; this is
not full accessibility compliance. Source protocol, all bundled label maps, local
Markdown links and tracked credential-pattern checks pass via
`python scripts/check_release.py`.
