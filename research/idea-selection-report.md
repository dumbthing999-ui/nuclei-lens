# EurekaDev Idea Tournament

**Initial research snapshot:** 2026-10-07. **Decision update, 2026-10-08: NucleiLens selected for implementation**, as a narrowed version of candidate #25. See the selection below and [DECISIONS.md](../docs/DECISIONS.md). The refreshed public gallery still displays 37 listings; detail coverage remains 10 reviewed/27 listing-only. Scores below are initial screening estimates, not judge feedback or measured project results.

## Scoring method

Each dimension is scored 0–10. Weighted total = 20% Innovation + 20% Impact + 20% Execution potential + 20% Presentation + 5% gallery differentiation + 5% reproducible evidence + 5% feasibility + 5% demo reliability. These are selection estimates only. Unknowns are reflected as lower scores; scores do not establish that a hard gate passes.

## Candidate set (25 distinct problem/mechanism pairs)

| # | Concept; user/problem | Mechanism and proof/demo | Data/evidence and principal risk | I | Im | Ex | Pr | Diff | Proof | Feas | Rel | Total |
|---:|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | **Microscopy count stress test** for biology learners: image degradation can make automated counts drift without an obvious visual failure. | Apply controlled blur, noise, and intensity shifts to a field; measure count drift and identify degradation thresholds; compare against a fixed-threshold baseline with a degradation sweep demo. | BBBC039 candidate; robustness testing is established and baseline segmenters exist, so a new useful stress-test protocol must be justified. | 7 | 6 | 8 | 9 | 8 | 9 | 8 | 8 | **7.65** |
| 2 | **Wheelchair data confidence auditor** for local mappers: route tools may overstate safety when access tags are missing. | Score route evidence completeness, distinguish unknown from inaccessible, propose targeted mapping audits; evaluate tag completeness on a sampled district. | OSM tag coverage and local usefulness uncertain; routing/audit tools already exist. | 6 | 8 | 7 | 8 | 6 | 6 | 7 | 6 | 7.05 |
| 3 | **Heat-plan resource allocator** for municipal planners: fixed cooling resources must cover vulnerable areas. | Robust optimization under uncertain population/heat inputs; compare coverage/fairness to nearest-site baseline in a scenario simulator. | IMD and WorldPop have caveats; toy allocation can look impactful without operational validation. | 7 | 9 | 8 | 9 | 7 | 7 | 7 | 7 | 8.00 |
| 4 | **Food-tray waste estimator** for school kitchens: kitchens need meal-specific waste signals. | Image segmentation before/after serving estimates edible leftovers by category; evaluate against weighed samples. | Requires new local consented data and consistent plates; privacy and domain shift. | 6 | 7 | 7 | 8 | 5 | 5 | 5 | 6 | 6.65 |
| 5 | **Water-network leak localizer** for utilities: acoustic leak search is costly. | Time-delay correlation across synthetic/real sensor arrays; compare localization error to single-sensor baseline in an interactive pipe simulator. | Real data access and physics assumptions are major risks; synthetic-only impact limited. | 8 | 8 | 8 | 9 | 8 | 6 | 6 | 7 | 7.95 |
| 6 | **Solar output fault explainer** for small solar operators: underperformance is hard to attribute. | Residual decomposition against weather-normalized output, classify likely fault signatures; evaluate on public PV time series. | Public dataset provenance/weather alignment and fault labels uncertain. | 6 | 7 | 8 | 8 | 6 | 7 | 7 | 7 | 7.15 |
| 7 | **School-bus stop fairness optimizer** for districts: stop placement trades walking burden against capacity. | Capacitated facility-location optimization with walk-distance and equity constraints; compare against current/greedy routes. | No verified local stop/population dataset; simulated demand weakens impact. | 7 | 8 | 8 | 9 | 7 | 6 | 6 | 7 | 7.70 |
| 8 | **Wildfire smoke classroom scheduler** for schools: outdoor activity decisions need local exposure context. | Fuse public air-quality forecast with school schedule and indoor/outdoor exposure scenarios; evaluate forecast error and policy tradeoffs. | Overlaps public AQI products; no sensor validation and health-safety claim risk. | 5 | 8 | 7 | 8 | 4 | 6 | 7 | 6 | 6.75 |
| 9 | **Sign-language lesson latency coach** for learners: feedback timing can block practice. | On-device hand-pose temporal alignment against a small signed phrase grammar; measure recognition and latency with consented recordings. | Dataset diversity, linguistic validity, and participant data requirements are substantial. | 7 | 8 | 6 | 9 | 7 | 5 | 4 | 5 | 7.05 |
| 10 | **Curb-ramp audit prioritizer** for civic mappers: limited survey time must capture high-value missing accessibility data. | Expected-information-gain ranking from OSM gaps and route centrality; compare coverage gain to random survey points. | Same OSM coverage/novelty risks; local field validation needed. | 7 | 8 | 7 | 8 | 7 | 6 | 6 | 6 | 7.25 |
| 11 | **Cold-chain excursion detector** for food banks: temperature excursions threaten donated food. | Change-point detection and remaining-safe-window estimates from logged temperatures; compare detection delay/false alarms to fixed thresholds. | Need public labeled traces or own sensor collection; safe window claims need domain authority. | 7 | 8 | 8 | 8 | 7 | 6 | 7 | 7 | 7.55 |
| 12 | **River gauge anomaly forecaster** for community monitors: broken sensors can masquerade as hazards. | Physics-informed plausibility checks on public water-level series; measure anomaly precision and lead time against seasonal/threshold baselines. | Find stable, licensed station data and labels; similar flood tools in gallery. | 6 | 8 | 7 | 8 | 5 | 6 | 6 | 6 | 6.95 |
| 13 | **Medication label accessibility verifier** for low-vision patients: OCR errors can alter instructions. | OCR with layout/consistency checks and explicit abstention; benchmark character/field error on public package images. | High-stakes use, language/domain variation, and medical reliance risk. | 7 | 9 | 7 | 8 | 7 | 7 | 6 | 6 | 7.50 |
| 14 | **Power outage restoration simulator** for community coordinators: restoration order affects essential services. | Graph optimization prioritizes critical loads under repair crew constraints; compare service restoration time to simple priority rules. | Grid topology and outage data access; simulation assumptions can overclaim. | 8 | 9 | 8 | 9 | 8 | 6 | 6 | 7 | 8.15 |
| 15 | **Public-space noise source mapper** for residents: aggregate noise masks actionable sources. | Mobile audio event classification plus privacy-preserving on-device aggregation; evaluate event F1 on public audio dataset. | Audio privacy, local domain shift, and source attribution uncertainty. | 7 | 7 | 7 | 8 | 7 | 7 | 6 | 6 | 7.10 |
| 16 | **Library demand-aware book transfer** for library networks: stock is unevenly distributed. | Inventory graph flow with travel/circulation costs; compare fulfilled requests against greedy transfers. | Public circulation/inventory data rarely available; synthetic user benefit. | 6 | 6 | 8 | 8 | 5 | 5 | 8 | 8 | 6.90 |
| 17 | **Flood evacuation bottleneck simulator** for planners: route capacity collapses under uncertain closures. | Dynamic graph flow with staged closures and shelter capacity; compare clearance time to shortest-path baseline. | Existing flood projects in gallery; evacuation modeling assumptions and safety implications. | 7 | 9 | 8 | 9 | 6 | 7 | 6 | 7 | 7.90 |
| 18 | **Microplastic sample image counter** for community labs: manual particle counting is slow and inconsistent. | Image processing separates fibers/particles and reports uncertainty; compare count and size error to labeled microscopy images. | Need suitable open annotated data and expert definition; image domain variability. | 7 | 8 | 7 | 9 | 8 | 6 | 6 | 7 | 7.55 |
| 19 | **Accessible chart sonifier** for blind students: static charts hide trends. | Extract chart geometry and encode shape as navigable audio/tactile cues; measure value recovery and task time against screen-reader baseline. | Need participant testing and chart corpus; chart extraction tools exist. | 8 | 8 | 7 | 9 | 8 | 6 | 6 | 6 | 7.70 |
| 20 | **Local-language emergency bulletin consistency checker** for responders: translations can alter critical details. | Constrained alignment checks for numbers, place names, negation, and time; evaluate error detection on parallel public bulletins. | Translation overlaps gallery NewsBridge; false confidence risk. | 6 | 8 | 8 | 8 | 5 | 7 | 7 | 7 | 7.30 |
| 21 | **Public procurement anomaly network** for watchdogs: related awards may evade single-record review. | Entity resolution + graph outlier ranking with explainable links; evaluate on adjudicated public cases. | Reliable ground truth is difficult; defamatory false positives and legal risk. | 8 | 8 | 8 | 9 | 8 | 4 | 5 | 5 | 7.70 |
| 22 | **Classroom air-ventilation experiment kit** for teachers: CO₂ readings need interpretable experiments. | Fit room response dynamics from sensor traces and compare ventilation interventions; measure parameter recovery on controlled trials. | Requires sensor hardware/experiments; CO₂ is not a direct infection-risk measure. | 7 | 8 | 8 | 9 | 7 | 7 | 6 | 7 | 7.75 |
| 23 | **Crop irrigation leak and stress distinction** for small farms: low soil moisture has multiple causes. | Fuse soil sensor, weather, and plant image features to distinguish leak/stress hypotheses; compare decision error to single-sensor threshold. | Field collection, crop specificity, and sensor calibration. | 8 | 8 | 7 | 9 | 8 | 5 | 4 | 5 | 7.50 |
| 24 | **Community map data-change impact simulator** for OSM contributors: edits can silently break critical routes. | Graph-diff identifies disconnected essential destinations and explains edge changes; evaluate against seeded edit regressions. | Novel workflow unclear and seeded cases may not predict actual harm. | 7 | 7 | 8 | 8 | 7 | 6 | 8 | 8 | 7.45 |
| 25 | **Lab image segmentation reliability audit** for microscopy users: average accuracy hides which images need manual review. | Calibrate object-level instability and estimate risk-versus-review coverage; compare stability score, model confidence, and random review on held-out annotated images; show count plus review-priority map. | BBBC039 and existing uncertainty-aware segmentation papers; novelty requires demonstrating that actionable review prioritization adds value beyond existing uncertainty outputs. | 8 | 6 | 8 | 9 | 8 | 9 | 8 | 8 | **7.85** |

## Initial top five: adversarial review — October 7

### 1. Lab image segmentation reliability audit (candidate, not locked)

1. **Why it could win:** An immediately legible visual: a convincing segmentation overlay beside a handful of highlighted unstable nuclei, with a review-priority control that trades human review effort against measured count error. Offline, reproducible, and anchored in expert-annotated images.
2. **Why it could lose:** Nuclear segmentation is mature; uncertainty-aware segmentation and active learning have prior research. If the contribution is only “run several perturbations and show disagreement,” judges may see a thin wrapper around standard methods.
3. **Is it new?** Not established. Research explicitly includes uncertainty-aware contour proposals, and the gallery/site research has not proven the exact review workflow absent elsewhere. Novelty is currently a hard-gate risk.
4. **Can impact be proved?** Technical value can be tested with held-out masks and risk-coverage curves. Real-world labor/time savings cannot be claimed without a user study.
5. **Is depth visible?** Yes, if the implementation includes instance matching, perturbation-consistency analysis, calibration, risk-coverage, and a fair comparator—not only a visualization.
6. **Demoable/reliable?** Yes using fixed bundled sample images and offline CPU inference, subject to measured runtime and weight/license checks.
7. **MVP reliability?** Plausible: one dataset, one baseline segmenter, fixed evaluation, no external service.
8. **Instant insight?** “It shows which count results deserve a human check” is understandable; the uncertainty map can show it within seconds.
9. **Better than gallery?** It is visibly different from the observed application themes, but no exhaustive claim: 27 gallery projects received listing-only review.
10. **Unforgettable moment?** Flip from all objects counted equally to a ranked set of uncertain objects, then show whether reviewing the top fraction captures more actual count errors than random review.

**Hard-gate status:** A, D, F, G, H appear feasible; B (technical novelty), C (outcome definition), and E (problem impact evidence) need more validation. Dataset licence/split and a comparator must be verified. Do not lock unless the audit adds a useful, nonredundant decision workflow and demonstrates that its uncertainty signal predicts held-out errors.

### 2. Heat-plan resource allocator

Could win on social relevance and simulation clarity. It may lose as a generic dashboard/optimization demo; an allocation optimum on modeled population does not establish heat outcomes. Novelty is in robust/fair allocation under missing and uncertain inputs, but needs a defensible baseline and local validation. Killer demo could show the preferred cooling-site plan change when population uncertainty rises. Data rights and spatial resolution remain risks. It is not a clinical or heat-warning product.

### 3. Power outage restoration simulator

Strong visual graph/scheduling story and substantial optimization. But the actual grid topology/outage records may be unavailable; synthetic network results are not impact proof. Existing outage restoration research is mature. A safe educational simulator with transparent assumptions could work, but a real-world claim needs authorized data and engineering validation.

### 4. Water-network leak localizer

Clear technical signal-processing insight and compelling animated localization. Risk: realistic pipe acoustics, sensor placement, and labeled leak data are hard; a simulator can make the answer look correct by construction. It passes only if an open dataset or independently validated physical model supports a meaningful baseline.

### 5. Flood evacuation bottleneck simulator

Compelling dynamic-network visualization and clear clearance-time metric. It risks duplicating the gallery's FloodSense and hiding weak assumptions behind a simulator. A credible version needs public, licensed road/shelter/capacity inputs and must compare scenarios to shortest-path and capacity-aware baselines; no route should be represented as a safe real evacuation instruction.

## Historical provisional recommendation — October 7

**Do not declare a winner yet.** Candidate #25 is not the highest raw weighted score, but has the best presently evidenced combination of bounded reproducible evaluation, offline demo feasibility, public benchmark availability, and separation from the gallery themes inspected. It does **not yet pass the technical novelty gate**. Existing nuclei segmentation and uncertainty research directly threaten a generic formulation. Next research must look for the exact uncertainty-to-human-review comparison and verify the BBBC039 licensing/split. If no genuinely differentiated contribution survives, reject it and return to the next candidate rather than force-locking it.

Potential distinct contribution to test (not a claim of novelty): **count-level reliability calibration under realistic image degradation**, where a user gets an explicit review budget and the system selects fields/objects to inspect to keep total-count error within a declared tolerance. Compare stability ranking against model confidence, image-quality-only ranking, and random review at equal review budgets. A model that is wrong but stable is a critical failure case. Establish this on untouched official test data; never tune on test data.

## Evidence requirements recorded on October 7

- Verify official BBBC039 download, license, annotation semantics, and split manifest; pin dataset/version and hashes.
- Search papers/patents/tools for perturbation stability used specifically for review-budget/count-error control; compare uncertainty methods and existing QuPath/Fiji workflows.
- Run an initial reproducible baseline before product build: count MAE, instance detection precision/recall, calibration/risk-coverage, and runtime, with train/validation/test leakage controls.
- Validate the intended user and workflow with public literature or consented, truthful interviews; do not invent user research.
- Re-crawl EurekaDev and review any new relevant submissions.
- Revisit all eight hard gates. If the candidate still cannot justify a novel mechanism and credible beneficiary, pivot.

## Selection — October 8: NucleiLens

**Selected direction:** NucleiLens helps biology students and researchers inspect likely nuclei-counting mistakes by showing where segmentation variations merge, split, or lose objects and prioritizing those regions for human review.

**Track/category:** Coding / Biology/Medical and Environmental Science.

**Specific technical contribution to implement and test:** Sparse local object correspondence graphs across sensitivity runs separate count-changing ambiguities from boundary-only disagreement. The review interface shows competing local masks and preserves an audit trail of human corrections. Performance will be compared to pixel disagreement, random review, and size/shape flags at an equal review budget.

The selection does not revive the rejected generic uncertainty dashboard. Existing count-uncertainty and structure-aware uncertainty methods remain prior art. We will claim an original application/implementation and measured task-level value only to the extent supported; we do not claim to invent uncertainty, segmentation, graph matching, or topology analysis.

**Evidence gained:** The official BBBC039 page was re-read and independently scraped on October 8; it documents CC0, instance annotations, and official split metadata. The associated Caicedo study specifically analyzes merge/split errors and limits of pixel-overlap metrics. Public overview/rules/resources/updates/discussions and both gallery pages were refreshed before this decision; no new public announcements or discussion topics were visible.

**Why it beat the other finalists:** Power restoration, leak localization, and evacuation had higher initial estimates on some dimensions but unresolved realism/data/operational validation. Heat allocation has direct mature tool overlap. NucleiLens has a compact legitimate dataset, local execution, observable error types, a comparative experiment, and a short visual explanation. This is an evidence-based choice among feasible implementations, not a prediction of placement.

**Winning thesis:** A judge can watch an apparently plausible count fail at a merged or split region, inspect why the count is ambiguous, review it, and then inspect held-out evidence for whether our queue finds such errors more efficiently than simpler methods. Technical proof must support that story before it is used in submission copy.

**Continue/pivot gate:** By October 10, test the predeclared validation protocol and targets in [DECISIONS.md](../docs/DECISIONS.md). If the selected graph mechanism adds no practical value, change it or pivot early. No project benchmark or 19+/20 score has been achieved or is claimed.
