# NucleiLens

**Tagline:** See beyond the count.

Saved as a fresh EurekaDev draft on October 8, 2026; authenticated API readback verified. Rendered page verification and final submission remain pending. The initial account response is archived under `archive/`. Video remains on hold.

## Inspiration

Two nuclei merge into one. Somewhere else, one splits into two. The total is unchanged—but the measurement is different.

In our fixed assessment of 50 public microscopy fields, four fields had exactly correct total counts while retaining 100 unmatched instances under object-level evaluation. A plausible total can hide disagreement about which nuclei exist.

We built NucleiLens for biology students and researchers who want to inspect the assumptions behind a count. The public BBBC039 benchmark and its associated study provide a concrete way to evaluate instance-level errors rather than rely on a convincing screenshot. [1,2]

## What it does

Open a real bundled field or your own single-field image. NucleiLens runs nine deterministic segmentation sensitivity probes on your device, compares their object correspondences, and shows the actual competing outlines.

The signature example is real: two runs both count74 nuclei, yet the graph contains a1→2 split alternative and a2→1 merge alternative. Click each explanation to inspect it. Neither alternative is automatically declared correct.

A reviewer can select a region, compare candidate counts, confirm a tally, undo it, and export a record with the input hash and analysis configuration. In this verified build, tally corrections do not modify mask geometry. Guided mask correction is a next development step, not a claimed completed feature.

## How we built it

The shared Python core uses intensity normalization, background correction, Otsu thresholding, distance peaks, and marker-controlled watershed. Eight alternatives vary threshold, seed spacing, smoothing, and midtone intensity around the baseline.

Sparse bipartite overlap graphs connect baseline and alternate instances when their intersection covers at least45% of the smaller object. Components with different object cardinalities expose local split, merge, missing, and additional-detection hypotheses; count-neutral boundary changes remain separate.

A React/TypeScript interface runs the numerical Python code inside a dedicated Pyodide/WebAssembly worker. Scientific libraries and real samples are self-hosted. Images are not sent to a project inference service. TIFF preserves numeric precision; browser PNG/JPEG decoding uses8-bit grayscale. A bounded local Python companion provides a separate recovery path.

## The core innovation

The contribution is an original, inspectable count-audit workflow: identical aggregate counts can be unpacked into opposing local object explanations, linked to real alternate masks and explicit human decisions.

Watershed, uncertainty review, graph matching, and sensitivity analysis are established methods. We do not claim a scientific first or state-of-the-art segmentation. The graph is an explanation layer; the review order is selected by measured comparison.

## Challenges we ran into

Our initial full-validation run had count MAE25.06. Saturated bright plateaus and weak-signal fields caused serious failures. Validation-guided safeguards reduced MAE to5.10, with failure cases retained.

Our original graph-ranking hypothesis also failed: simple object disagreement found more annotated error mass at the same budget. A bounded nonnegative ranker failed its adoption gate too. We kept the stronger simple queue, preserved the negative results, froze the protocol, and assessed all50 test fields without test-driven tuning.

Browser deployment required preserving16-bit TIFF precision while running the same scientific code locally. We replaced the browser Pillow dependency with bounded TIFF/browser decoding and a small numerical PNG encoder, reducing runtime assets to about39 MB.

## Accomplishments

- Actual device-local scientific analysis and a public, login-free review workflow.
- A verified same-total opposing split/merge example from a real public image.
- Complete frozen50-field test: count MAE5.12, mean instance F1 0.827.
- The preselected object-disagreement queue captures45.8% of annotated FP+FN error mass at a20% tile-review budget, versus20.0% expected random review. Graph ranking captures39.5%; its inferiority is disclosed.
- Full per-image results, fixed comparator budgets, tie averaging, image-bootstrap intervals, source/archive hashes, and reproducible commands.
- Working review, undo, compatible reruns, JSON export, and mobile-layout checks on the actual deployment.

These are algorithm and workflow measurements, not evidence of human time savings, adoption, clinical benefit, or generalization to all microscopy.

## What we learned

A better explanation is not automatically a better ranking policy. Our object graphs make opposing hypotheses visible, while a simpler overlap-based queue concentrates more benchmark errors. Treating those as separate responsibilities produced a more honest product.

We also learned that a correct count can coexist with poor instance correspondence, and that uncertainty under chosen perturbations cannot detect every stable-but-wrong result.

## What's next

Human-confirmed local mask correction and export, a controlled reader study, and external-dataset validation. We will measure those outcomes before claiming user-effort or scientific improvements. The required competition video will be produced only after the owner's special instructions.

## Built with

Python, NumPy, SciPy, scikit-image, React, TypeScript, Vite, Pyodide, WebAssembly, GeoTIFF.js, FastAPI, pytest, Vitest, Playwright.

## Links

- Live application: https://nuclei-lens.dumbthing999.chatgpt.site
- Public source: https://github.com/dumbthing999-ui/nuclei-lens
- Complete test evidence: https://github.com/dumbthing999-ui/nuclei-lens/tree/main/evaluation/test
- Video: pending owner instructions; no URL claimed.

## Sources and scope

1. Broad Bioimage Benchmark Collection, BBBC039: https://bbbc.broadinstitute.org/BBBC039 — public CC0 U2 OS fluorescence images, instance annotations, official partitions.
2. Caicedo et al., Evaluation of Deep Learning Strategies for Nucleus Segmentation: https://doi.org/10.1002/cyto.a.23863 — dataset-associated analysis of instance segmentation and error modes.
3. Our fixed protocol and measured outputs: repository `evaluation/frozen/` and `evaluation/test/`.

This is a research/education prototype, not a clinical diagnostic tool. AI assistance was used for development, research, review, and draft writing; reported numerical results come from reproducible program execution, not model-generated estimates. No users, interviews, experiments, or development history are fabricated.
