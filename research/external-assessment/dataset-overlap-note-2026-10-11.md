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

## Complete-archive pixel cross-check

Before any annotation decoding or inference, the frozen screen compared the 539
image-property candidates against all 200 BBBC039 images using sampled intensity
correlation, full-image same-size correlation, and horizontal/vertical/both
flips. It flagged 43 potential same-size overlaps; these were excluded before
evaluation. A separate reproducible scan of all 670 BBBC038 stage1 images
reproduced exactly those 43 candidates and reference-image mappings. Each matched
one distinct BBBC039 field; full-image Pearson correlations ranged from
0.99895–0.99990. No additional same-size matches met the frozen thresholds.

The official BBBC038 workbook separately reports 43 stage1 training images under
`project_id=bbbc022`. The one-to-one pixel-match count and this source-group count
agree exactly, consistent with the screen capturing the complete known BBBC022
overlap group. The workbook is aggregate metadata and has no per-image ID
crosswalk, so this is strong count-level corroboration rather than a publisher
supplied identity map. Machine results and file hashes are in
`overlap-audit-all-stage1-2026-10-11.json`; reproduce with:

```bash
mkdir -p data/raw/BBBC039
curl --fail --location --output data/raw/BBBC038-stage1_train.zip https://data.broadinstitute.org/bbbc/BBBC038/stage1_train.zip
curl --fail --location --output data/raw/BBBC038-metadata.xlsx https://data.broadinstitute.org/bbbc/BBBC038/metadata.xlsx
curl --fail --location --output data/raw/BBBC039/images.zip https://data.broadinstitute.org/bbbc/BBBC039/images.zip
.venv/bin/python scripts/audit_dataset_overlap.py
```

The 43-to-43 correspondence strongly supports that the known BBBC022 image group
was identified and excluded. It does not establish absence of every possible
crop/resampled copy, any related images from other BBBC038 sources, or shared
biological experiments. The remaining 496-image analysis is therefore additional
descriptive image evidence, not an independent biological-group validation.

## Interpretation and action

No post-hoc exclusion is justified: the overlap candidates were excluded before
labels/inference, and changing membership after seeing the results would alter
the declared assessment. Preserve all 496 results, report the count-level
corroboration and remaining source limitations, and use a genuinely
experiment-held-out dataset for any future generalization claim.
