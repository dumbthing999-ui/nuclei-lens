# Retrospective 19-factor concept screening — October 10, 2026

Assessment status: **subjective potential estimates**, made after NucleiLens exists. This is not the original October 7 prebuild scoring, official judging, actual experimental outcomes, a prediction of placement, or proof that any hard gate passes. The existing 25 concepts and their IDs are preserved; no new concept or reused project code is proposed. The original report remains unchanged.

## Formula declared before scores

Let I, Im, Ex and Pr be potential Innovation & Creativity, Impact & Relevance, Execution & Technical Quality, and Presentation & Communication, respectively, each scored 0–10. Each contributes 20% of this screening total. These names follow the official criteria recorded in source S2; **the strategic extension is our screening rubric, not the official judging formula**.

The 15 strategic factors collectively contribute 20%, each with weight 20%/15 = 1/75. The first 13 are positive, with higher scores better. The last two are raw costs: `failure_risk` and `paid_api_dependence` each run from 0 (low) to 10 (high), and contribute `10 - raw_score`.

```text
S = gallery_originality + wow + feasibility_before_Oct19
  + real_data_availability + measurable_results + visual_demo
  + robustness + technical_depth + social_relevance
  + judge_understandability + reproducibility + live_demo_reliability
  + explain_under_30_seconds + (10 - failure_risk) + (10 - paid_api_dependence)
T_0_10 = 0.20*(I + Im + Ex + Pr) + S/75
       = (15*(I + Im + Ex + Pr) + S)/75
```

All 19 inputs are integers on 0–10. The range of T is 0–10. Exact rational totals determine ranking, never rounded displays. Equal exact totals share competition rank; concept ID ascending breaks display order only. A perfect risk score contribution requires raw risk 0. No conversion into a new /20 judge score is made.

## Evidence and estimation boundaries

Inputs were read locally from [original report](idea-selection-report.md), [numbered sources](SOURCES.md), [41-row current competitor matrix](competitors/competitor-matrix.csv), and [recorded judge simulations](../docs/hackathon/JUDGE_SCORECARD.md), at audit checkout HEAD `2f39f2669b8dde9bcf358fb223dae58796e274c8`. The matrix is a working-tree October 10 snapshot, not necessarily the committed version. No external research, account writes, participant recruitment, agent spawning, experiments or application-code changes were performed for this scorecard. Matrix rows express public page claims and visibility limits; they do not establish competitors' actual technical quality. New Aegis, MediCheck and MuseumEcho rows are included in the comparison context. No research or competitor implementation is copied.

`S<n>` refers to the existing entry number in SOURCES.md, using that entry's retrieval date and caveats. Sources support the specific context stated in CSV notes, not the numerical opinions. No numbered source is invented for unsupported sectors; data or validation is explicitly **unknown** there. Dynamic source availability and rules were not independently refreshed for this audit. Gallery comparisons are local-snapshot thematic observations, not superiority findings or a global novelty search.

Each CSV row contains problem, user, mechanism, innovation, data, demo, impact, implementation_estimate, major_risk, why_memorable, evidence_assumptions_notes and score_rationale, plus all 19 scores, exact numerator/75 and rank. All CSV fields are quoted. Its formula column precedes numerical scores. The Markdown tables below show the same 19 inputs; the CSV is the concise per-concept dossier.

Common scoring anchors: 0 means little plausible merit or very severe absence; 5 means mixed/uncertain potential; 10 means exceptionally strong screening potential under stated assumptions. Integer judgments have no confidence intervals or empirical calibration. Missing data is usually scored 2–4, not assumed obtainable; documented useful inputs can score 6 even when outcome labels are unknown. Innovation concerns the proposed workflow, never an invented scientific breakthrough. High impact potential denotes importance/reach, never a measured effect.

Feasibility and implementation estimates assume one focused developer building a small **greenfield** demonstration within the remaining October 10–19 window, without existing project code. Day ranges are opinions about engineering effort, exclude wait time for consent/data/hardware, and are not delivery commitments. High execution or live-demo scores can describe a deterministic toy simulator while real-world data scores stay low. Robustness considers sensitivity/domain limitations; failure risk additionally includes missing-data, delivery and reliance risks. Paid API risk 0 means no necessary paid API in the sketched MVP, not proof of zero hosting/hardware/time cost. #8's raw 2 allows unresolved optional feed dependence; billing is unknown. NucleiLens receives no automatic score bonus for being implemented.

Readiness remains unknown for every new concept: no complete access/license package, novelty search, user validation and baseline evaluation was established by these opinions. No scores certify gates or replace the documented NucleiLens failure decisions.

## All concepts: official potential inputs and exact totals

I = innovation; Im = impact; Ex = execution; Pr = presentation. Names are the original concept names.

| Rank | ID | Existing concept | I | Im | Ex | Pr | Exact total /10 | Display /10 |
|---:|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | 14 | Power outage restoration simulator | 7 | 8 | 7 | 9 | 581/75 | 7.746667 |
| 2 | 24 | Community map data-change impact simulator | 7 | 7 | 8 | 8 | 573/75 | 7.640000 |
| 3 | 3 | Heat-plan resource allocator | 5 | 9 | 7 | 9 | 564/75 | 7.520000 |
| 4 | 7 | School-bus stop fairness optimizer | 6 | 8 | 7 | 9 | 559/75 | 7.453333 |
| 4 | 17 | Flood evacuation bottleneck simulator | 6 | 8 | 7 | 9 | 559/75 | 7.453333 |
| 6 | 1 | Microscopy count stress test | 6 | 6 | 8 | 9 | 557/75 | 7.426667 |
| 6 | 19 | Accessible chart sonifier | 7 | 8 | 6 | 9 | 557/75 | 7.426667 |
| 6 | 22 | Classroom air-ventilation experiment kit | 6 | 8 | 7 | 9 | 557/75 | 7.426667 |
| 9 | 25 | Lab image segmentation reliability audit | 6 | 6 | 8 | 9 | 555/75 | 7.400000 |
| 10 | 21 | Public procurement anomaly network | 7 | 8 | 6 | 9 | 548/75 | 7.306667 |
| 11 | 11 | Cold-chain excursion detector | 6 | 8 | 7 | 8 | 539/75 | 7.186667 |
| 12 | 5 | Water-network leak localizer | 7 | 7 | 6 | 9 | 537/75 | 7.160000 |
| 13 | 18 | Microplastic sample image counter | 6 | 8 | 6 | 9 | 535/75 | 7.133333 |
| 14 | 10 | Curb-ramp audit prioritizer | 6 | 8 | 6 | 8 | 527/75 | 7.026667 |
| 15 | 6 | Solar output fault explainer | 6 | 7 | 7 | 8 | 525/75 | 7.000000 |
| 16 | 23 | Crop irrigation leak and stress distinction | 7 | 8 | 5 | 9 | 524/75 | 6.986667 |
| 17 | 20 | Local-language emergency bulletin consistency checker | 5 | 8 | 7 | 8 | 522/75 | 6.960000 |
| 18 | 9 | Sign-language lesson latency coach | 6 | 8 | 5 | 9 | 516/75 | 6.880000 |
| 19 | 16 | Library demand-aware book transfer | 5 | 6 | 8 | 8 | 514/75 | 6.853333 |
| 20 | 12 | River gauge anomaly forecaster | 5 | 8 | 6 | 8 | 501/75 | 6.680000 |
| 20 | 15 | Public-space noise source mapper | 6 | 7 | 6 | 8 | 501/75 | 6.680000 |
| 22 | 2 | Wheelchair data confidence auditor | 5 | 8 | 6 | 7 | 492/75 | 6.560000 |
| 22 | 13 | Medication label accessibility verifier | 5 | 9 | 5 | 8 | 492/75 | 6.560000 |
| 24 | 8 | Wildfire smoke classroom scheduler | 4 | 8 | 6 | 8 | 484/75 | 6.453333 |
| 25 | 4 | Food-tray waste estimator | 5 | 7 | 5 | 8 | 467/75 | 6.226667 |

## All concepts: strategic inputs

The headers below are the exact requested factors, split into two tables for readability. Together with the four potential columns above, they provide all 19 inputs per concept. In the second table, raw failure and paid dependence scores run in the adverse direction and are inverted only inside the formula.

| ID | gallery_originality | wow | feasibility_before_Oct19 | real_data_availability | measurable_results | visual_demo | robustness |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 8 | 8 | 8 | 9 | 8 | 9 | 7 |
| 2 | 7 | 6 | 6 | 6 | 6 | 7 | 5 |
| 3 | 6 | 8 | 7 | 6 | 7 | 9 | 6 |
| 4 | 5 | 7 | 4 | 3 | 4 | 9 | 4 |
| 5 | 8 | 9 | 5 | 3 | 5 | 9 | 4 |
| 6 | 7 | 7 | 6 | 4 | 6 | 8 | 5 |
| 7 | 7 | 8 | 6 | 3 | 6 | 9 | 6 |
| 8 | 4 | 6 | 6 | 4 | 4 | 8 | 5 |
| 9 | 6 | 9 | 4 | 3 | 4 | 10 | 4 |
| 10 | 7 | 7 | 6 | 6 | 6 | 8 | 5 |
| 11 | 7 | 7 | 6 | 3 | 5 | 8 | 5 |
| 12 | 4 | 7 | 5 | 3 | 5 | 8 | 5 |
| 13 | 4 | 8 | 5 | 3 | 5 | 9 | 3 |
| 14 | 8 | 9 | 6 | 3 | 6 | 10 | 6 |
| 15 | 7 | 7 | 5 | 3 | 5 | 8 | 4 |
| 16 | 7 | 6 | 8 | 2 | 6 | 8 | 7 |
| 17 | 4 | 9 | 6 | 3 | 6 | 10 | 5 |
| 18 | 8 | 8 | 5 | 2 | 4 | 9 | 4 |
| 19 | 8 | 9 | 6 | 4 | 5 | 9 | 5 |
| 20 | 4 | 7 | 7 | 3 | 5 | 8 | 5 |
| 21 | 8 | 9 | 5 | 3 | 3 | 9 | 4 |
| 22 | 7 | 8 | 5 | 3 | 5 | 9 | 6 |
| 23 | 6 | 9 | 3 | 2 | 3 | 9 | 3 |
| 24 | 8 | 8 | 8 | 6 | 8 | 9 | 7 |
| 25 | 8 | 8 | 8 | 9 | 8 | 9 | 6 |

| ID | technical_depth | social_relevance | judge_understandability | reproducibility | live_demo_reliability | explain_under_30_seconds | failure_risk | paid_api_dependence |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 7 | 6 | 9 | 9 | 8 | 9 | 3 | 0 |
| 2 | 6 | 9 | 8 | 7 | 7 | 8 | 6 | 0 |
| 3 | 8 | 10 | 8 | 8 | 8 | 8 | 5 | 0 |
| 4 | 6 | 8 | 9 | 5 | 6 | 9 | 7 | 0 |
| 5 | 9 | 8 | 8 | 6 | 7 | 8 | 7 | 0 |
| 6 | 8 | 8 | 8 | 7 | 8 | 8 | 5 | 0 |
| 7 | 8 | 9 | 8 | 7 | 8 | 9 | 5 | 0 |
| 8 | 6 | 9 | 9 | 6 | 6 | 9 | 6 | 2 |
| 9 | 8 | 9 | 8 | 5 | 6 | 8 | 8 | 0 |
| 10 | 8 | 9 | 8 | 7 | 8 | 8 | 6 | 0 |
| 11 | 7 | 9 | 9 | 7 | 8 | 9 | 6 | 0 |
| 12 | 7 | 9 | 8 | 6 | 7 | 8 | 6 | 0 |
| 13 | 7 | 10 | 9 | 5 | 6 | 9 | 8 | 8 |
| 14 | 9 | 9 | 9 | 8 | 9 | 9 | 5 | 0 |
| 15 | 8 | 7 | 8 | 6 | 6 | 8 | 6 | 0 |
| 16 | 7 | 7 | 9 | 8 | 9 | 9 | 4 | 0 |
| 17 | 9 | 10 | 8 | 7 | 9 | 9 | 6 | 0 |
| 18 | 7 | 9 | 9 | 5 | 8 | 9 | 7 | 0 |
| 19 | 8 | 9 | 8 | 6 | 8 | 8 | 6 | 0 |
| 20 | 7 | 9 | 9 | 7 | 8 | 9 | 6 | 0 |
| 21 | 9 | 9 | 7 | 5 | 7 | 8 | 8 | 0 |
| 22 | 8 | 9 | 9 | 7 | 8 | 9 | 6 | 0 |
| 23 | 8 | 9 | 8 | 4 | 5 | 8 | 8 | 0 |
| 24 | 8 | 8 | 9 | 9 | 9 | 9 | 3 | 0 |
| 25 | 8 | 7 | 8 | 9 | 8 | 8 | 4 | 0 |

## Top five: adversarial answers to all ten original questions

These are conjectural answers about the proposed concepts. Requested evaluations are not new studies or results. “Could” and “potential” below denote unproven outcomes; demonstrations are planned scenarios, not executions. The ten-question ordering follows the original report, separating why win/lose and demoability/MVP reliability. No finalist's data, impact or originality gate is declared passed.

### #14 Power outage restoration simulator — rank 1

1. **Why could it win?** Conjecture: a clear essential-service tradeoff plus inspectable constrained scheduling could combine relevance, technical depth and a vivid graph demonstration.
2. **Why could it lose?** Real grid/crew data are unknown. A toy optimizer could omit electrical feasibility and make its preferred policy win by construction.
3. **Is it actually new?** Unknown. Graph scheduling is established; the concise explanation workflow might differentiate, but no source here proves novel restoration methods or an original research contribution.
4. **Can impact be proved?** Proposed test: compare essential-service downtime on preregistered networks against fixed-priority and constraint-aware baselines. This would establish modeled performance only. Actual outage impact needs authorized records, validated constraints and operator evidence; all unknown.
5. **Is technical depth visible?** Potentially, through crew constraints, dependency edges, objective terms and a counterexample to the naive schedule. A colored map alone would not demonstrate depth.
6. **Is it demoable?** A bundled synthetic network can replay a closure and two schedules. Ten-score visual potential assumes transparent scenario labels; no demo was run.
7. **Can the MVP be reliable?** Plausible in 4–7 engineering days for small graphs with input bounds and deterministic replay. Utility-grade reliability and validated electrical modeling remain unproven.
8. **Is there instant insight?** Proposed opening: “Which repair brings essential services back first?” Show the answer change when a shared dependency is exposed; understandability is untested.
9. **Is it better than the gallery?** Unproven. Aegis and ClearRoute already pitch consequential coordination; SwasthSetu pitches allocation. The matrix suggests room for an explicitly inspectable schedule, not superior execution or impact.
10. **What is unforgettable?** Conjectural moment: repairing the less obvious edge restores two services earlier. It must be an honestly labeled model consequence, not a claimed real outcome.

### #24 Community map data-change impact simulator — rank 2

1. **Why could it win?** Conjecture: one tiny map edit produces an immediately visible consequence, with deterministic attribution and a compact reproducible implementation.
2. **Why could it lose?** Reviewers may already use equivalent tooling. Seeded broken edges can make detection trivial while real directionality/access restrictions remain unsupported.
3. **Is it actually new?** Unknown. Graph diffs and route regression tests are established. S17 and S19–S20 describe map semantics and terms, not novelty. Contributor workflow advantage requires a direct tool comparison.
4. **Can impact be proved?** Proposed test: blinded seeded regressions plus documented real edit cases, comparing detection and false alerts with a connectivity-only baseline. Prevented travel harm or contributor time savings require observed users; unknown.
5. **Is technical depth visible?** Potentially: changed-edge attribution, reachability witnesses, direction/access handling and before/after counterfactuals. Basic component coloring would weaken the depth claim.
6. **Is it demoable?** A locally bundled before/after extract or explicitly synthetic graph could reveal a disconnected destination. Actual legal extract and replay validation are not established here.
7. **Can the MVP be reliable?** Plausible in 3–5 days for bounded graphs and seeded cases; production editor integration, large-scale routing and domain completeness excluded. Reproducibility potential is not an observed test pass.
8. **Is there instant insight?** Proposed opening: “This edit cuts access to the clinic.” Use a labeled essential destination and show the responsible edge, without claiming verified on-street access.
9. **Is it better than the gallery?** Unknown. RepoScope describes blast-radius graphs and Nexora invariant-driven drift detection. A civic graph interpretation is thematically distinct, not evidence that its mechanism or build is stronger.
10. **What is unforgettable?** Conjectural moment: an innocuous changed edge erases a destination's access, then restoration brings its route back. The model's omitted restrictions must remain visible.

### #3 Heat-plan resource allocator — rank 3

1. **Why could it win?** Conjecture: heat equity is consequential, and a transparent uncertainty/fairness tradeoff can be explained visually in seconds.
2. **Why could it lose?** S32–S35 directly overlap cooling allocation and uncertainty planning. Dated population and absent local vulnerability/site inputs could yield a polished but operationally weak simulator.
3. **Is it actually new?** Not established. Generic optimization is directly challenged by S33 and S34. The score of 5 for innovation reflects this; even a good interface does not invent robust location-allocation.
4. **Can impact be proved?** Proposed test: worst-case modeled coverage and distributional tradeoffs versus nearest-site and nominal-optimization baselines. Actual reduced heat exposure/injury requires local validation and longitudinal outcomes; unknown. IMD products S4–S9 do not prove project effectiveness.
5. **Is technical depth visible?** Potentially through demand uncertainty, capacity limits, fairness constraints and explanations of plan changes. These must visibly drive the result rather than serve as decorative sliders.
6. **Is it demoable?** A bounded, disclosed scenario using documented WorldPop inputs S14 or labeled synthetic demand could show a site change. No local planning demo was executed in this audit.
7. **Can the MVP be reliable?** Plausible in 4–7 days with local scenario inputs and a small solver. Historical-feed access, site inventories and operational validation remain unknown; cached inputs cannot solve validity.
8. **Is there instant insight?** Proposed opening: “One cooling site cannot serve everyone equally; which plan holds up when demand is uncertain?” Audience comprehension untested.
9. **Is it better than the gallery?** Unproven. CivicAid, SwasthSetu and FloodSense already frame civic/environmental decisions. Primary-source prior art is the stronger threat; missing competitor validation does not imply our superiority.
10. **What is unforgettable?** Conjectural moment: the nominally best site changes when uncertainty or underserved groups are exposed. This is modeled sensitivity, not a measured equity improvement.

### #7 School-bus stop fairness optimizer — shared rank 4

1. **Why could it win?** Conjecture: familiar school travel, explicit capacities and visible distributions could make optimization personally understandable.
2. **Why could it lose?** No verified school demand or safe-walking network. Synthetic pupil locations can hide unsafe crossings and produce a misleadingly fair plan.
3. **Is it actually new?** Unknown; facility-location/equity optimization is established. A transparent burden explanation is a product hypothesis, not a new algorithm.
4. **Can impact be proved?** Proposed test: compare walking-burden distribution, unmet demand and capacity violations against greedy/current layouts on declared scenarios. Real school benefit needs consented demand, verified walk routes and observed usage. S11–S15 describe transit data/terms, not school validation.
5. **Is technical depth visible?** Potentially through capacity constraints, infeasibility explanations and Pareto tradeoffs. A rearranged set of map pins without objectives would be weak evidence.
6. **Is it demoable?** Labeled synthetic demand can show who gains/loses when a capacity or equity constraint changes. No solver/demo result is claimed.
7. **Can the MVP be reliable?** Plausible in 4–7 days for a bounded scenario model; district integration and operational stop selection excluded. S11–S13 access requirements are unresolved for any proposed transit feed.
8. **Is there instant insight?** Proposed opening: “A shorter average walk can still give one group a much longer walk.” Show the distribution; fairness understanding is untested.
9. **Is it better than the gallery?** Unknown. ClearRoute, SwasthSetu and StudentSuccess provide routing/allocation/student context. Mechanism focus may differ; execution and outcomes have not been compared.
10. **What is unforgettable?** Conjectural moment: average-distance improvement reverses when the worst-served group becomes visible. It is an objective tradeoff, not evidence that pupils travel more safely.

### #17 Flood evacuation bottleneck simulator — shared rank 4

1. **Why could it win?** Conjecture: shortest-distance versus clearance-time reversal makes capacity constraints unusually legible and memorable.
2. **Why could it lose?** FloodSense and NewsBridge overlap disaster context. Unsupported traffic/closure assumptions may give a toy simulation the appearance of authoritative evacuation guidance.
3. **Is it actually new?** Unknown; dynamic graph flow and evacuation modeling are established. A scenario explanation could be original implementation, but no novel scientific method is established.
4. **Can impact be proved?** Proposed test: clearance time and unmet shelter demand versus shortest-path and capacity-aware baselines on declared scenarios. Independent traffic calibration and observed evacuations are unknown; no lives-saved claim follows.
5. **Is technical depth visible?** Potentially through edge capacities, queues, staged closures and conservation constraints, with a counterexample to shortest-path routing. Animation without constraint evidence would conceal model weakness.
6. **Is it demoable?** Bundled synthetic roads and shelters could show a closure causing a queue. All assumptions must be displayed; no live routing or real safety evaluation occurred.
7. **Can the MVP be reliable?** Plausible in 4–7 days for a small educational simulator and deterministic replay. Pedestrian/vehicle behavior, road safety and real evacuation reliability remain unproven.
8. **Is there instant insight?** Proposed opening: “The shortest route can clear people last.” The capacity bottleneck should become visible within seconds; audience effect unknown.
9. **Is it better than the gallery?** Unproven. FloodSense covers river intelligence, NewsBridge emergency alerts, and ClearRoute response routing. A capacity experiment is distinct from a risk dashboard, but originality4 reflects the crowded theme.
10. **What is unforgettable?** Conjectural moment: a shorter route visibly accumulates a queue while a longer route clears sooner. A staged toy example does not demonstrate better actual evacuations.

## Interpretation alongside NucleiLens evidence

NucleiLens is existing concept #25, rank 9 at 555/75 = 7.400000/10 under this potential rubric. Its stronger documented data/reproducibility estimates do not establish a new scientific method or a useful human-review advantage. S24–S31 and S37,S40–S46 cover mature segmentation, uncertainty, graph/structure analysis, consensus, editing and measurement prior art. S21/S36 ground the task; S38's dataset record does not establish independent biological groups.

The recorded [JUDGE_SCORECARD.md](../docs/hackathon/JUDGE_SCORECARD.md) retains October 9 simulation totals **15.8 / 15.7 / 15.5 out of 20**, from separate contexts in the same model family. Those are assessments of an implemented project under stated reading limits, not official or independent human judges. They remain unchanged. This 19-factor screening does not numerically replace, uplift or average them. Their documented failed graph/NNLS adoption gates remain failed; the current audit contains no new benchmark or observed-reader evidence.

No participants, interview observations, measured time savings, biological accuracy superiority or gallery superiority are established here. A potential high score for a hypothetical simulator cannot compensate for its unverified realism. Conversely, an implemented project should not receive a fabricated innovation/impact uplift merely because it runs. Scores and close orderings are opinions, not precise probabilities: changing one official input by one point changes T by 0.20; one strategic point changes it by 1/75. The first/fifth spread is only 22/75; tied finalists remain tied.

## Audit provenance

Status: both assigned artifacts completed; original report untouched by this sidecar. Input SHA256 values at read time:

- `research/idea-selection-report.md`: `d21a0140319ef7ebb806e1b0ff80277eeae1dc87095460bcc8e81797eca0d0d1`
- `research/SOURCES.md`: `7ebe7211bbe0286c024744efa1100e2fa684927ceea8c2668e510e9f85c39136`
- `research/competitors/competitor-matrix.csv`: `e84bbdc96b5b47a9744d078e06224ecca5fd2e615818b1b3ea7aaf1ed16d3e66`
- `docs/hackathon/JUDGE_SCORECARD.md`: `da05e9acd313a87d45650d7ab6dc8f777b4b5a7f36759f722fd182d97a5e7b05`

The provenance list is a local snapshot identifier, not an upstream authenticity signature. Other agents may continue editing shared inputs. No global progress file is modified because ownership is restricted to the two scorecard files.

## Implications

The retrospective ranking favors visible constrained-decision demonstrations, while their principal weakness is realistic data and operational validation. It records alternative potential, not a decision to replace NucleiLens. The defensible implication for the existing project is to explain its count-relevant insight and reversible review workflow clearly, preserve failed comparisons, and identify real reader advantage as unresolved. More polish cannot substitute for that evidence. Any future human evaluation must remain truthful and consented; until observations exist, benefit remains unknown. No pivot, scientific-source edit, retuning or judge-score increase is authorized or implied by this audit.
