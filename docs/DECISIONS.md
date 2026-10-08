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
