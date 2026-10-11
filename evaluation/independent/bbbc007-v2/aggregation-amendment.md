# Reporting amendment: BBBC007 v2

Date: 2026-10-12

The first frozen run is retained at `evaluation/independent/bbbc007/`. Its
per-image inference records are valid, but its aggregate error-capture
calculation is invalid: per-image `capture_curves[method][4]` already contains
absolute captured error mass, and the v1 summarizer multiplied it by each
field's total error mass before dividing by the overall mass.

The corrected v2 uses the same archive/member manifest, frozen inference
configuration, unchanged core/graph/evaluation modules, and the same 11 fields.
It sums the per-field captured masses and divides once by the sum of all field
error masses. The random baseline is exactly 20%, matching four selected tiles
out of twenty. The corrected protocol and complete records are stored beside
this note. No inference settings, selection criteria, source images, or frozen
BBBC039 outcomes were changed in response to results.
