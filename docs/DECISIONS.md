# Decisions

## 2026-10-08 — Select NucleiLens for implementation

**Decision:** Build a microscopy counting review tool in the Coding Track. Working name: **NucleiLens**. Tagline: **See the mistakes behind the count.** Intended category: Biology/Medical and Environmental Science.

**One sentence:** NucleiLens helps biology students and researchers inspect likely nuclei-counting mistakes by showing where segmentation variations merge, split, or lose objects and prioritizing those regions for human review.

### Why this candidate

The official BBBC039v1 record provides 200 image fields, approximately 23,000 manually annotated nuclei, a CC0 license, and official partition metadata. This gives a bounded, inspectable evaluation path without proprietary data, participant recruitment, or paid inference. The paper associated with the dataset explicitly distinguishes merge/split error modes and warns that pixel overlap alone does not adequately capture relevant instance errors. Sources: [BBBC039](https://bbbc.broadinstitute.org/BBBC039), [Caicedo et al. 2019](https://onlinelibrary.wiley.com/doi/full/10.1002/cyto.a.23863).

The October 8 gallery refresh still displayed 37 entries. No microscopy count-review pitch was visible in the captured listings. This is thematic differentiation, not proof that every competitor's implementation has been inspected.

### What changed after the earlier rejection

The generic uncertainty-dashboard formulation remains rejected. Existing work already covers segmentation uncertainty, count intervals, and uncertainty-guided review. The selected implementation is narrower: represent object correspondence across controlled segmentation variations as a graph; distinguish count-changing events from boundary-only disagreement; and provide a review queue with local alternative segmentations and auditable user corrections.

The proposed technical insight is that a counting review queue should prioritize changes in **object cardinality**, whereas a pixel uncertainty map may also emphasize uncertain boundaries that leave the count unchanged. This is an engineering hypothesis to test, not a claim that uncertainty, graph matching, or topology analysis was invented here. Existing structure-aware uncertainty work is an explicit comparator/prior-art risk. The contribution will be our original implementation and its measured usefulness on this bounded task; no scientific-first claim is authorized.

### Alternatives rejected

- Heat/cooling allocation: substantial direct overlap with City-HEAT, cooling-center allocation workflows, and WRI Cool Cities Lab; no validated local planning partner or operational constraint that justifies a new workflow.
- Power-restoration simulator: high estimated presentation/impact potential, but no verified realistic topology, repair data, or utility validation. Its initial score assumed evidence we do not possess.
- Water-leak localization: accessible benchmarks may support it, but the acoustic proposal's real sensor data and localization assumptions were unverified; existing detection/localization literature is extensive.
- Evacuation simulator: direct gallery overlap with flood/emergency tools and major capacity/safety validation issues.

### Concept gates (design review, not release approval)

| Gate | Basis for proceeding | Limitation / required verification |
|---|---|---|
| A — One sentence | Specific user, count-review problem, and visual mechanism | Validate wording with a nontechnical reader |
| B — Technical insight | Object-correspondence graph detects local count disagreement and suppresses count-neutral boundary jitter | Prior methods exist; establish comparative value, make no global novelty claim |
| C — Measurable proof | Annotated instances allow event recall, count MAE, and equal-budget review comparison | No measurements have been run |
| D — Killer demo | Show a real field, inspect a merge/split ambiguity, review it, and see the count update | Select a legitimate validation example after running the method; label ground-truth reveal |
| E — Important problem | Dataset-associated research documents nucleus instance errors and evaluation shortcomings | No clinical benefit, user adoption, or labor savings established |
| F — Feasible | Bounded 2D images, classical CPU baseline, downloadable benchmark | Actual latency and error detection must be measured immediately |
| G — Reliable | Locally executable analysis, bundled samples, no paid model/API dependency | Deployment hosting remains to be configured |
| H — Ethical | Public cell-line images; research/education review support | No diagnosis, treatment, autonomous correction, or correctness guarantee |

### First prototype acceptance gate

Tune on official training/validation partitions only. Before a product build expands, compare topology-based ranking against random review, pixel disagreement, and simple object-size/shape flags using the same nonoverlapping review units and budget. At the predeclared 20% review budget, target at least 1.5× random count-error capture and a 10 percentage-point advantage over pixel disagreement. These are **targets**, not results. Report the entire risk/review curve and failure cases, including stable-but-wrong outputs.

If the method gives no useful advantage on validation data by October 10, change the mechanism or pivot before building polish. The untouched official test split is reserved for the frozen comparison. Simulated oracle correction estimates are clearly labeled and do not establish real human review speed or outcomes.

**Consequence:** Stop broad ideation and build the graph/evaluation vertical slice first. Keep judge scores unassigned until implementation and evidence exist. This selects the project direction; it does not approve a final submission or establish a 19+/20 score.


## 2026-10-08 — Separate explanation, ordering, tally and mask decisions

**Evidence:** Graph and NNLS ordering failed validation gates. Frozen50-field test
confirmed object disagreement's stronger error concentration. Three AI judge
critiques found tally-only editing limited practical value.

**Decision:** Retain object disagreement as default; use graphs to expose opposing
local hypotheses. Add explicit source-mask component replacement, strict overlap
conflicts, undo and lossless TIFF/audit exports. Keep tally entries separate.
No automatic correctness or reader-benefit claim. Inference and frozen scientific
evaluation remain unchanged. Alternatives: tally-only (limited actionability),
freehand editor (larger unvalidated scope), automatic correction (unsupported).

**Consequences:** Actual real-field browser workflow74→75→74, pixel/hash readback,
rerun preservation and exact undo pass locally. New feature needs remote CI and
production readback before release. Human study/external dataset remain future
evidence, not implied completed work.

Devpost fresh credentials authenticated successfully; prior account listing showed
no EurekaDev project. Fresh draft1470185/submission1224432 was created and read
back; no final submission. The required video remains owner-held.


## October8 — freeze and retain complete additional assessment

Decision: keep the original configuration and object-disagreement default after
all496 preselected BBBC038 fields were evaluated. No post-result exclusions or
retuning. Evidence: MAE6.54/F1.772; object capture45.7%, graph39.3%, random20%.
Alternative: promote a new comparator, repair visually sparse reference masks, or
exclude hard fields. Rejected because it would contaminate the assessment and
misrepresent scope.43 potential same-size overlaps were excluded before evaluation;
related source groups may remain. Retain37 fields below F1 0.5 and original labels.
Consequence: present bounded additional-image evidence, not universal validity or
human benefit. Add actual public Firefox verification and an explicit unsaved-review
notice; neither changes inference. Required video remains owner-held.


## October 8 — completed-video publication and judge entry clarity

The owner explicitly released the earlier video hold and requested upload, a PR,
and completed Devpost fields. Preserve the original completed master and correct
unsupported presentation claims in a separate reviewed version before upload.
Use the real audit schema, smaller-area overlap definition, native timing labels,
and bounded research/education claims. See `docs/hackathon/video-review.md`.

Composio provides working GitHub authentication and repository push permission;
local git/gh authentication alone was insufficient evidence to declare the account
blocked. PR9 is open and its initial exact commit passed Actions. YouTube is
connected; channel reads return HTTP403 quotaExceeded and an actual upload returned
HTTP429 rateLimitExceeded for Video Uploads per day. A guarded single local retry
is scheduled after reset, October9 at12:35PM IST; uncertain/successful outcomes
must not be repeated. Public playback remains unverified. The owner authorized
use of the connected Devpost account email
for organizer contact; keep the value out of public files. The available MCP has
no separate draft-answer writer, so do not submit simply to save draft answers.

Update the public Devpost tagline to explain microscopy and the concrete review
workflow while retaining “See beyond the count.” Synchronize the actual technology
stack and place the live demo first in project links. The API uses the first link
as the entry website; authenticated readback confirms the demo URL is primary.
This improves judge understanding without changing scientific claims or scores.

The corrected215-second upload master and720p backup fully decode. Captions,
audio measurements, exact hashes and review corrections are recorded separately
from the original preserved owner video. Timers/metadata/media checks do not
establish an upload, submission or higher judge score.

## October8 — established-model QA, measured masks and equal-count evidence

Decision: add an optional local CPU Cellpose3/StarDist runner, strict external
TIFF comparison, explicit component confirmation and exact per-mask measurements.
Keep the frozen classical inference/graph/evaluator unchanged. Alternatives were
claiming consensus as novel, adding automatic correction, or integrating giant
neural dependencies into the browser; each weakens honesty, reliability or size.

Primary literature establishes consensus/model combination as prior art. The
observed training001 run returned68instances from each model, with3,738foreground
assignment differences and69differing correspondence components. This validates
integration and an equal-count demonstration, not accuracy or69biological errors.
The real output masks and provenance are bundled; weights remain outside Git.
The complete observed optional environment is pinned separately. Main application
and neural dependency audit results must remain separate.

Measurement exports describe pixels and exposed grid edges; no physical size,
intensity, clinical diagnosis or measured human benefit is inferred. External
components exceeding32total IDs remain inspect/export only. Bounded pagination,
strict uncompressed TIFF parsing and inspected-before-confirmed edits keep the
workflow manageable. Existing mask conflict checks/undo remain authoritative.
Unit adapter mocks are labeled separately from the actual model run.

PR9 is merged with both exact-head CI runs green. Browser-dependent Devpost custom
fields were deferred by the owner; the actual YouTube upload remains quota-rejected
with a single guarded next-reset retry. No final submission is claimed.

## October8 — reject incomplete static inference packages

Observed the saved V5 local build directory lacks `runtime/pyodide/`, although the
worker imports it. Vite success alone cannot prove a fresh deployment can infer.
Strengthen `copy_site_dist.mjs` to require runtime loader/WASM/stdlib/lock files,
verify every pinned scientific wheel's bytes/SHA256, and match built Python engine
files to source before replacing root dist. Include the verified generated runtime
in the next Site package; preserve exact source/build provenance. This observation
concerns saved packaging artifacts, not an invented production browser test.
