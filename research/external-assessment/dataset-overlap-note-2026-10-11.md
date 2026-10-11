# BBBC038 / BBBC039 overlap provenance note

Retrieved October 11, 2026. This note documents a newly checked dataset-level
qualification; it does not change either frozen evaluation, selected manifest,
model output, or metric.

## Primary records

- The [official BBBC039v1 record](https://bbbc.broadinstitute.org/BBBC039)
  describes 200 U2OS chemical-screen fields and states that a small fraction of
  its images are also in BBBC038. It does not publish the overlapping image IDs.
- The [2018 Data Science Bowl paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC6919559/)
  describes BBBC038 as images from more than 30 experiments. Its stage1 training
  plus first-stage evaluation comprise approximately 16 experiments; the count
  is uncertain because some public/anonymous images lack source metadata. The
  paper reserves 15 separate experiments for its second-stage holdout. This
  project's additional evaluation used the stage1 training archive, not that
  experiment-held-out set.

Both claims are supported by the dataset publisher and peer-reviewed primary
paper. See [SOURCES.md entries 47–48](../SOURCES.md).

## What the existing screen establishes

Before any annotation decoding or inference, the frozen screen compared the 539
image-property candidates against all 200 BBBC039 images using sampled intensity
correlation, full-image same-size correlation, and horizontal/vertical/both
flips. It flagged 43 potential same-size overlaps; these were excluded before
evaluation. The screening protocol and its original result remain unchanged.

The official BBBC039 page does not identify which images overlap, so the 43
screen flags cannot be claimed as a complete identification of the publisher's
overlap. Nor does the screen detect all possible crops, resampling, or shared
biological experiments. The remaining 496-image analysis is therefore additional
descriptive image evidence, not an independent biological-group validation.

## Interpretation and action

No rerun or post-hoc exclusion is justified from this source statement alone:
the overlapping IDs are not provided, the existing protocol froze the selection
and evaluation before labels/inference, and changing membership after seeing the
results would alter the declared assessment. Preserve all 496 results, state the
overlap limitation, and seek a genuinely experiment-held-out dataset for any
future generalization claim.
