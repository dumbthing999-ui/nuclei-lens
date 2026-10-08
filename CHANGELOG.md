# Changelog

## Unreleased — 2026-10-08

- Original deterministic nuclei segmentation and nine-run sensitivity pipeline.
- Sparse object-overlap graphs expose split, merge, lost, and additional candidates.
- Equal-budget evaluation against five comparators on official BBBC039 partitions.
- Bright-artifact and weak-signal safeguards, with visible scope limitations.
- Browser-local Python/WebAssembly analysis and bundled real training examples.
- Responsive review UI, alternative overlays, manual count corrections, undo,
  and downloadable audit records. Corrections do not silently change masks.
- Optional bounded FastAPI companion and deterministic unit/integration checks.

No submission release is tagged yet. Video production is deferred by the owner.


### Human-confirmed mask correction

- Add bounded lossless source labels, explicit graph-component replacement with
  conflict rejection, fresh IDs, exact undo and separate reviewed-mask display.
- Export uint32 label TIFF plus audit SHA256; preserve compatible edits on rerun.
- Verify real74→75→74 split/merge workflow, exported pixels and exact restoration.
- Preserve frozen inference/evaluation; no human accuracy or time-savings claim.
- Restore Devpost authentication, create/read back fresh EurekaDev draft, and merge
  verified production-preview CI repair via PR1. Video remains on hold.
- Preserve original dependency license notices with source/version provenance.
