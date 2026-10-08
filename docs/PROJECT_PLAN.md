# NucleiLens Project Plan

**Selected:** 2026-10-08. **State:** functional browser-local MVP and frozen 50-image test completed; release and submission verification in progress.

## Must Have

- Reproducible BBBC039 download, hashes, official splits, instance-mask decoding, and dataset attribution.
- Classical CPU nuclei segmentation baseline and deterministic sensitivity ensemble.
- Sparse object correspondence graph, count-changing region detection, and review ranking.
- Fair comparison to random review, pixel disagreement, and simple shape/size ranking; frozen test protocol.
- One workflow: sample/image → count and flagged regions → compare masks → human review/correction → audit export.
- Explicit sensitivity/uncertainty limits; unknown/stable-but-wrong failure examples.
- Responsive accessible interface, sample path, error states, clean setup, focused tests, and release checks.
- Public repository/live demo, evidence plots, README, Devpost copy, screenshots, <=4-minute video, verified final submission.

## Should Have

- Mask import for analysis independent of the built-in segmenter.
- A second dataset or segmenter for a clearly labeled external/generalization check, after provenance and overlap checks.
- Export of original and reviewed masks plus review decisions and parameters.
- Offline local use, downloadable demo package, and a rapid redeploy procedure.

## Could Have

- Batch review after single-field workflow is reliable.
- Browser-local analysis — promoted and implemented; actual cold/warm timings recorded.
- More segmentation methods after the main comparative result is frozen.

## Won't Have

- Chatbot, LLM inference, paid API dependence, clinical claims, patient-data workflows, accounts, team dashboards, 3D/whole-slide analysis, and automatic unreviewed corrections.

## Milestones

Dates are targets; completion requires evidence.

| Milestone | Target | Exit condition |
|---|---|---|
| M0 — Concept selected | Oct 8 | Decision, scoped contribution, prior art, and prototype acceptance criteria written |
| M1 — Architecture | Oct 8 | Components, interfaces, evaluation, and trust boundaries documented |
| M2 — Vertical slice | Oct 9 | Real image → masks → graph → flags → local demo; deterministic core tests |
| Early continue/pivot gate | Oct 10 | Validation ranking comparison shows useful benefit; otherwise change mechanism/pivot |
| M3 — Complete MVP | Oct 11 | Review/edit/export workflow works with sample and valid uploaded inputs |
| M4 — Evaluation | Oct 12 | Frozen method, untouched test evaluation, baseline comparison, all cases reported |
| M5 — UI polish | Oct 14 | Clear judge journey, responsive/keyboard-accessible controls, readable overlays |
| M6 — Reliability/security | Oct 15 | Focused security review, release checks, deployment and recovery verified |
| M8 — Demo/video | Oct 16–18 | Actual product footage, sourced claims, captions, 3:20–3:45 target |
| M9 — Submission candidate | Oct 18 | Three independent judge simulations, links/media/accounts checked |
| M7 — Feature freeze | Oct 19 | Stable production and evidence; only high-confidence fixes |
| M10 — Submission | Oct 20, early | Final fields/legal owner gates resolved, rendered entry and confirmation verified |

## First action and measurement gate

The first implementation priority is the offline graph/evaluation slice. Use validation data to test the fixed 20% review-budget target in [DECISIONS.md](DECISIONS.md). No marketing or broad product polish before that signal exists. Keep official test annotations out of inference and parameter tuning.

## Risks

- Graph superiority failed. The original contribution is the inspectable same-total opposing-component workflow; object disagreement is the measured default.
- Classical segmentation can be stably wrong; the audit cannot detect everything.
- A single U2OS experiment does not demonstrate generalization or clinical utility.
- Review-area/oracle comparisons do not measure actual human effort.
- Public repository and production origin exist. Source/CI release verification continues; Devpost draft is verified; video playback and final entry fields remain pending.

## Verified milestone update — October 8

M0/M1/M2/M3/M4 have working artifacts: concept/architecture, real image analysis, browser review/undo/export, and complete frozen test. The validation ranking gate rejected graph superiority and NNLS; object disagreement is the selected default and graphs explain competing objects. M5/M6 continue with accessibility, production parity, remote CI, and recovery verification. The owner released the M8 video hold; the reviewed215-second video and720p backup fully decode. Actual YouTube upload was rejected by the daily upload quota; a single local retry is scheduled for October9 at12:35PM IST. Devpost project content is saved; custom draft answers need the browser connection. No milestone implies official acceptance or a19+/20 score.

## October8 — owner-requested model QA scope

Implement one bounded extension of the same workflow: actual local Cellpose and
StarDist predictions → strict aligned label import → sparse correspondence
hypotheses → inspect/confirm → updated measurements/undo → hash-linked exports.
Both real training-field outputs and one-click precomputed examples are now
implemented. No browser neural weights, automatic consensus, batch platform,
new clinical claim or retuning of frozen assessment source is in scope.
Release gate:22frontend/41native tests, existing Chromium/Firefox paths, expanded
QA/browser/axe checks, frozen-source integrity, dependency audits and exact-head
remote CI. The optional model environment requires its own audit/limitations.
