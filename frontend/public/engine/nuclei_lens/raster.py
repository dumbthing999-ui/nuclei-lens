"""Bounded image decoding and transparent rendering of actual analysis masks."""

from __future__ import annotations

import base64
import struct
import zlib
from io import BytesIO
from typing import Any

import numpy as np
from skimage.segmentation import find_boundaries

from . import __version__
from .core import MAX_PIXELS, MAX_SIDE, validate_image

MAX_FILE_BYTES = 10 * 1024 * 1024


def decode_image(payload: bytes) -> np.ndarray:
    from PIL import Image, UnidentifiedImageError

    if not payload or len(payload) > MAX_FILE_BYTES:
        raise ValueError("Use an image file smaller than 10 MB.")
    try:
        with Image.open(BytesIO(payload)) as image:
            if image.format not in {"PNG", "TIFF", "JPEG"}:
                raise ValueError("Supported formats: PNG, TIFF, and JPEG.")
            width, height = image.size
            if width * height > MAX_PIXELS or max(width, height) > MAX_SIDE:
                raise ValueError("Image must be at most 1,048,576 pixels and 2,048 pixels per side.")
            if getattr(image, "n_frames", 1) != 1:
                raise ValueError("Use a single two-dimensional field, not a multi-frame file.")
            if image.mode in {"RGB", "RGBA", "P", "CMYK"}:
                image = image.convert("L")
            result = np.asarray(image).copy()
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as exc:
        raise ValueError("The image could not be decoded safely.") from exc
    validate_image(result)
    return result


def png_bytes(array: np.ndarray) -> bytes:
    """Encode bounded 8-bit arrays without a browser image-decoder dependency."""
    if array.dtype != np.uint8 or array.ndim not in {2, 3}:
        raise ValueError("PNG output must be an 8-bit grayscale/RGB/RGBA array.")
    channels = 1 if array.ndim == 2 else array.shape[2]
    if channels not in {1, 3, 4}:
        raise ValueError("Unsupported PNG channel count.")
    height, width = array.shape[:2]
    color_type = {1: 0, 3: 2, 4: 6}[channels]

    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))

    rows = np.ascontiguousarray(array).reshape(height, width * channels)
    scanlines = np.column_stack((np.zeros(height, dtype=np.uint8), rows)).tobytes()
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, color_type, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(scanlines, 6)) + chunk(b"IEND", b""))


def outline_png(mask: np.ndarray, color: tuple[int, int, int]) -> bytes:
    rgba = np.zeros((*mask.shape, 4), dtype=np.uint8)
    boundary = find_boundaries(mask, mode="inner")
    rgba[boundary, :3] = color
    rgba[boundary, 3] = 240
    return png_bytes(rgba)


def serialize(result: dict[str, Any], assets: bool = True) -> dict[str, Any]:
    public = {key: value for key, value in result.items()
              if key not in {"normalized", "masks", "boundary_uncertainty"}}
    public["software_version"] = __version__
    public["limitations"] = [
        "Sensitivity is not a calibrated confidence interval.",
        "Stable-but-wrong segmentations can escape every probe.",
        "Use nucleus-stained fluorescence images; other image types are outside the evaluated scope.",
        "A review flag is an ambiguity, not proof of an error.",
    ]
    if assets:
        def encode(data: bytes) -> str:
            return base64.b64encode(data).decode("ascii")
        public["image_png"] = encode(png_bytes(np.round(result["normalized"] * 255).astype(np.uint8)))
        public["outline_pngs"] = [
            encode(outline_png(mask, (115, 232, 207) if index == 0 else (255, 184, 103)))
            for index, mask in enumerate(result["masks"])
        ]
        # Lossless instance IDs enable explicit local mask review. Inference and
        # frozen evaluation are unchanged; no annotations enter these assets.
        public["label_maps"] = {
            "encoding": "zlib-base64-uint32-le",
            "runs": [encode(zlib.compress(np.asarray(mask, dtype="<u4").tobytes(), 6))
                     for mask in result["masks"]],
        }
        uncertainty = result["boundary_uncertainty"]
        rgba = np.zeros((*uncertainty.shape, 4), dtype=np.uint8)
        rgba[..., :3] = (121, 156, 255)
        rgba[..., 3] = np.round(uncertainty * 210).astype(np.uint8)
        public["boundary_png"] = encode(png_bytes(rgba))
    return public
