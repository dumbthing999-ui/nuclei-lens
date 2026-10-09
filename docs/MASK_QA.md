# Segmentation QA, measurements and external masks

## Relationship to existing tools

Cellpose and StarDist already segment instances, napari already supports label
editing and measurements, and CellSampler combines existing model outputs.
These capabilities are prior art, not a scientific-first claim for NucleiLens.
Sources43–46 in `research/SOURCES.md` document that boundary. The purpose of this
addition is a concrete inspect/confirm/recalculate/export workflow with explicit
provenance. Comparative user benefit remains unmeasured.

## Workflow

1. Open an image/example and inspect sensitivity alternatives as before.
2. Optionally run established neural models locally using `OPTIONAL_MODELS.md`,
   or export their already generated instance masks from an existing editor.
3. On the first training field, **Load real Cellpose + StarDist examples** loads
   two actual CPU predictions and their source hashes. These are precomputed, not
   neural inference in the browser. Each has68instances, but the masks differ.
   Pairwise comparisons are retained in the QA report. Alternatively, import up to three aligned, uncompressed, single-channel label TIFFs.
   Dimensions must exactly match; unsigned8/16/32-bit IDs are preserved, background0.
4. Inspect actual original/imported outlines before confirming an external
   component. Sparse overlap edges use intersection divided by the smaller area
   ≥0.45. Split/merge/boundary/loss/addition/complex labels are hypotheses.
5. Confirm explicitly; retained-object conflicts and overlapping edits are
   rejected. Undo restores the original pixel values exactly.
6. Area, pixel-center centroid, exclusive bounding box, border flag and exposed
   four-neighbor grid perimeter recalculate from the actual reviewed label map.
7. Export all current measurements as CSV, the uint32 label TIFF, review JSON
   and a segmentation-QA JSON report linking source, original and reviewed hashes.

## Report semantics

The report distinguishes equal totals from equal partitions. Arbitrary label-ID
renumbering is treated as the same segmentation; direct label-value changes are
reported separately from foreground/background differences. Opposing split and
merge components can change the partition while retaining the total and foreground
area. No reference mask is loaded, so none of this measures accuracy or proves
biological errors. Imported source names are user descriptions; matching image
size and a hash do not independently verify alignment or model/weight provenance.

Object rows describe pixels, not physical microns, intensity or validated biology.
Centroids use pixel centers(x+0.5,y+0.5), bounding-box maxima are exclusive, and
perimeter counts exposed horizontal/vertical edges. This grid perimeter is not
an isotropic Euclidean estimate. All pixels sharing an ID form one instance,
even if disconnected. Tally corrections remain separate from geometry.

## Bounds and failure states

Files≤10MB; image≤1,048,576pixels;≤10,000instances per mask;≤200,000intersecting
label pairs;≤2,000differing components;≤3external masks per field. Correspondence lists show30components per page, with every component available
for inspection and in the report. Use smaller fields for shorter queues. Unsupported compression, signed or
floating IDs, multiple pages, orientation and geometry mismatches fail explicitly.
Uncompressed imports avoid unbounded decompressor expansion. No resampling or
automatic consensus is performed. Changing images discards imported masks; all
review state is tab-local and must be exported before closing.

## Validation

Unit tests cover exact geometry, empty/high-ID fields, ID permutation invariance,
opposing split/merge components, boundary/appearance/loss hypotheses, undo and
strict TIFF reading. `frontend/tests/mask-qa-smoke.mjs` exercises actual frozen
sensitivity masks (explicitly not neural outputs), explicit inspection/confirmation,
CSV/report/TIFF hash agreement, equal-count/different-partition reporting, exact
measurement undo, invalid geometry, image-switch cleanup and mobile overflow.
The same browser check loads both actual neural outputs, verifies their integrity,
and checks the68/68equal-total/different-segmentation result. Actual outcomes
belong in `evaluation/checks/mask-qa-browser.json`; mock adapter unit tests remain
separate from real execution. Neither is a comparative accuracy evaluation.

## Reviewed limitations

Tiny fragments can connect several objects transitively under a smaller-area
threshold; a component is an overlap hypothesis, not a verified biological group.
External components with more than32total IDs are inspect/export only to avoid
confirming large aggregate changes in this interface. Detailed original/reviewed
correspondence can exceed its computation bounds; in that case the report
explicitly marks it unavailable while retaining actual measurements and hashes.
