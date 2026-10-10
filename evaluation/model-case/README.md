# Existing model masks: single-field annotation diagnostic

This is a descriptive examination of the existing first BBBC039 training example,
not a held-out comparison or a new segmentation algorithm. All three predictions
already exist. Their images, counts and masks were public before this diagnostic
was declared; the new measurements must not be called independent confirmation.

The [protocol](protocol.json) fixes that one field, all three methods, source/
archive/prediction hashes and IoU0.5 cardinality-first matching. It is committed
before calculating these new diagnostic results. No annotation enters inference;
this workflow only scores existing predictions after verifying them. The existing
50-field and496-field protocols/results remain unchanged. Fixed0.1IoU merge/split
hypotheses are diagnostics, not verified biological mistakes. Keep every method
and any failure; do not tune or select by the outcome.

No outcome is recorded yet. Run the diagnostic only after the reproducible script
is reviewed and checked. Model weights and parameters remain the previously
recorded ones; training overlap and reference imperfection are unresolved.
No human-reader benefit, scientific-first or general superiority claim follows.
