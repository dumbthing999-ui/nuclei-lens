# Human-confirmed mask review

The baseline and sensitivity masks are immutable inference outputs. A separate
working label map begins as the baseline. A tally is a human-entered count against
original baseline-centroid tiles; tally entries never edit mask geometry. The UI
labels the tally total and reviewed-mask instance count separately.

## Confirm a component

1. Inspect a graph event and its source sensitivity run.
2. Explicitly confirm its complete baseline/alternate instance sets.
3. Reject if original target geometry has already changed, a source ID is absent,
   or a proposed foreground pixel overlaps any retained foreground instance.
4. Remove the exact baseline IDs and copy complete actual alternate instances,
   assigning fresh unique IDs. No boundary clipping or invented pixels.
5. Check that actual unique-instance count changes by alternate−baseline cardinality.
6. Record changed pixel indices and prior IDs for exact undo.

An alternative with conflicting geometry remains inspectable, but cannot be applied
as a component replacement. Undo overlapping edits or choose another proposal.
Free drawing, arbitrary instance merging and clinical diagnosis are outside scope.

## Export and preservation

**Export label TIFF** writes single-channel little-endian unsigned32bit instance
IDs, with zero background. **Export review JSON** records input hash, configuration,
source event IDs/run, new IDs, timestamps, changed-pixel counts, actual instance
count and SHA256 of the little-endian uint32 pixel stream. The TIFF file hash itself
differs because it includes headers. Use both exports to preserve the session.

Compatible identical input/configuration/source-mask reruns retain mask edits and
tallies. A different input or different source masks resets editing. Reload clears
unsaved in-memory state. No user image or review is uploaded. History is bounded
to20 edits and1,048,576 changed-pixel entries; export or undo at the limit.

## Evidence and limitations

The automated first-training-field workflow confirms the real1→2 split then2→1
merge proposals:74→75→74 instances while pixels change. TIFF readback, audit hash,
compatible rerun preservation and exact undo all pass. This is a **test interaction
fixture**, not human scientific validation or proof those alternatives are correct.
No mask-edit accuracy, real reader time savings or clinical benefit is claimed.
Frozen test segmentation/evaluation code and results remain unchanged.
