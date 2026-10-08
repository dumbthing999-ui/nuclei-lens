# Test report

Updated October8,2026. These observations concern the verified tally-review build; guided mask editing is a next improvement, not an implemented claim.

| Check | Actual result | Evidence / scope |
|---|---|---|
| Python unit/integration suite |26 passed | `pytest`; core, graph, matching, decoding, bounded local API |
| Frontend unit suite |4 passed | `npm test --prefix frontend`; count validation, audit semantics, compatible review preservation, real equal-total witness conditions |
| Ruff | Passed | `ruff check src tests scripts` |
| TypeScript / Vite production build | Passed | `npm run build --prefix frontend` |
| Pinned native dependency audit |Zero known findings | `pip-audit --strict --no-deps -r requirements.lock`; JSON in `evaluation/checks/python-audit.json` |
| npm dependency audit |Zero known findings in saved snapshot | `evaluation/checks/npm-audit.json` |
| Public production browser path | Passed | `evaluation/checks/browser-smoke.json`; actual local count74, same-total inspection, confirm/undo/export, compatible reruns, no page exceptions |
| Mobile layout |No horizontal page overflow at390×844 | Chromium viewport emulation; not a physical-device test |
| Frozen scientific assessment |50/50 officialtest fields | MAE5.12, meanF1 0.827, selected object-queue capture45.8% at4/20 tiles; all failures retained |
| First remote CI | Failed at audit configuration | GitHub run37740678643: `--strict --skip-editable` rejects the editable local distribution. Scientific tests/Ruff passed; browser steps skipped. No vulnerability finding implied. |

## Audit correction

The release workflow now audits the complete pinned project dependency manifest with strict failure handling. It does not ask PyPI to identify the unpublished editable NucleiLens distribution. This retains all pinned transitive dependencies; no vulnerability is ignored or allowed. Rerun remote CI and record its actual status before tagging a release.

## Performance and network limits

The latest production Chromium observation was22,712 ms cold browser analysis and3,473 ms warm on this machine. These are single-run wall-clock observations, not population percentiles. Native test-set median analysis was3,454.62 ms under the recorded environment. Hosting injected a Cloudflare challenge POST; application image processing stayed in the worker. No promise of anonymous web use or zero hosting requests is made.

## Not yet verified

Remote CI after the audit fix; physical mobile devices; Firefox/Safari; formal accessibility compliance; parser fuzzing; an independent security assessment; real reader-time/accuracy benefits; guided mask correction; a separate backup production origin; authenticated Devpost draft/rendered submission; required video.

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

Run37741357081 passed the pinned dependency audit, Python/Ruff checks, npm audit/tests, shared engine sync, runtime preparation, and production build. Its development-server browser inference timed out. The local development path then passed with actual count74 (13,290ms cold;3,648ms warm). The next CI revision tests the production preview, records failure diagnostics, prevents reuse of stale checked-in pass artifacts, and makes a watchdog expiry visible as an error. CI remains failed until the next actual run proves otherwise.
