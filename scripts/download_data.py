#!/usr/bin/env python3
"""Fetch only pinned, public CC0 benchmark archives and verify their hashes."""

from hashlib import sha256
from pathlib import Path
from urllib.request import urlopen

ARCHIVES = {
    "images": "6f30a5d4fe38c928ded972704f085975f8dc0d65d9aa366df00e5a9d449fddd7",
    "masks": "f9e6043d8ca56344a4886f96a700d804d6ee982f31e2b2cd3194af2a053c2710",
    "metadata": "a2c1f900bed9ba92a99553efd4c2ae98598433691c7401d818653ab61110deb2",
}
root = Path(__file__).resolve().parents[1] / "data/raw/BBBC039"
root.mkdir(parents=True, exist_ok=True)
for name, expected in ARCHIVES.items():
    target = root / f"{name}.zip"
    if target.exists() and sha256(target.read_bytes()).hexdigest() == expected:
        print(f"{name}: verified existing archive")
        continue
    temporary = target.with_suffix(".download")
    try:
        with urlopen(f"https://data.broadinstitute.org/bbbc/BBBC039/{name}.zip", timeout=60) as response:
            with temporary.open("wb") as output:
                while chunk := response.read(1024 * 1024):
                    output.write(chunk)
        if sha256(temporary.read_bytes()).hexdigest() != expected:
            raise ValueError(f"{name}: archive SHA-256 does not match the pinned release")
        temporary.replace(target)
        print(f"{name}: downloaded and verified")
    finally:
        temporary.unlink(missing_ok=True)
