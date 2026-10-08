# EurekaDev demo delivery

The owner authorized completed-video publication on October 8. Original media
is retained locally in `demo-video/dist/`; reviewed media is separate under
`demo-video/reviewed/`. Large video/audio files stay outside Git.

The reviewed master is **3:35**, 1920×1080 at 30 fps. A full decode passed,
with 39 burned caption cues and a separately decoded 720p backup. The original
owner master remains unchanged. Exact media hashes and audio measurements are
in `evaluation/checks/video-verification.json`; `captions.srt` is the matching
caption sidecar. `youtube-metadata.json` contains accurate unlisted-video metadata.

An actual Composio upload was rejected with HTTP 429 `rateLimitExceeded` for
**Video Uploads per day**. Earlier channel reads separately returned HTTP 403
`quotaExceeded`. Neither response establishes a successful upload. YouTube's
[current quota documentation](https://developers.google.com/youtube/v3/determine_quota_cost)
places video uploads in a separate daily bucket and resets quotas at midnight
Pacific time.

A single local timer is verified active for October 9, 2026, **12:35 PM IST**
(07:05 UTC). It runs the guarded retry below. The computer and user session must
remain running; this transient timer is not a guaranteed scheduler across reboot.
It does not automatically attach a video to Devpost. Check its actual result in
`evaluation/checks/youtube-upload.json` before doing anything else.

After the recorded reset time, the same guarded retry can be run manually:

```bash
python scripts/retry_youtube_upload.py
```

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
