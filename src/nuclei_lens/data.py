"""BBBC039 evaluation I/O. Ground truth is never imported by inference."""

from __future__ import annotations

from hashlib import sha256
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

import numpy as np
from PIL import Image
from skimage.measure import label

ARCHIVES = {
    "images": "6f30a5d4fe38c928ded972704f085975f8dc0d65d9aa366df00e5a9d449fddd7",
    "masks": "f9e6043d8ca56344a4886f96a700d804d6ee982f31e2b2cd3194af2a053c2710",
    "metadata": "a2c1f900bed9ba92a99553efd4c2ae98598433691c7401d818653ab61110deb2",
}


class Dataset:
    def __init__(self, root: str | Path = "data/raw/BBBC039", verify: bool = True):
        self.root = Path(root)
        if verify:
            for name, expected in ARCHIVES.items():
                path = self.root / f"{name}.zip"
                if not path.exists():
                    raise FileNotFoundError(f"Missing {path}. Run python scripts/download_data.py.")
                if sha256(path.read_bytes()).hexdigest() != expected:
                    raise ValueError(f"Dataset archive {name} failed SHA-256 verification.")
        with ZipFile(self.root / "metadata.zip") as archive:
            self.splits = {
                name: archive.read(f"metadata/{name}.txt").decode("utf-8").splitlines()
                for name in ("training", "validation", "test")
            }
        for names in self.splits.values():
            if len(names) != len(set(names)) or any(Path(name).name != name for name in names):
                raise ValueError("Unsafe or duplicate filename in official split metadata.")
        sets = {name: set(names) for name, names in self.splits.items()}
        if sets["training"] & sets["validation"] or sets["training"] & sets["test"] or sets["validation"] & sets["test"]:
            raise ValueError("Official partitions unexpectedly overlap.")
        self.images = ZipFile(self.root / "images.zip")
        self.masks = ZipFile(self.root / "masks.zip")

    def close(self) -> None:
        self.images.close()
        self.masks.close()

    def __enter__(self) -> Dataset:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def filenames(self, split: str) -> list[str]:
        if split not in self.splits:
            raise ValueError("Split must be training, validation, or test.")
        return list(self.splits[split])

    def image_bytes(self, filename: str) -> bytes:
        if not any(filename in names for names in self.splits.values()):
            raise ValueError("Filename is not in the pinned official dataset manifest.")
        return self.images.read("images/" + Path(filename).with_suffix(".tif").name)

    def image(self, filename: str) -> np.ndarray:
        with Image.open(BytesIO(self.image_bytes(filename))) as image:
            return np.asarray(image).copy()

    def annotations(self, filename: str) -> np.ndarray:
        if not any(filename in names for names in self.splits.values()):
            raise ValueError("Filename is not in the pinned official dataset manifest.")
        with Image.open(BytesIO(self.masks.read("masks/" + filename))) as mask:
            raster = np.asarray(mask)
        # Dataset-author decoder: connected components of equal values in the
        # FIRST channel (8-connectivity). Colors are reused for separated nuclei.
        # https://gist.github.com/jccaicedo/15e811722fca51e3ae90e8b43057f075
        return label(raster[..., 0], connectivity=2, background=0).astype(np.int32)
