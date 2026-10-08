# NucleiLens

See beyond the count.


[Like](https://secure.devpost.com/users/register?flow%5Bdata%5D%5Bsoftware_id%5D=1470185&flow%5Bname%5D=like_software&return_to=https%3A%2F%2Fdevpost.com%2Fsoftware%2Fnucleilens)

[Comment](https://devpost.com/software/nucleilens#updates)

- #### [Story](https://devpost.com/software/nucleilens)

- #### [Updates](https://devpost.com/software/nucleilens\#updates)


[![NucleiLens – screenshot 3](https://d112y698adiu2z.cloudfront.net/photos/production/software_photos/005/535/310/datas/gallery.jpg)](https://d112y698adiu2z.cloudfront.net/photos/production/software_photos/005/535/310/datas/original.png)
_Frozen50-field assessment: actual equal-budget FP+FN error capture; not measured human time savings._

[![NucleiLens – screenshot 1](https://d112y698adiu2z.cloudfront.net/photos/production/software_photos/005/535/306/datas/gallery.jpg)](https://d112y698adiu2z.cloudfront.net/photos/production/software_photos/005/535/306/datas/original.png)
_Actual interface and real BBBC039 training field. Reference results are labeled and can be rerun locally._

[![NucleiLens – screenshot 2](https://d112y698adiu2z.cloudfront.net/photos/production/software_photos/005/535/308/datas/gallery.jpg)](https://d112y698adiu2z.cloudfront.net/photos/production/software_photos/005/535/308/datas/original.png)
_Automated workflow example: opposing split/merge mask choices preserve total74. Not a human-validated correction._

[![NucleiLens – screenshot 3](https://d112y698adiu2z.cloudfront.net/photos/production/software_photos/005/535/310/datas/gallery.jpg)](https://d112y698adiu2z.cloudfront.net/photos/production/software_photos/005/535/310/datas/original.png)
_Frozen50-field assessment: actual equal-budget FP+FN error capture; not measured human time savings._

[![NucleiLens – screenshot 1](https://d112y698adiu2z.cloudfront.net/photos/production/software_photos/005/535/306/datas/gallery.jpg)](https://d112y698adiu2z.cloudfront.net/photos/production/software_photos/005/535/306/datas/original.png)
_Actual interface and real BBBC039 training field. Reference results are labeled and can be rerun locally._

[![NucleiLens – screenshot 2](https://d112y698adiu2z.cloudfront.net/photos/production/software_photos/005/535/308/datas/gallery.jpg)](https://d112y698adiu2z.cloudfront.net/photos/production/software_photos/005/535/308/datas/original.png)
_Automated workflow example: opposing split/merge mask choices preserve total74. Not a human-validated correction._

[![NucleiLens – screenshot 3](https://d112y698adiu2z.cloudfront.net/photos/production/software_photos/005/535/310/datas/gallery.jpg)](https://d112y698adiu2z.cloudfront.net/photos/production/software_photos/005/535/310/datas/original.png)
_Frozen50-field assessment: actual equal-budget FP+FN error capture; not measured human time savings._

- 1
- 2
- 3

## Inspiration

Two nuclei merge into one. Somewhere else, one splits into two. The total is unchanged—but the measurement is different.

In our fixed assessment of 50 public microscopy fields, four fields had exactly correct total counts while retaining 100 unmatched instances under object-level evaluation. A plausible total can hide disagreement about which nuclei exist.

We built NucleiLens for biology students and researchers who want to inspect the assumptions behind a count. The public BBBC039 benchmark and its associated study provide a concrete way to evaluate instance-level errors rather than rely on a convincing screenshot. \[1,2\]

## What it does

Open a real bundled field or your own single-field image. NucleiLens runs nine deterministic segmentation sensitivity probes on your device, compares their object correspondences, and shows the actual competing outlines.

The signature example is real: two runs both count 74 nuclei, yet the graph contains a 1 → 2 split alternative and a 2 → 1 merge alternative. Click each explanation to inspect it. Neither alternative is automatically declared correct.

A reviewer can select a region, compare candidate counts, confirm a tally, undo it, and export a record with the input hash and analysis configuration. Tally entries stay separate from mask geometry. A reviewer can also explicitly confirm a whole graph-component alternative, producing a real edited label map. Overlap with retained nuclei is rejected; fresh IDs and exact undo preserve integrity. Export a lossless unsigned 32-bit TIFF and a SHA256-linked audit. These human choices are not automatically correct.

## How we built it

The shared Python core uses intensity normalization, background correction, Otsu thresholding, distance peaks, and marker-controlled watershed. Eight alternatives vary threshold, seed spacing, smoothing, and midtone intensity around the baseline.

Sparse bipartite overlap graphs connect baseline and alternate instances when their intersection covers at least 45% of the smaller object. Components with different object cardinalities expose local split, merge, missing, and additional-detection hypotheses; count-neutral boundary changes remain separate.

A React/TypeScript interface runs the numerical Python code inside a dedicated Pyodide/WebAssembly worker. Scientific libraries and real samples are self-hosted. Images are not sent to a project inference service. TIFF preserves numeric precision; browser PNG/JPEG decoding uses 8-bit grayscale. A bounded local Python companion provides a separate recovery path.

## The core innovation

The contribution is an original, inspectable count-audit workflow: identical aggregate counts can be unpacked into opposing local object explanations, linked to real alternate masks and explicit human decisions.

Watershed, uncertainty review, graph matching, and sensitivity analysis are established methods. We do not claim a scientific first or state-of-the-art segmentation. The graph is an explanation layer; the review order is selected by measured comparison.

## Challenges we ran into

Our initial full-validation run had count MAE 25.06. Saturated bright plateaus and weak-signal fields caused serious failures. Validation-guided safeguards reduced MAE to 5.10, with failure cases retained.

Our original graph-ranking hypothesis also failed: simple object disagreement found more annotated error mass at the same budget. A bounded nonnegative ranker failed its adoption gate too. We kept the stronger simple queue, preserved the negative results, froze the protocol, and assessed all 50 test fields without test-driven tuning.

Browser deployment required preserving 16-bit TIFF precision while running the same scientific code locally. We replaced the browser Pillow dependency with bounded TIFF/browser decoding and a small numerical PNG encoder, reducing runtime assets to about 39 MB.

## Accomplishments

- Actual device-local scientific analysis and a public, login-free review workflow.
- A verified same-total opposing split/merge example from a real public image.
- Complete frozen 50-field test: count MAE 5.12, mean instance F1 0.827.
- The preselected object-disagreement queue captures 45.8% of annotated FP+FN error mass at a 20% tile-review budget, versus 20.0% expected random review. Graph ranking captures 39.5%; its inferiority is disclosed.
- Full per-image results, fixed comparator budgets, tie averaging, image-bootstrap intervals, source/archive hashes, and reproducible commands.
- Actual split/merge mask correction, exact undo, compatible reruns, lossless TIFF plus audit-hash readback on the deployment.
- Automated WCAG A/AA checks across desktop, expanded benchmark, and mobile layouts; manual accessibility checks remain.

These are algorithm and workflow measurements, not evidence of human time savings, adoption, clinical benefit, or generalization to all microscopy.

## What we learned

A better explanation is not automatically a better ranking policy. Our object graphs make opposing hypotheses visible, while a simpler overlap-based queue concentrates more benchmark errors. Treating those as separate responsibilities produced a more honest product.

We also learned that a correct count can coexist with poor instance correspondence, and that uncertainty under chosen perturbations cannot detect every stable-but-wrong result.

## What's next

A controlled reader study and external-dataset validation. We will measure those outcomes before claiming user-effort or scientific improvements.

## Built with

Python, NumPy, SciPy, scikit-image, React, TypeScript, Vite, Pyodide, WebAssembly, GeoTIFF.js, FastAPI, pytest, Vitest, Playwright.

## Links

- Live application: [https://nuclei-lens.dumbthing999.chatgpt.site](https://nuclei-lens.dumbthing999.chatgpt.site/)
- Public source: [https://github.com/dumbthing999-ui/nuclei-lens](https://github.com/dumbthing999-ui/nuclei-lens)
- Complete test evidence: [https://github.com/dumbthing999-ui/nuclei-lens/tree/main/evaluation/test](https://github.com/dumbthing999-ui/nuclei-lens/tree/main/evaluation/test)

## Sources and scope

1. Broad Bioimage Benchmark Collection, BBBC039: [https://bbbc.broadinstitute.org/BBBC039](https://bbbc.broadinstitute.org/BBBC039) — public CC0 U2 OS fluorescence images, instance annotations, official partitions.
2. Caicedo et al., Evaluation of Deep Learning Strategies for Nucleus Segmentation: [https://doi.org/10.1002/cyto.a.23863](https://doi.org/10.1002/cyto.a.23863) — dataset-associated analysis of instance segmentation and error modes.
3. Our fixed protocol and measured outputs: repository `evaluation/frozen/` and `evaluation/test/`.

This is a research/education prototype, not a clinical diagnostic tool. AI assistance was used for development, research, review, and draft writing. Reported measurements come from reproducible program execution; human-reader benefits remain unmeasured.

## Built With

- fastapi
- geotiff.js
- [numpy](https://devpost.com/software/built-with/numpy)
- pyodide
- [python](https://devpost.com/software/built-with/python)
- [react](https://devpost.com/software/built-with/react)
- scikit-image
- [scipy](https://devpost.com/software/built-with/scipy)
- [typescript](https://devpost.com/software/built-with/typescript)
- vite
- webassembly

## Try it out

- [nuclei-lens.dumbthing999.chatgpt.site](https://nuclei-lens.dumbthing999.chatgpt.site/ "https://nuclei-lens.dumbthing999.chatgpt.site")
- [GitHub Repo](https://github.com/dumbthing999-ui/nuclei-lens "https://github.com/dumbthing999-ui/nuclei-lens")

