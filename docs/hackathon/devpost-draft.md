## Inspiration

[Try the live demo](https://nuclei-lens.dumbthing999.chatgpt.site) · [Watch the 3:35 video](https://youtu.be/nik8WtPUrUc) · [View the code](https://github.com/dumbthing999-ui/nuclei-lens) · [Download the 720p video](https://github.com/dumbthing999-ui/nuclei-lens/releases/download/v0.2.0/eurekadev-reviewed-720p.mp4)

Two segmentation runs can report the same number of nuclei while disagreeing about which objects are present. One region may merge two nuclei; another may split one into two. The errors can cancel in the total.

In our fixed 50-field test, four fields had the reference count but 100 unmatched instances by object-level evaluation. A correct total alone does not prove that the segmentation is correct. [1,2,3]

## What it does

NucleiLens runs nine deterministic segmentation variations on a single image in your browser. It compares the resulting objects, highlights regions that changed, and shows possible split, merge, missing-object, or extra-object explanations.

The live example is real: two runs both count 74. Inspecting a split and a merge changes the reviewed mask count **74 → 75 → 74**. Each alternative is only a hypothesis. You choose whether to confirm it.

A reviewer can record a separate count, correct a mask component, undo the edit, and export a label TIFF plus an audit report. The report links the original and reviewed masks with hashes. Measurements recalculate from the edited mask; the review tally remains separate.

## How we built it

A Python image-analysis core runs locally in a browser worker through Pyodide and WebAssembly. It uses background correction, thresholding, distance peaks, watershed, and sparse object matching across sensitivity runs. Images are not sent to a NucleiLens inference service.

The matching graph explains count-changing alternatives. It did **not** make the best review queue: on validation, it captured 38.4% of annotated error mass at a 20% tile budget, compared with 44.0% for simple object disagreement. We kept the graph as an explanation and use the better measured queue as the default. [3]

## Model comparison

The browser includes actual precomputed Cellpose and StarDist predictions for one public training image. Both predict 68 instances, but their masks differ at 3,738 pixels and across 69 correspondence components. These are disagreements, not 69 verified errors or an accuracy ranking.

The browser imports model masks; it does not run those neural networks. An optional local CLI runs Cellpose and StarDist on CPU and records model, weight, input, and output hashes. [5,6]

## Results

On the frozen 50-field BBBC039 test set, count MAE was 5.12 and mean instance F1 was 0.827. At a fixed 20% tile-review budget, the selected object-disagreement queue contained 45.8% of annotated FP+FN error mass; the graph queue contained 39.5%, and random review is 20% in expectation. This measures error concentration, not human time saved or automatic correction. [1,2,3]

A separate run on 496 BBBC038 fields had count MAE 6.54, mean instance F1 0.772, and object-queue error capture of 45.7% at the same budget. We scanned all 670 BBBC038 stage1 images against all 200 BBBC039 fields: 43 same-size matches mapped one-to-one to 43 distinct fields, agreeing with the BBBC038 workbook's 43-image BBBC022 training group. The workbook has no per-image crosswalk, and crop, resampling, or other source overlap may remain. This is not an independent biological-group validation. [1,4]

## What is different

Cellpose and StarDist segment images; napari and other tools support mask review; consensus methods already combine segmentation results. NucleiLens focuses on one task: expose how opposing object changes can hide behind a plausible total, then let a person inspect and record a mask decision. We do not claim a new segmentation algorithm, better accuracy than existing tools, or measured reader benefit. [5,6]

## Challenges and what we learned

Our first idea was to rank review regions with the correspondence graph. It performed worse than simple object disagreement under the predeclared validation comparison, so we changed its role and retained the negative result. We also learned that a correct count can coexist with poor object correspondence, and sensitivity checks cannot detect every stable-but-wrong mask.

## Limitations and next steps

The current workflow is for bounded, single-channel 2D images. Alignment of an imported mask requires a person's visual judgment. We have not measured reader speed, correction accuracy, adoption, or downstream biological impact. A consented reader study and more independent source validation are needed before making those claims.

The video phrase “biological measurement is broken” at 0:06 refers to a possible object-level segmentation mismatch, not a demonstrated downstream biological outcome.

## Built with

Python, NumPy, SciPy, scikit-image, React, TypeScript, Vite, Pyodide, WebAssembly, GeoTIFF.js, FastAPI, pytest, Vitest, Playwright, Cellpose, StarDist.

## Sources

1. [BBBC039 dataset record](https://bbbc.broadinstitute.org/BBBC039) — public images, instance annotations, and official partitions.
2. [Caicedo et al., nucleus segmentation evaluation](https://doi.org/10.1002/cyto.a.23863) — dataset-associated instance-segmentation evaluation.
3. [Frozen protocol and results](https://github.com/dumbthing999-ui/nuclei-lens/tree/main/evaluation/frozen).
4. [BBBC038 dataset record](https://bbbc.broadinstitute.org/BBBC038) — images and dataset metadata; full additional assessment is in the [repository](https://github.com/dumbthing999-ui/nuclei-lens/tree/main/evaluation/additional).
5. [Established-tool comparison](https://github.com/dumbthing999-ui/nuclei-lens/blob/main/docs/PRODUCT_COMPARISON.md).
6. [Cellpose/StarDist implementation notes and sources](https://github.com/dumbthing999-ui/nuclei-lens/blob/main/docs/OPTIONAL_MODELS.md); [2025 consensus segmentation study](https://doi.org/10.3389/fgene.2025.1547788).

NucleiLens is a research and education prototype, not a clinical diagnostic tool. AI tools assisted with development, research, review, and writing. All reported measurements come from reproducible program runs; human-reader benefits remain unmeasured.
