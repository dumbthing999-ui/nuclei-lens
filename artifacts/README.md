# Artifact provenance

Screenshots show the actual application and actual public BBBC039 samples. `review-audit-smoke.json` was exported during automated QA using a deliberately entered +1 tally to check update/undo/export behavior. It is a **synthetic interaction fixture**, not a real human scientific review, corrected ground truth, or evidence of biological accuracy. Real benchmark results are in `evaluation/`.


`mask-edit-smoke.tif` and `mask-edit-audit-smoke.json` record automated UI
confirmation of the real first training field's split and merge alternatives.
Counts follow74→75→74 while exported pixels change. This is a **software-test
interaction fixture**, not a human-validated scientific correction or evidence
of improved segmentation accuracy. A separate rerun check confirms byte equality;
undo restores the exact original mask. Those duplicate temporary TIFFs are ignored.
