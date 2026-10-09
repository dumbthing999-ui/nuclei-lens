# Test report

Latest local QA:45native/22frontend tests pass; actual model outputs and QA
workflow verified. The saved V5 package directory lacks generated runtime assets;
metadata success/source-tree parity alone did not verify fresh live inference.
V6 now includes the full runtime and passed actual public browser inference/QA.
See `evaluation/checks/deployment-v6-browser.json` and `deployment-v6-mask-qa.json`.
Reviewed video is uploaded and attached to Devpost. HD processing and anonymous
opening-sample audio/video decode pass. Full player viewing and human-benefit
evidence remain outstanding. Historical V5 observations below retain their original scope.

## October 8 UX clarification follow-up

PR7 `fix/clarify-mask-tally-status` is merged. Accepted mask edits and
undo now announce both the resulting mask-instance count and the unchanged review
tally total. Frontend unit tests passed (10/10), TypeScript/Vite production build
passed, and the complete Chromium local-preview workflow passed split→merge,
export/hash, rerun, exact undo, cancellation, and the independent-tally message.
axe-core reported no violations in desktop, benchmark, additional-assessment, or
mobile-layout states. Exact-head CI passed, and the existing Site is now on V5.
The local browser and CI ran the same source tree that was packaged for V5; Site
deployment metadata reports success. No post-deploy browser session is claimed.
Current screenshots and machine-readable run reports are under `artifacts/screenshots/`
and `evaluation/checks/`.

The Sites packager accepted the generated `dist/` archive, including the existing
Site ID manifest and static entry point. Version5's deployment and current public
URL were read back from Sites; exact archive/source details are in
`evaluation/checks/deployment-v5.json`.

| Check | Actual result | Evidence / scope |
|---|---|---|
| Python unit/integration suite |33 passed on additional-assessment/reliability branch; v0.1.0 build27 | `pytest`; core, graph, matching, decoding, bounded local API |
| Frontend unit suite |10 passed | `npm test --prefix frontend`; count validation, audit semantics, compatible review preservation, real equal-total witness conditions |
| Ruff | Passed | `ruff check src tests scripts` |
| TypeScript / Vite production build | Passed | `npm run build --prefix frontend` |
| Pinned native dependency audit |Zero known findings | `pip-audit --strict --no-deps -r requirements.lock`; JSON in `evaluation/checks/python-audit.json` |
| npm dependency audit |Zero known findings in saved snapshot | `evaluation/checks/npm-audit.json` |
| Public V4 browser path | Passed before the V5 source update | `evaluation/checks/deployment-v4-browser.json`; production checks from the prior version |
| V5 source browser path | Passed on local preview and in PR8 CI; no post-deploy browser session claimed | `evaluation/checks/browser-smoke.json`; local count74, split→merge mask edits, undo/export/hash, reruns, cancel, and no page exceptions |
| V5 deployment | Sites API reports succeeded; current URL and saved version read back | `evaluation/checks/deployment-v5.json`; exact archive and source-tree match |
| Mobile layout |No horizontal page overflow at390×844 | Chromium viewport emulation; not a physical-device test |
| Frozen scientific assessment |50/50 officialtest fields | MAE5.12, meanF1 0.827, selected object-queue capture45.8% at4/20 tiles; all failures retained |
| First remote CI | Failed at audit configuration | GitHub run37740678643: `--strict --skip-editable` rejects the editable local distribution. Scientific tests/Ruff passed; browser steps skipped. No vulnerability finding implied. |

## Audit correction

The release workflow now audits the complete pinned project dependency manifest with strict failure handling. It does not ask PyPI to identify the unpublished editable NucleiLens distribution. This retains all pinned transitive dependencies; no vulnerability is ignored or allowed. Remote run37743698558 passed all checks on commit ea0d558; PR1 was merged into main. The new mask feature requires its own subsequent run.

## Performance and network limits

The prior V4 production Chromium observation was22,712 ms cold browser analysis and3,473 ms warm on this machine. The PR7 local-preview run recorded21,642 ms cold and5,901 ms warm. These are single-run wall-clock observations, not population percentiles. Native test-set median analysis was3,454.62 ms under the recorded environment. Hosting injected a Cloudflare challenge POST; application image processing stayed in the worker. No promise of anonymous web use or zero hosting requests is made.

## Not yet verified

physical mobile devices; Safari; formal accessibility compliance; parser fuzzing; an independent security assessment; real reader-time/accuracy benefits; a separate backup production origin; final EurekaDev submission (project API/public rendered readbacks passed); required video.

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


## Verified prototype release

CI37745742321 passed all checks; PR2 merged and v0.1.0 prerelease/tag points to
c4a73d7b7f36d322ad04a41ab531106475c7a684, with the exact verified CI tree.
ProductionV3 actual mask workflow passed,21,517ms cold/3,645ms warm on this machine.
Public automated axe checks passed desktop/benchmark/mobile.128 independent
proposals across the three declared demo fields apply/undo exactly;6 retained-object
conflicts are rejected. These are integrity results, not biological accuracy.

Devpost project API, fresh public rendered description,3 image IDs/captions, thumbnail
and both live/repository links are verified. update_project automatically published
the project; EurekaDev submitted_at remains null and no video is attached.


## Firefox production check

Playwright Firefox155.0 passed the actual publicV3 workflow on October8: baseline74,
mask74→75→74, independently decoded uint32 TIFF, audit SHA256, real local
inference/native-count parity, byte-identical edited TIFF after rerun, undo-history
clearance, and no horizontal overflow at390×844. No page exceptions were observed.
Evidence: `evaluation/checks/firefox-smoke.json`; reproduce with
`npx playwright install firefox` in `frontend/`, then
`NUCLEILENS_DEMO_URL=https://nuclei-lens.dumbthing999.chatgpt.site node frontend/tests/firefox-smoke.mjs`.
Cold elapsed29,360ms is one observation during concurrent native assessment,
not an isolated performance benchmark. This does not cover physical mobile or Safari.

Additional-protocol CI37748707090 passed on public commit
a242d74134919e408050444b1bf321c05c764069 before real BBBC038 evaluation.


## Additional assessment and process lifetime checks

All496 selected additional fields evaluated,0 structural reference/inference
failures; MAE6.54/F1.772, object capture45.7%, graph39.3%, random20%.
Source/selection hashes, complete manifest, count arithmetic and56,544 independent
cutoff/tie capture calculations passed. All37 low-F1 fields remain. Reference
imperfections and unknown biological-source independence are explicit limitations.

The optional API now runs a child process per admitted job with90-second deadline.
New tests start actual child processes, enforce a deadline and task cancellation,
and verify non-running exit state. An HTTP test checks504 and repeated capacity
release. Existing real API analysis and invalid-image422 tests pass. Full native
suite33 passed; frontend10 passed; Ruff/build pass. One test-client dependency
deprecation warning remains. Client disconnect alone need not cancel an ASGI task;
the hard compute deadline still bounds its lifetime. This is not an OS sandbox.

The updated local production browser check passes the real mask path and rendered
additional evidence. Automated axe checks cover desktop, original benchmark,
expanded additional-assessment and mobile states; no formal compliance claim.


## Public V4 release readback

Exact CI37751491341 passed every step, including additional-record integrity,
33 native/10 frontend tests, both audits, build and actual browser/axe workflow.
PR4 merged into maine7c60ad. SiteV4 source5fe9b8f0ad10feaa27c92875a52c01e9a4465018
deployed successfully; real public Chromium and Firefox mask/TIFF/hash/live/undo
checks passed. Four-state axe passed; actual public JSON equals the complete local
additional summary, and build-source identifies the verified GitHub tree.

Concurrent browser observations: Chromium69,700ms cold/12,780ms warm; Firefox
69,474ms cold. A subsequent sequential Chromium path passed at30,611ms cold/3,973ms
warm. All observations are retained; no isolated or population performance claim.
The plain urllib GET returned403; normal browser fetches pass. Health checks must
distinguish hosting bot/challenge behavior from the actual browser workflow.

Devpost authenticated readback and fresh rendered copy show additional results,
scope limitations, live/repo links and five distinct gallery images; new CDN
derivatives return200 and were inspected. EurekaDev submitted_at remains null,
video absent. Concurrent video-worker reports are not validated by this release.


Bandit1.9.4 Python security AST scan completed across all src files:0 findings,
0 scanner errors, no suppressions. Isolated tool versions are pinned separately
and its dependency audit is included in CI. This does not cover JS/TS static
security patterns, parser fuzzing or independent penetration testing.

## October8 — external-mask QA and real neural integration

- Native pytest:45passed (including8mock-adapter plumbing/validation/timeout tests).
- Frontend Vitest:19passed; TypeScript/Vite production build passed.
- Existing real Chromium workflow passed; Firefox155 mask/TIFF/hash/rerun/undo
  workflow passed on local production preview. These are desktop engines and
  resized layouts, not physical devices or assistive-technology certification.
- New QA browser check passed on local preview: actual sensitivity TIFF import,
  explicit inspection gate, opposing74→75→74edits, CSV/TIFF/report hash agreement,
  exact measurement undo, invalid geometry rejection, image-switch cleanup,
  desktop/mobile axe scans and no horizontal overflow.
- The same browser check loaded actual Cellpose and StarDist predictions, checked
  their file/label hashes, and verified68/68counts with differing segmentation,
  69correspondence components and3,738foreground-assignment differences.
- Actual optional CPU model execution completed on one CC0 training field;
  provenance records package/weight/input/output hashes and parameters. This is
  integration evidence, not held-out accuracy or observed user-benefit evidence.

See `evaluation/checks/mask-qa-browser.json`, the original browser/Firefox reports
and `frontend/public/model-examples/training-001/provenance.json`. New source is
not released until its exact remote CI and deployment state are verified.

The remediated optional environment also completed both actual models:68/68with
pixel-identical outputs to the initial run. Added3bundled-loader guard tests
bring the frontend total to22passed. Optional dependency audit now returns no
known records; prior findings and CPU-version mapping limits are retained.

Static-package regression check: packaging now requires complete runtime files,
pinned scientific-wheel hashes/sizes and exact built/source Python engine bytes.
An intentionally missing loader must be rejected before replacing existing dist.

Four static-package fixture tests passed: complete inputs copy; missing loader,
changed wheel and stale engine each reject before replacing the prior dist.
These tiny fixtures test packaging only, not inference. The complete regenerated
production package also passes real runtime/engine hash verification.

Final visual follow-up: clip imported-mask overlays to the inspected component's
bounded view rectangle, preventing neighboring pixels from rendering into SVG
letterboxing. Browser QA verifies clip geometry alongside actual edits/hashes.

## October9 — verified V6 delivery

PR10 merged after exact-head CI37824736213/37824726626 succeeded. Site V6 source
and GitHub release tree match; full runtime/model assets verified in the local
archive. Server canonical archive metadata has a distinct hash/size scope. Public
Chromium workflow passes actual count74inference, edits/undo/hash/rerun/cancel.
Public QA passes actual neural68/68comparison, measurements/CSV/TIFF/report,
import validation, field cleanup and desktop/mobile axe. Known same-origin
Cloudflare challenge POSTs are recorded separately; other writes fail QA. Route
classification does not inspect encrypted payloads or establish anonymity.

The first public QA run failed its final local-only no-write assumption after
all workflow actions, with no page errors; its report omitted request details.
That failed observation is retained. The revised check's public rerun passed,
with hosting traffic explicit. Devpost version9 copy/18tags/sixth photo and fresh
rendered/authenticated/image readbacks pass. Video remains quota-blocked.

## October 9 — Keyboard navigation and motion evidence

The keyboard-only Chromium local-preview check passed sample selection, native
select navigation, split/merge inspection, real74→75→74 mask edits, exact undo
and JSON/uint32 TIFF downloads with pixel/hash checks. All interactions in this
script use Tab/Shift+Tab/Enter/Space/arrow keys; DOM reads observe focus and values.
Sixteen focused targets were reached with visible computed3px outlines and no
page/console/request errors. It uses actual public sample masks, not biological
reference annotations or fake results. It does not trigger model inference.

A separate check passed the first-focus skip link into the workspace, keyboard
disclosure expansion/focus, and the actual busy spinner with reduced motion
requested. Automated axe checks still pass desktop/benchmark/additional/mobile
states.22frontend tests and the TypeScript/Vite build pass. CI runs these new
checks before release; production publication/readback is required separately.

```bash
NUCLEILENS_DEMO_URL=http://127.0.0.1:5174 node frontend/tests/keyboard-smoke.mjs
NUCLEILENS_DEMO_URL=http://127.0.0.1:5174 node frontend/tests/focus-motion.mjs
```

Reports: `evaluation/checks/keyboard-smoke.json`, `focus-motion.json`. Downloads
are regenerated locally and uploaded as CI artifacts. This does not establish
assistive-technology compatibility, physical mobile behavior, full accessibility
compliance, biological accuracy or measured human benefit.

### Keyboard release/public verification

PR13 final-head CI37969591623 and37969476854 both passed, including new keyboard
and motion checks. PublicV7 source/tree exactly matches GitHub-main22b3b15.
Actual public core workflow, model QA and skip/disclosure/reduced-motion checks
pass; all11 archive loader/wheel hashes were independently verified. Reports are
`deployment-v7-browser.json`, `deployment-v7-mask-qa.json`, `deployment-v7-focus-motion.json`
and `static-package-v7.json`. Full keyboard edit/undo/export ran locally and in CI;
only the focus/navigation/motion subset is independently checked on production.

## Alignment safeguard — local checked candidate

TypeScript/Vite build and22frontend tests passed. Updated actual Chromium QA
workflow passes matching-field and deliberately misaligned same-size gate checks,
checkbox cancellation with unchanged reviewed pixels/history, audited input-bound
judgment, opposing74→75→74edits, exact undo, CSV/TIFF/hash/QA and axe/mobile.
The reversed-pixel fixture is a test construction, not biological reference data.
See mask-qa-browser.json for the local target; V7 public results are separately
preserved. This candidate is not live until CI/merge/deployment readback pass.

## V8 production verification

Both PR14 final-head remote CI37971886672/37971812034passed. Public source/tree
and saved-version/archive readbacks agree at deployment. All11scientific runtime
files in the actual archive pass length/hash checks. Actual public Chromium
inference/count74, edits/undo/TIFF/hash/rerun/cancel/mobile, external/model QA
including matching/misaligned acknowledgment/cancellation/audit, measurements/CSV,
axe/mobile, skip/disclosurefocus/reducedmotion pass. Full keyboard-only edit/export
remains local+CI evidence. No assistive-tech/physical-device/full-video-player or
human-benefit validation. See deployment-v8*.json; subsequent docs do not change
the deployed application source.
