# Innovation and evidence

## Existing approach

Established tools already segment nuclei, count objects, edit masks, and estimate uncertainty. Watershed, object matching, test-time perturbations, and human review are prior art. See [sources](../research/SOURCES.md), especially Caicedo et al. 2019 and references 21–31, 36–37. No scientific-first or state-of-the-art claim is made.

## Limitation

A total can conceal opposing local instance changes. A split adds one object; a merge removes one. Agreement in the final count is not evidence of agreement about which nuclei exist. Pixel uncertainty and count-changing topology answer different questions.

## Our insight

Make the disagreement inspectable, including when aggregate counts agree. Use the review policy that actually measures best, while retaining sparse count-changing graphs as explanations rather than claiming they are a superior ranker.

## Technical mechanism

Nine deterministic watershed sensitivity runs vary threshold, seed spacing, smoothing, and midtone intensity. For each alternative, a sparse bipartite overlap graph connects baseline and alternate instances with at least 45% coverage of the smaller object. Connected components with different cardinalities yield localized split, merge, lost, or additional-detection hypotheses. Count-neutral components are excluded from this explanation layer. Masks remain whole; a fixed 4×5 grid assigns review counts and errors by centroid.

A worker runs the same numerical Python core in the browser. The reviewer can inspect actual competing outlines, highlight conflict bounds, choose a candidate count, confirm a human entry, undo it, and export an audit document. Manual tallies stay separate from mask geometry. Explicitly confirmed graph components can replace original mask instances, with overlap conflicts rejected, fresh label IDs, undo, lossless uint32 TIFF export and an audit hash. Compatible reviews and mask edits survive deterministic reruns. The real split/merge sequence changes74→75→74 while preserving its changed pixels; it demonstrates inspectable choices, not improved accuracy.

## Evidence

The first bundled **real** training field has 74 baseline nuclei and 74 nuclei in its lower-threshold alternative. Graph events include both a 1→2 split alternative and a 2→1 merge alternative. The interface links directly to these measured alternatives; neither is declared correct without human inspection.

On 50 official validation fields, graph ranking captures 38.4% of FP+FN error mass at a 20% review budget, versus 44.0% for simple object disagreement and 20% expected random review. The graph underperforms the object comparator by 5.6 percentage points, paired bootstrap 95% interval −8.4 to −3.4. A nonnegative ranker (four features plus one intercept; five fitted coefficients) trained on all 100 training fields captured 43.56% on validation and failed its predefined adoption gate; it is excluded from the product. See `evaluation/ranker/validation.json`.

Therefore object disagreement is the default queue. Graph correspondence provides explanations and the same-total counterexample, not a performance-superiority claim. Frozen configuration and protocol are in `evaluation/frozen/`; the completed 50-image held-out test has MAE 5.12, mean F1 0.827, and 45.8% error capture for the preselected object queue versus 39.5% graph and 20% random. Four exactly counted test fields still contain 100 unmatched instances in total; these are IoU-matching errors, not biological diagnoses.

## Why it matters

The workflow lets a biology student or researcher inspect the assumptions behind a count and record a decision without uploading the image to an analysis service. An unchanged-pipeline additional BBBC038 assessment covers496 preselected images: MAE6.54, meanF1.772, object-queue capture45.7%, graph39.3%, random20%; zero structural failures.43 potential same-size overlaps were removed before evaluation, but unknown source-group dependence and reference imperfections remain. See [complete scope/results](../evaluation/additional/README.md). Actual human effort, user accuracy, independent biological generalization and downstream research benefit remain unmeasured.

## Thirty-second explanation

“Two microscopy runs can both count 74 nuclei and still disagree about which nuclei exist. NucleiLens shows the split and merge alternatives behind that agreement, runs the analysis on your device, and records your review decisions. We benchmarked every review queue, kept the stronger simple ordering, and show the cases where our graph did not win.”

## Established consensus and editing tools — October8 refresh

Cellpose, StarDist and napari already provide segmentation and/or mask editing;
CellSampler's2025 paper combines multiple segmentation methods and exports object
property catalogs. See sources41–44 in `research/SOURCES.md`. Multi-model support,
manual correction and geometric measurements alone are not a novel algorithm.
NucleiLens must be assessed on its inspectable local workflow, correspondence
hypotheses, hash-linked exports and declared review-budget evidence. Practical
advantage over these tools remains unmeasured. External label imports and new
measurements do not change the frozen benchmark or establish accuracy gains.
