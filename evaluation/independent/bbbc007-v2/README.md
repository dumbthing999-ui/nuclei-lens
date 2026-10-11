# BBBC007 external-data check (corrected reporting revision)

This is a small exploratory check of the frozen NucleiLens workflow on a
separate Broad Bioimage Benchmark Collection assay. BBBC007 contains Drosophila
Kc167 fluorescence images with DNA/actin channels and hand-drawn outlines; the
official record states a CC0 waiver. Its primary challenge is cell-boundary
segmentation, so this is not a dedicated nuclei-segmentation benchmark. See
[the official BBBC007 record](https://bbbc.broadinstitute.org/BBBC007).

## Protocol and results

The protocol selects every archive image whose relative path ends exactly in
`_D_1UL.tif` and has a same-path outline. This path rule selected 11 fields,
without looking at image content or benchmark outcomes. The inference
configuration and evaluation method are unchanged from the project's frozen
BBBC039 evaluation. Outlines are converted by filling enclosed contours,
removing contour pixels, then labeling interiors with 4-connectivity. No manual
repair, tuning, or post-result exclusion was applied.

All 11 selected fields evaluated successfully. Count MAE was 4.91 nuclei per
field, macro instance F1 at IoU 0.5 was 0.870, and total false positives plus
false negatives were 202. At four of twenty fixed centroid tiles, the
object-disagreement queue captured 46.0% of pixel/object error mass; random
selection captured 20.0%. This is descriptive evidence on a small path-selected
set, not proof of superiority, broad biological generalization, independent
laboratory validation, or researcher benefit. The result is not a new tuned
model or an official held-out challenge score.

The aggregation repair is limited to the summary: `evaluate_partition`
returns absolute captured error mass for each field, so v2 sums those values
and divides once by total error mass. The initial v1 report multiplied each
field's captured mass by that field's error mass again. The original v1 files
remain unchanged for audit; v2 uses the same selected image/outline hashes,
configuration, inference code, and metric definitions. No model parameters or
frozen BBBC039 results were changed.

## Reproduce

Download the two official archives to `data/raw/` and verify the recorded
SHA256 values. Then run:

```sh
python scripts/evaluate_bbbc007_v2.py --freeze
python scripts/evaluate_bbbc007_v2.py --run
```

The freeze step records source, archive, and member hashes; the run refuses
changes and retains every selected field. Raw images and masks are not included
in the repository.
