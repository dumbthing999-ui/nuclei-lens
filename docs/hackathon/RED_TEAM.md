# Red team: 30 criticisms and current responses

October 8, 2026. Evidence concerns actual files and saved runs; accepted limitations remain open risks, not solved claims.

| # | Criticism | Engineering/evidence response | Current state |
|---:|---|---|---|
| 1 | This is an API wrapper. | Shared local numerical segmentation, sparse graphs, and worker inference; no inference API. | Implemented |
| 2 | Watershed and uncertainty review already exist. | Acknowledge prior art; claim original implementation/inspection workflow, not scientific first. | Limitation disclosed |
| 3 | Graph ranking is worse than a simpler method. | Compare equal budgets; select stronger object disagreement by validation; retain graph only as explanation. | Implemented |
| 4 | A learned model hides a weak result. | NNLS fails adoption gate, remains rejected and excluded from product. | Verified experiment |
| 5 | Correct totals hide opposing errors. | Real same-total graph witness; test fields with exactly correct totals still have unmatched instances. | Verified |
| 6 | Graph disagreement is presented as a diagnosis. | UI labels alternatives/hypotheses and requires human confirmation. | Implemented |
| 7 | Stable masks can still be wrong. | Explicit limitation and retained failure fields; no agreement-to-correctness claim. | Unsolved limitation |
| 8 | Annotation leakage inflates metrics. | Read labels only after inference; official manifests and frozen source/config hashes. | Implemented; auditable |
| 9 | Validation is being called held out. | Clearly mark validation as development data; report complete frozen test separately. | Corrected |
| 10 | Test-driven tuning invalidates the assessment. | Freeze before test access; interrupted process rerun unchanged; save all 50 records. | Verified hashes |
| 11 | Matching can prefer fewer high-IoU matches. | Cardinality-first Hungarian objective; focused tests. | Implemented |
| 12 | Unique mask colors are mistaken for instances. | Label connected equal-color regions according to dataset author's decoder. | Implemented |
| 13 | Ties are cherry-picked. | Expected capture within score ties; same budget for all methods. | Implemented |
| 14 | Random baseline is misleading. | Exact expected random capture; no best-seed selection. | Implemented |
| 15 | Count MAE alone is insufficient. | FP+FN, instance F1, full curves, and count MAE retained together. | Implemented |
| 16 | Oracle curves are fake human outcomes. | Label them secondary simulation; no time-savings/user-study claims. | Disclosed |
| 17 | Uncertainty range sounds calibrated. | Call it nine-run sensitivity range, explicitly not a confidence interval. | Implemented |
| 18 | Fixed tiles split cells. | Masks remain whole; centroid allocation documented; attribution can change near boundaries. | Implemented; limitation |
| 19 | Saturated or blank fields fail catastrophically. | Validation-guided saturation threshold safeguard and weak-signal withholding; retain old failures. | Improved, not guaranteed |
| 20 | Public examples are cherry-picked. | First two training fields plus lowest-F1 field among first eight; complete test results published. | Disclosed selection |
| 21 | Manual corrections silently alter scientific masks. | Separate reviewed count, original masks, explicit export semantics, undo. | Implemented |
| 22 | Rerunning destroys review work. | Preserve compatible same-input/configuration/baseline reviews; tests cover reset boundaries. | Implemented |
| 23 | Selecting a candidate is falsely called verification. | Candidate selection note says human confirmation still required. | Corrected |
| 24 | Browser runtime is too slow. | Immediate labeled reference example; measured cold/warm timings; worker/cancel/local companion. | Improved; cold latency remains |
| 25 | Image upload breaks privacy. | Browser worker processes bytes locally; tested network path; hosting metadata caveat. | Implemented, scoped proof |
| 26 | Malicious image exhausts resources. | File/pixel/frame bounds, header checks, worker watchdog; no parser fuzz guarantee. | Mitigated; residual risk |
| 27 | Native companion is publicly exploitable. | Loopback-only support, Host/Origin controls, two slots; killable90-second child processes with timeout/task-cancel tests. Public exposure unsupported; client disconnect may not cancel tasks. | Mitigated; residual risk |
| 28 | Dependencies contain known vulnerabilities. | Pillow upgraded, removed from browser; native/npm audit reports retained; repeat in CI. | Snapshot verified |
| 29 | Judges cannot reproduce results or use mobile. | Public samples, setup/benchmark scripts, actual browser review/export/mobile checks and per-image outputs. | Locally/public-path checked; CI pending |
| 30 | Presentation and impact are being self-awarded. | Separate AI judge roles with shared model/context, honest unchanged scores, no fake users/benefits. Reviewed video uploaded; processing/HD and anonymous opening-sample decode verified. | Quality gates remain open |

Every remaining limitation must stay visible in public copy. The graph contribution does not establish scientific superiority. Real reader-time/accuracy studies, independent-source generalization, physical-device/assistive-technology coverage and full browser-player viewing remain unfinished. Native process limits and real Chromium/Firefox workflows are implemented; these do not remove their documented limits.
