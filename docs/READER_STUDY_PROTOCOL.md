# Planned exploratory reader exercise

**Status: protocol only. No participants recruited, sessions run, or benefits measured.**

## Question

At the same four-of-twenty region budget, do the default queue and visible
segmentation alternatives help a reader correct local nucleus tallies more
accurately than baseline-only inspection? This evaluates human counting decisions,
not the benchmark's FP+FN capture proxy or the biological correctness of mask edits.

## Participants and consent

Proposed pilot: six consenting adults with basic microscopy/counting experience.
Record pseudonymous participant codes and broad experience bands only. No names,
contact information, health information, images of people or student records.
Explain the exploratory purpose, voluntary participation and withdrawal before
starting. Do not send recruitment messages without owner authorization. Confirm
any applicable institutional review requirements before conducting the exercise.

## Conditions

- Control: same public image, baseline outlines, fixed centroid tile definitions,
  tally input and export; four regions supplied in a seeded random order.
- NucleiLens: same controls and baseline, four regions selected by the preselected
  object-disagreement queue, actual alternative outlines and graph explanation.

This compares the complete review assistance workflow; it does not isolate graph
explanations from ranking. A later ablation would require separate conditions.
Study-specific condition presentation/blinding is not yet implemented. Hide all
reference counts, benchmark metrics and annotated overlays from both conditions.
Do not use the familiar same-total demonstration as a blinded assessment field.

## Allocation and tasks

Predeclare a fixed unseen-to-participant field manifest from public data, allocate
different fields to each condition and counterbalance condition order. A participant
must not see the same field in both conditions. Provide the same short practice
before measurement. Freeze field assignments and seeds before sessions; never
remove difficult cases after seeing results.

Task: inspect the four indicated regions and enter the number of nuclei whose
centers fall within each region. Record confirmation, uncertainty and task completion
locally. Participants may stop or mark an unresolvable region. Annotation reference
is loaded only after final export; it is not an infallible biological oracle.

## Predeclared observations

Primary: mean absolute local count error across the four assigned regions, relative
to the saved annotation-centroid reference. Secondary: elapsed completion time,
wrong-direction count changes, unresolved regions, and explanation comprehension.
Count errors are distinct from pixel/instance segmentation errors. A correct total
can still conceal opposing instance mistakes.

Keep all completed/failed tasks with reasons. Analyze paired participant summaries,
show individual distributions and uncertainty; avoid treating tiles as independent
participants. With a six-person pilot, report descriptive observations and limited
scope, not population-wide or clinical claims. Predeclare any later confirmatory
sample size and analysis before collecting it.

## Records and release gate

Local pseudonymous JSON/CSV exports should identify condition, field hash,
configuration, order, start/end, entered counts, uncertainty and completion. Provide
participants a clear retention choice. Publish only appropriately consented,
non-identifying aggregates. Do not fabricate sessions, simulate people, or substitute
algorithmic oracle correction for observed human behavior.

No recruitment, consent, study-mode implementation or human result is implied by
this document. The owner released the video hold; delivery is documented in `demo/README.md`.
This changes no reader-study status or benefit claim.
