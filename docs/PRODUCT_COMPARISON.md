# Product position and established alternatives

Retrieved October8,2026. This is a sourced capability comparison, **not** a head-to-head
accuracy, usability or speed experiment. Existing tools already count, segment,
inspect and edit biological objects. No claim that their extensions cannot
implement our workflow is justified by this review.

| Tool | Established capabilities in official sources | Relationship to this prototype |
|---|---|---|
| CellProfiler | Reusable pipelines identify and measure nuclei/cells, clumpy objects, morphology and intensity; published pipelines retain modules/settings. [1,2] | Prefer an established pipeline for broad reusable quantitative analysis. NucleiLens concentrates on one small field, nine declared alternatives and an explicit same-total review explanation. |
| ImageJ/Fiji ecosystem | Particle analysis supports counts, outlines/masks, manual multipoint counting and macro/plugin automation. Its Nucleus Counter includes background correction, thresholding and watershed. [3] | These are direct prior art for classical segmentation and counting. NucleiLens packages a particular correspondence explanation, measured queue and auditable component-alternative review. No comparative user-effort advantage has been measured. |
| QuPath | Official documentation describes fluorescence/multiplex cell detection and selecting/configuring the detection channel. [4] | Prefer the established broader workflow when channel-aware analysis is required. NucleiLens supports one grayscale single-frame field; it does not provide multiplex analysis. |
| NucleiLens | Same-core browser inference, nine sensitivity runs, count-changing correspondence components, real alternative replacement, exact undo, uint32 TIFF/audit hash;50 held-out+496 additional-image records. | A bounded review/education prototype. Intended value: inspect why two counts agree or differ without a project inference upload. Actual reviewer preference, benefit and biological correction accuracy remain hypotheses. |

## Specific job to evaluate with users

A biology student or researcher has a small nucleus-stained field and wants to
understand whether a plausible aggregate hides incompatible object explanations.
The first interaction opens an actual split/merge pair, not a settings-heavy
pipeline. The reviewer can export the chosen mask and configuration-linked audit.
This focused interaction is implemented and tested; demand and improved reviewer
outcomes are not established by interface tests.

The graph is an explanation and replacement mechanism, **not** the best measured
ranking method. The simpler object-disagreement queue is the preselected default.
That distinction is visible in the UI and full assessment reports.

## Boundaries and unanswered comparisons

No direct experiment against CellProfiler, ImageJ or QuPath was performed. We
have not exhaustively surveyed all plugins or uncertainty-review literature.
Do not claim numerical superiority, unique mask editing, a scientific first,
universal privacy, faster human review or that existing products lack comparable
features. NucleiLens lacks stacks, multichannel analysis, arbitrary polygon editing,
batch workflows and calibrated uncertainty. Its defensible contribution is the
specific original implementation and inspectable, benchmark-governed workflow.

## Primary sources

1. [CellProfiler official examples](https://cellprofiler.org/examples), publisherCellProfiler; page date not specified, retrieved2026-10-08.
2. [CellProfiler published pipelines](https://cellprofiler.org/published-pipelines), publisherCellProfiler; page date not specified, retrieved2026-10-08. Saved pipelines preserve modules and settings.
3. [ImageJ particle analysis](https://imagej.net/imaging/particle-analysis), publisherImageJ project; page date not specified, retrieved2026-10-08. Threshold/watershed nucleus counting is established functionality.
4. [QuPath multiplexed analysis](https://qupath.readthedocs.io/en/stable/docs/tutorials/multiplex_analysis.html), publisherQuPath documentation; version as rendered0.7.0, retrieved2026-10-08. Default detection can apply to fluorescence/multiplexed images.
