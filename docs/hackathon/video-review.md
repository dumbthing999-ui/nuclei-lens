# Completed-video review

The owner explicitly authorized use and upload of the completed demo on October 8.
The original 214.167-second master is preserved at
`demo-video/dist/eurekadev-final.mp4`, SHA-256
`cf07f35bd59174c7b7fae33fd057f55193576210a74e01d2ae43c9fdaff72d70`.
A separate reviewed version is complete from actual product footage, corrected
supporting slides, and corrected narration. No frozen scientific inference or
evaluation source is changed.

## Corrections completed before publication

| Original presentation issue | Reviewed presentation | Authoritative evidence |
|---|---|---|
| Schematic nuclei could look like real captured microscopy | Opening explicitly labels the animation as a schematic | Owner video source animation and actual browser captures in scenes 5–6 |
| Arbitrary field-grid positions and “OK” labels | Actual per-image order and count differences | `evaluation/test/per-image.json` |
| FP/FN labeled as known over-splits/merges or unique misidentified cells | 50 FP + 50 FN are unmatched instance error mass, not a count of distinct biological cells | `evaluation/test/count-cancellation.json` |
| Graph edge cutoff called IoU ≥ 0.45 | Intersection divided by smaller area ≥ 0.45 | `src/nuclei_lens/graph.py` |
| Sensitivity candidates called verified | Candidates remain hypotheses; human choices are unvalidated | `frontend/src/masks.ts`, `docs/INNOVATION.md` |
| Example JSON displayed as an actual audit, with an empty-file hash and invented mask ID | Abbreviated excerpt of the real automated workflow audit | `artifacts/mask-edit-audit-smoke.json` |
| Export dimensions 670×670 | Bundled witness field is 696×520 | `frontend/public/samples/training-001.json` |
| Unchecked native compatibility with external tools | uint32 round trip is verified; external integrations are untested | Existing mask TIFF smoke/equality evidence |
| Absolute privacy and zero network transmission claims | Local uploaded-image analysis; hosting/runtime downloads use the network | `frontend/src/engine-worker.js`, `docs/security-review.md` |
| Unmeasured 45 MB memory and SIMD claims | Remove unsupported memory/SIMD figures | No source measurement supported the claims |
| Native 3.45 s median and 5.76 s p95 described as WebAssembly timing | Identify both as native Python observations; p95 is not a guarantee | `evaluation/test/summary.json`, `docs/TEST_REPORT.md` |
| Review ranking could imply test-selected policy | State validation selection before frozen test inference | `evaluation/frozen/`, `docs/DECISIONS.md` |
| Pathology, instant biological anomaly detection, universal device support | Research/education scope, tested Chromium/Firefox workflows, unvalidated human benefit and clinical use | `docs/READER_STUDY_PROTOCOL.md`, existing browser evidence |
| Self-awarded 9.83/10 video score treated as validation | Exclude that score from repository/Devpost claims | No independent human assessment supports it |

## Verified media

The reviewed master is `demo-video/reviewed/eurekadev-reviewed.mp4`: exactly
215 seconds, 1920×1080 at 30 fps, H.264/AAC stereo at 48 kHz, 60,856,253 bytes.
SHA-256: `8f4a0c306d2e0027992954d7da28abda90026d2c78cbd859940890fc4ab69f85`.
Full decoding passed; 39 burned caption cues are monotonic and end at212.580s.
Measured audio is -16.22 LUFS integrated, -1.45 dBTP, and7.7 LU loudness range.
The 720p backup also fully decodes; its separate hash is recorded in
`evaluation/checks/video-verification.json`. Final supporting frames and the
contact sheet were visually inspected.

Existing scene5/6 browser recordings had7/8seconds of blank startup. Those
starts are trimmed at original playback speed, with a visible startup-trimmed
label. The actual recorded undo sequence is included. This edit provides no
measurement of browser latency. Captions are available as `demo/captions.srt`.

## Delivery state

GitHub publishing works through the existing Composio account. The YouTube account
is also connected. Both channel read paths returned HTTP403 `quotaExceeded`;
the actual upload subsequently returned HTTP429 `rateLimitExceeded` for
**Video Uploads per day**. This is a verified rejection, with no video ID.
A single guarded local retry is scheduled for October9 at12:35PM IST. It depends
on the running computer/user session and available connector quota. No upload or
public playback can be claimed. Visibility is unlisted; metadata is in
`demo/youtube-metadata.json`, and actual state in `evaluation/checks/youtube-upload.json`.

The owner authorized use of the connected Devpost account email for organizer
contact. Its value stays out of the public repository. The video URL remains
missing; custom entry answers are prepared. Track is Coding; category is Biology/Medical and
Environmental Science. The available MCP exposes custom entry answers through
final submit, not a separate draft-answer save. Do not invoke final submit just
to populate draft fields. The owner said the browser was ready, but supported
discovery still returned no browser; diagnostics found no running Chrome session.
The owner has been asked to connect Chrome/Chromium with the ChatGPT extension.
No legal agreement or private contact disclosure has been invented.

Technical media inspection can prove container properties, complete decoding,
caption timing bounds, and selected rendered frames. It does not establish a
human reader study, impact validation, accessibility for every viewer, or a
winning judge score.
