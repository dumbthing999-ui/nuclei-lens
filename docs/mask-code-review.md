# Mask code review — October8,2026

A separate Gemini3.8FlashMedium read-only review received actual mask/UI source.
Its findings were reviewed against implementation and tests, rather than accepted
automatically. A preceding filesystem-based reviewer timed out and produced no
review; it is not counted as completed evidence. This is AI-assisted code review,
not an independent human/security assessment.

## Changes made

- Guard failed sample requests by sequence so an old failure cannot clear newer
  busy/error state. Upload reads now set busy immediately and handle read failure.
- Tag worker results/status/errors with request IDs; reject stale messages and
  messages from terminated/replaced worker instances.
- Delay audit Blob URL revocation, matching the TIFF download implementation.
- Align TIFF pixel-strip start to4bytes as a conservative compatibility choice.
- Add a uint32 ID-exhaustion rejection test.

## Findings rejected or qualified

- Claimed transposed zoom: core bbox is explicitly x0,y0,x1,y1 and conversion is
  correct. Fractional number strings also parse normally; no demonstrated defect.
- Claimed SHORT-valued TIFF tags corrupt the file: count1 SHORT fits in the TIFF
  value slot. Fresh buffer padding is zero. Independent uint32 TIFF readback passes.
  Existing134byte strip offset is word aligned; no reader corruption was reproduced.
- Claimed inability to repeatedly refine an edited component: deliberate scope and
  conflict policy. Undo first; baseline graph events must not silently target newIDs.
- Claimed canceling a closed readable stream must reject: no failure reproduced
  in Chromium or Node tests. Expansion failures already propagate and are bounded.

Tests cover actual same-total pixel edits, TIFF/audit integrity, exact undo,
compatible reruns, conflicting and invalid components. Tally and mask counts remain
separate. Broader browser/physical-device testing remains outstanding.
