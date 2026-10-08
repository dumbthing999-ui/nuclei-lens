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

Use the committed frozen protocol and selection artifacts. Do not regenerate or
replace their timestamped profiles while reproducing this assessment. Raw-image
profiling and overlap scripts document the original pre-freeze selection process;
rerunning them belongs in a separate scratch checkout with an explicit new protocol.
The archive checksum is locally computed/frozen, not a publisher signature.

```bash
mkdir -p data/raw
curl --fail --location --output data/raw/BBBC038-stage1_train.zip https://data.broadinstitute.org/bbbc/BBBC038/stage1_train.zip
.venv/bin/python scripts/evaluate_external.py --run
# If interrupted under the same exact source/protocol:
.venv/bin/python scripts/evaluate_external.py --run --resume
.venv/bin/python scripts/check_additional.py
.venv/bin/python scripts/plot_additional.py
.venv/bin/python scripts/inspect_additional_cases.py
```

The runner verifies the local archive checksum and frozen source hashes before
inference, then reads the committed496-image manifest. Per-field atomic checkpoints
are ignored under `data/cache/BBBC038-assessment/`. Full results are under
`evaluation/additional/`: all496 selected images evaluated,0 structural failures;
MAE6.54, meanF1.772; object capture45.7%, graph39.3%, random20%. See the
[complete report](../../evaluation/additional/README.md) for all records and scope.
