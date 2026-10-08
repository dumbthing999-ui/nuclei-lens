#!/usr/bin/env python3
"""Retry a confirmed quota rejection once, retaining an uncertain result for review."""

import fcntl
import hashlib
import json
import os
import re
import subprocess
from datetime import datetime, time, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "evaluation/checks/youtube-upload.json"
PRIVATE = ROOT / ".firecrawl"


def save(path, value, private=False):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n")
    if private:
        temporary.chmod(0o600)
    temporary.replace(path)


def next_reset(now):
    pacific = now.astimezone(ZoneInfo("America/Los_Angeles"))
    tomorrow = pacific.date() + timedelta(days=1)
    return datetime.combine(tomorrow, time(0, 5), pacific.tzinfo).astimezone(timezone.utc)


def video_resource(value):
    if isinstance(value, str):
        try:
            return video_resource(json.loads(value))
        except (ValueError, RecursionError):
            return None
    if isinstance(value, dict):
        candidate = value.get("id") or value.get("video_id") or value.get("videoId")
        if isinstance(candidate, str) and re.fullmatch(r"[A-Za-z0-9_-]{11}", candidate):
            if value.get("kind") == "youtube#video" or "snippet" in value or "video_id" in value or "videoId" in value:
                return candidate
        for child in value.values():
            found = video_resource(child)
            if found:
                return found
    if isinstance(value, list):
        for child in value:
            found = video_resource(child)
            if found:
                return found
    return None


def main():
    PRIVATE.mkdir(exist_ok=True)
    lock = PRIVATE / "youtube-upload.lock"
    with lock.open("a") as handle:
        lock.chmod(0o600)
        fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        previous = json.loads(STATE.read_text())
        if previous.get("phase") != "rejected_quota":
            print("No retry: last attempt was not a confirmed quota rejection.")
            return
        now = datetime.now(timezone.utc)
        if now < datetime.fromisoformat(previous["retry_not_before"]):
            print("No retry: waiting for the recorded quota reset.")
            return
        verification = json.loads((ROOT / "evaluation/checks/video-verification.json").read_text())
        video = ROOT / verification["video_path"]
        if hashlib.sha256(video.read_bytes()).hexdigest() != verification["sha256"]:
            raise ValueError("Reviewed video hash changed; review before upload.")
        metadata = ROOT / "demo/youtube-metadata.json"
        if json.loads(metadata.read_text())["privacyStatus"] != "unlisted":
            raise ValueError("Unexpected upload visibility; review before upload.")
        state = {
            "checked_at": now.isoformat(),
            "sha256": verification["sha256"],
            "tool": "YOUTUBE_MULTIPART_UPLOAD_VIDEO",
            "phase": "completion_uncertain",
            "reason": "Upload started; inspect the protected result before any retry.",
            "attempt_count": previous.get("attempt_count", 1) + 1,
            "public_playback_verified": False,
            "devpost_video_attached": False,
        }
        save(STATE, state)
        save(PRIVATE / "youtube-upload-started.json", state, private=True)
        executable = Path.home() / ".local/bin/composio"
        try:
            result = subprocess.run(
                [str(executable), "execute", state["tool"], "--file", str(video), "-d", "@" + str(metadata)],
                cwd=ROOT, capture_output=True, text=True, timeout=900,
            )
        except subprocess.TimeoutExpired:
            print("Upload outcome uncertain after timeout; do not repeat automatically.")
            return
        for suffix, content in (("json", result.stdout), ("stderr", result.stderr)):
            target = PRIVATE / ("youtube-upload-cli." + suffix)
            descriptor = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
            with os.fdopen(descriptor, "w") as stream:
                stream.write(content)
            target.chmod(0o600)
        state.update(checked_at=datetime.now(timezone.utc).isoformat(), return_code=result.returncode)
        try:
            response = json.loads(result.stdout)
        except ValueError:
            response = {}
        identity = video_resource(response.get("data"))
        if response.get("successful") is True and identity:
            state.update(phase="uploaded", video_id=identity, url="https://www.youtube.com/watch?v=" + identity)
            state.pop("reason", None)
        else:
            error_text = json.dumps(response.get("error")) + json.dumps(response.get("data"))
            if response.get("successful") is False and ("quotaExceeded" in error_text or "Video Uploads per day" in error_text):
                state.update(
                    phase="rejected_quota", reason="YouTube rejected the request because its API quota is exhausted.",
                    retry_not_before=next_reset(datetime.now(timezone.utc)).isoformat(),
                )
        save(STATE, state)
        save(PRIVATE / "youtube-upload-started.json", state, private=True)
        print(json.dumps(state))


if __name__ == "__main__":
    main()
