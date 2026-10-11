> Superseded for aggregate capture metrics by the corrected v2 run. The original protocol and output are retained for audit; see [the amendment](../bbbc007-v2/aggregation-amendment.md).

# BBBC007 external-data check

This is a small, separate check of the frozen NucleiLens analysis against a
different Broad Bioimage Benchmark Collection assay. BBBC007 contains
Drosophila Kc167 fluorescence images with hand-drawn nucleus outlines and a
CC0 waiver on images and annotations. The official page describes the image
channels and outlines, recommends citing the original dataset paper, and notes
that its main challenge is cell-boundary segmentation. It is not a dedicated
nuclei-segmentation challenge. [1]

## Frozen scope

The selection rule is every image/outline pair whose relative image filename
ends in `_D_1UL.tif`. This keeps the explicitly marked DNA channel and excludes
the `_F_2UL` actin channel and legacy filenames without channel markers. The
selection is based on archive paths, not image content or benchmark results.
The frozen protocol records the archive-member hashes and the exact inference
and evaluator source hashes.

Before freezing, one marked-DNA outline was inspected only to confirm the binary
outline format and whether closed contours could be filled. No inference or
benchmark outcome was computed during that feasibility check. At protocol
freeze, the evaluator uses the unchanged config from
`evaluation/frozen/protocol.json` and the existing `evaluate_partition`
implementation.

For reference conversion, nonzero outline pixels are treated as drawn contours;
enclosed interiors are filled, contour pixels are removed, and interiors are
labeled with four-connectivity. Open contours and other conversion failures are
retained as failed records. There is no manual repair or post-result exclusion.
RGB and RGBA inputs are converted using the same Rec. 601 luminance equation as
the browser's raster decoder.

## Measures and limits

The primary measures are count MAE, macro instance F1 at IoU 0.5, and error-mass
capture by the preselected object-disagreement queue at four of twenty fixed
tiles. Existing comparators and tie handling are retained. This is a small,
path-selected external-data check, not an official held-out split, representative
sample, lab-independence claim, proof of broad biological generalization, or
human-benefit study. The object masks are reconstructed from outlines, so their
pixel geometry depends on the stated deterministic conversion.

The measured records will be reported in `summary.json` and `per-image.json`;
raw images and masks remain out of version control. Do not use this dataset to
change the frozen BBBC039 protocol or parameters.

## Reproduction

Download the two archives from the official BBBC007 page into `data/raw/` and
verify their SHA256 values against `frozen-protocol.json`. Then run:

```sh
python scripts/evaluate_bbbc007.py --freeze
python scripts/evaluate_bbbc007.py --run
```

The first command records provenance and selection without inference. The
second refuses changed archives or source code and retains every selected field.

## Source

1. Broad Bioimage Benchmark Collection, [BBBC007v1 official record](https://bbbc.broadinstitute.org/BBBC007), retrieved October 12, 2026. It describes Drosophila Kc167 images, DNA/actin channels, hand-drawn nuclei/cell outlines, the recommended citation, and the CC0 waiver.
