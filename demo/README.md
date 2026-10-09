# EurekaDev demo delivery

The owner authorized completed-video publication on October 8. Original media
is retained locally in `demo-video/dist/`; reviewed media is separate under
`demo-video/reviewed/`. Large video/audio files stay outside Git.

The reviewed master is **3:35**, 1920×1080 at 30 fps. A full decode passed,
with 39 burned caption cues and a separately decoded 720p backup. The original
owner master remains unchanged. Exact media hashes and audio measurements are
in `evaluation/checks/video-verification.json`; `captions.srt` is the matching
caption sidecar. `youtube-metadata.json` contains accurate unlisted-video metadata.

## Verified delivery — October 9

[YouTube demo](https://www.youtube.com/watch?v=nik8WtPUrUc), unlisted and embeddable.
The guarded reset retry succeeded at 07:05 UTC after the first quota rejection.
YouTube API readback reports processed/HD and succeeded processing. Public metadata
reports 215 seconds; the API rounds this to 216 seconds, both below four minutes.
An anonymous 1080p/audio opening sample (10.033 seconds) was retrieved and decoded.
This is scoped media-access evidence, not full browser viewing or all-region proof.
Captions are burned into the picture; no separate YouTube caption track exists.
Devpost authenticated and fresh public-rendered readbacks show the same video URL.
The competition entry remains unsubmitted. Do not upload another copy.

Evidence: `evaluation/checks/youtube-api-readback.json`, `youtube-playback.json`,
and `youtube-upload.json`. The one-shot timer has fired; preserve the recorded ID.

The guarded upload script remains available for recovery diagnostics:

```bash
python scripts/retry_youtube_upload.py
```

It refuses to repeat this successful upload.

The script checks the reviewed hash and unlisted visibility, holds a process
lock, and retries only a confirmed quota rejection after its recorded reset.
It records an uncertain state before sending the request and refuses to repeat
an uncertain or successful attempt. Raw connector responses stay in ignored,
protected files. Its parser/reset guards passed six assertions, including a
daylight-saving check, and a pre-reset invocation made no API call.

Preserve any returned video ID. Verify status, processing, duration, and link
playback before attaching it to Devpost. If uploading through the browser
instead, stop the pending timer and record that video's ID before continuing.
Do not claim an upload, Devpost attachment, or competition submission from local
media or this prepared command. See `docs/hackathon/video-review.md` for review
scope and the exact media hash in `evaluation/checks/video-verification.json`.
