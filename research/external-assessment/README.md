# Additional image assessment — completed under frozen protocol

Source: official [BBBC038v1](https://bbbc.broadinstitute.org/BBBC038), CC0 labeled
stage1 archive. Raw670 images were profiled without decoding reference masks or
running inference.539 match a predeclared monochrome/opaque/uint8/dark-background
image-property filter and product dimension bounds. This does not independently
verify modality or cell/source group.

Same-sized raw content screening against all200 BBBC039 raw images found43
potential overlaps, using conservative sampled/full-image intensity correlations
and flips. They were excluded before performance evaluation. The remaining496
images comprise the complete frozen assessment manifest, not a selected success
subset. Crop/resampling/shared-experiment overlap may remain; this is additional
image evidence, not proof of independent biological generalization.

The original inference configuration and scientific core remain unchanged. One
original mask file defines one reference instance, including disconnected pixels.
Overlapping/empty/wrong-shaped reference masks produce retained failure records;
no silent reference correction. Annotations load after each field's inference.
Expected tie capture at4/20 tiles and all6 comparators follow the frozen evaluator.
Image-resampling intervals are conditional on this filtered set, not independent
biological-group intervals. Human review and correction benefits remain unmeasured.

## Reproduce

Download the exact official archive identified in
`research/problem-evidence/bbbc038-download.json` into `data/raw/`. Its checksum is
locally computed and frozen, not a publisher-provided cryptographic signature.

```bash
.venv/bin/python scripts/inspect_external_images.py
.venv/bin/python scripts/screen_external_overlap.py
# Existing protocol is already frozen: never overwrite it.
.venv/bin/python scripts/evaluate_external.py --run
# If interrupted under the same exact source/protocol:
.venv/bin/python scripts/evaluate_external.py --run --resume
```

Per-field atomic checkpoints are ignored under `data/cache/BBBC038-assessment/`.
Final complete records, figures and summary are saved under `evaluation/additional/`.
All496 selected images evaluated;0 structural failures. MAE6.54, meanF1.772;
object-queue capture45.7%, graph39.3%, random20%. See the
[complete report](../../evaluation/additional/README.md) for all records and scope.
