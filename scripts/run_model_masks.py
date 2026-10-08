#!/usr/bin/env python3
"""Run optional external neural instance segmentation models on a single image.

Outputs uint32 instance-label TIFFs and transparent provenance JSON.
Does not claim ground truth, accuracy, or model superiority.
Runs models in isolated, killable subprocesses with configurable deadlines.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

import numpy as np
import tifffile

# Hard bounded constraints matching NucleiLens architecture
MAX_FILE_BYTES = 10 * 1024 * 1024  # 10 MB
MAX_PIXELS = 1_048_576             # 1 Megapixel
MAX_SIDE = 2048
DEFAULT_TIMEOUT_SECONDS = 90.0

SUPPORTED_MODELS = ("cellpose_nuclei", "stardist_2d_fluo")


def compute_sha256(data_or_path: bytes | Path) -> str:
    """Compute hex SHA-256 digest of bytes or a file path."""
    hasher = hashlib.sha256()
    if isinstance(data_or_path, (bytes, bytearray, memoryview)):
        hasher.update(data_or_path)
    else:
        with open(data_or_path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                hasher.update(chunk)
    return hasher.hexdigest()


def validate_input_image_file(path: Path) -> tuple[np.ndarray, str]:
    """Read and validate image bounded constraints.

    Returns the decoded array (2D grayscale) and its file SHA256.
    Rejects files > 10MB, multi-frame images, > 1MP, or non-finite pixels.
    """
    if not path.is_file():
        raise FileNotFoundError(f"Input image file not found: {path}")

    file_size = path.stat().st_size
    if file_size > MAX_FILE_BYTES:
        raise ValueError(
            f"Input file size ({file_size} bytes) exceeds maximum allowed limit of {MAX_FILE_BYTES} bytes (10 MB)."
        )

    file_sha256 = compute_sha256(path)

    # Use PIL for safe dimension / frame checking, matching raster.py
    from PIL import Image, UnidentifiedImageError

    try:
        with Image.open(path) as img:
            if getattr(img, "n_frames", 1) != 1:
                raise ValueError("Use a single two-dimensional field, not a multi-frame file.")
            width, height = img.size
            if width * height > MAX_PIXELS or max(width, height) > MAX_SIDE:
                raise ValueError(
                    f"Image dimensions ({width}x{height} = {width * height} px) exceed bounds "
                    f"of {MAX_PIXELS} pixels and {MAX_SIDE} pixels per side."
                )
            if img.mode in {"RGB", "RGBA", "P", "CMYK"}:
                img = img.convert("L")
            array = np.asarray(img).copy()
    except (UnidentifiedImageError, OSError) as exc:
        raise ValueError(f"Failed to safely decode image: {exc}") from exc

    if array.ndim != 2 or min(array.shape) < 32:
        raise ValueError("Image must be a 2D array of at least 32x32 pixels.")
    if max(array.shape) > MAX_SIDE or array.size > MAX_PIXELS:
        raise ValueError("Image must be at most 1,048,576 pixels and 2,048 pixels per side.")
    if array.dtype.kind not in "buif" or not np.isfinite(array).all():
        raise ValueError("Image pixels must be finite numeric values.")

    return array, file_sha256


def validate_instance_label_array(labels: np.ndarray, expected_shape: tuple[int, int]) -> np.ndarray:
    """Validate that output labels match expected geometry and are non-negative integer IDs."""
    if labels.ndim != 2 or labels.shape != expected_shape:
        raise ValueError(
            f"Output label mask geometry {labels.shape} does not match input image geometry {expected_shape}."
        )
    if not np.issubdtype(labels.dtype, np.integer):
        raise ValueError(f"Output label array must be integer dtype, got {labels.dtype}.")
    if labels.size and int(labels.max()) > 0xffffffff:
        raise ValueError("Instance labels exceed unsigned 32-bit IDs.")
    if (labels < 0).any():
        raise ValueError("Instance labels must be non-negative integers (0 is background).")

    # Enforce uint32 type representation
    if labels.dtype != np.uint32:
        labels = labels.astype(np.uint32)
    return labels


def build_worker_script(model_name: str) -> str:
    """Generate worker Python script executed inside the isolated child process.

    This code communicates strictly through file paths (no unpickling/eval).
    Arguments passed via sys.argv:
    1: input_image_path
    2: output_mask_path
    3: metadata_json_path
    """
    if model_name == "cellpose_nuclei":
        return """\
import sys
import json
import time
import numpy as np
from PIL import Image
import tifffile
from importlib.metadata import version
from pathlib import Path
import hashlib

def weight_hashes(paths):
    result = []
    for value in paths:
        if not isinstance(value, (str, Path)) or not value:
            continue
        path = Path(value)
        if path.is_file():
            result.append({"file":path.name,"sha256":hashlib.sha256(path.read_bytes()).hexdigest(),"bytes":path.stat().st_size})
    return result

input_image_path = sys.argv[1]
output_mask_path = sys.argv[2]
meta_path = sys.argv[3]

with Image.open(input_image_path) as img:
    if img.mode in ("RGB", "RGBA", "P", "CMYK"):
        img = img.convert("L")
    img_arr = np.asarray(img)

# Import Cellpose inside child process
from cellpose import models
import cellpose

t0 = time.perf_counter()
model = models.Cellpose(gpu=False, model_type='nuclei')
masks, flows, styles, diams = model.eval(img_arr, diameter=None, channels=[0, 0])
elapsed = time.perf_counter() - t0

if masks.dtype.kind not in "iu" or (masks < 0).any() or int(masks.max(initial=0)) > 0xffffffff:
    raise ValueError("Invalid model instance IDs")
masks = masks.astype(np.uint32)
tifffile.imwrite(output_mask_path, masks, dtype=np.uint32)

meta = {
    "framework": "cellpose",
    "framework_version": version("cellpose"),
    "torch_version": version("torch"),
    "weight_files": weight_hashes([getattr(model.cp,"pretrained_model",None),getattr(model.sz,"pretrained_size",None)]),
    "parameters": {"gpu":False,"model_type":"nuclei","diameter":None,"channels":[0,0]},
    "model_type": "nuclei",
    "diameter_estimated": float(diams) if isinstance(diams, (int, float, np.floating)) else None,
    "elapsed_seconds": float(elapsed),
    "elapsed_scope": "Model setup, uncached weight download and prediction; framework import excluded.",
    "device": "cpu",
}
with open(meta_path, "w", encoding="utf-8") as f:
    json.dump(meta, f)
"""
    elif model_name == "stardist_2d_fluo":
        return """\
import sys
import json
import time
import numpy as np
from PIL import Image
import tifffile
from importlib.metadata import version
from pathlib import Path
import hashlib

def weight_hashes(paths):
    result = []
    for value in paths:
        if not isinstance(value, (str, Path)) or not value:
            continue
        path = Path(value)
        if path.is_file():
            result.append({"file":path.name,"sha256":hashlib.sha256(path.read_bytes()).hexdigest(),"bytes":path.stat().st_size})
    return result

input_image_path = sys.argv[1]
output_mask_path = sys.argv[2]
meta_path = sys.argv[3]

with Image.open(input_image_path) as img:
    if img.mode in ("RGB", "RGBA", "P", "CMYK"):
        img = img.convert("L")
    img_arr = np.asarray(img).astype(np.float32)

from csbdeep.utils import normalize
from stardist.models import StarDist2D
import stardist

t0 = time.perf_counter()
norm_img = normalize(img_arr, 1, 99.8, axis=(0, 1))
model = StarDist2D.from_pretrained('2D_versatile_fluo')
labels, details = model.predict_instances(norm_img)
elapsed = time.perf_counter() - t0

if labels.dtype.kind not in "iu" or (labels < 0).any() or int(labels.max(initial=0)) > 0xffffffff:
    raise ValueError("Invalid model instance IDs")
labels = labels.astype(np.uint32)
tifffile.imwrite(output_mask_path, labels, dtype=np.uint32)

meta = {
    "framework": "stardist",
    "framework_version": version("stardist"),
    "tensorflow_version": version("tensorflow-cpu"),
    "weight_files": weight_hashes(list(Path(model.logdir).glob("*.h5"))),
    "parameters": {"normalization_percentiles":[1,99.8],"pretrained_model":"2D_versatile_fluo"},
    "pretrained_model": "2D_versatile_fluo",
    "elapsed_seconds": float(elapsed),
    "elapsed_scope": "Model setup, uncached weight download and prediction; framework import excluded.",
    "device": "cpu",
}
with open(meta_path, "w", encoding="utf-8") as f:
    json.dump(meta, f)
"""
    else:
        raise ValueError(f"Unknown model name: {model_name}")


def run_model_inference_in_child(
    model_name: str,
    input_path: Path,
    expected_shape: tuple[int, int],
    python_executable: str = sys.executable,
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
    custom_worker_script: str | None = None,
) -> tuple[np.ndarray, dict[str, Any]]:
    """Execute model segmentation in an isolated, killable local child process.

    Returns the validated (height, width) uint32 label array and child provenance dictionary.
    Guarantees child termination on timeout or unexpected error.
    """
    if not math.isfinite(timeout_seconds) or not 0.1 <= timeout_seconds <= 600:
        raise ValueError("Model timeout must be finite and between 0.1 and 600 seconds.")
    with tempfile.TemporaryDirectory(prefix="nucleilens_model_") as tmpdir:
        tmp_dir_path = Path(tmpdir)
        worker_py = tmp_dir_path / "worker.py"
        output_mask_path = tmp_dir_path / "out_mask.tif"
        metadata_json_path = tmp_dir_path / "out_meta.json"

        script_code = custom_worker_script or build_worker_script(model_name)
        worker_py.write_text(script_code, encoding="utf-8")

        cmd = [
            python_executable,
            str(worker_py),
            str(input_path.resolve()),
            str(output_mask_path.resolve()),
            str(metadata_json_path.resolve()),
        ]

        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            start_new_session=True,
            env={**os.environ,"CUDA_VISIBLE_DEVICES":"","OMP_NUM_THREADS":"2","TF_NUM_INTRAOP_THREADS":"2","TF_NUM_INTEROP_THREADS":"2"},
        )

        try:
            stdout, stderr = proc.communicate(timeout=timeout_seconds)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass  # The process group already exited between timeout and cleanup.
            stdout, stderr = proc.communicate()
            raise TimeoutError(
                f"Model execution '{model_name}' timed out after {timeout_seconds} seconds; process group stopped."
            )
        except BaseException:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            proc.wait()
            raise

        if proc.returncode != 0:
            raise RuntimeError(
                f"Model execution failed with returncode {proc.returncode}.\n"
                f"STDOUT (tail):\n{stdout[-2000:]}\nSTDERR (tail):\n{stderr[-4000:]}"
            )

        if not output_mask_path.exists() or not metadata_json_path.exists():
            raise FileNotFoundError(
                "Worker completed with returncode 0 but failed to create required outputs."
            )

        labels = tifffile.imread(output_mask_path)
        labels = validate_instance_label_array(labels, expected_shape)

        with open(metadata_json_path, "r", encoding="utf-8") as f:
            worker_meta = json.load(f)

        return labels, worker_meta


def run_pipeline(
    image_path: Path,
    output_dir: Path,
    models: list[str] | tuple[str, ...],
    python_executable: str = sys.executable,
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
    custom_worker_scripts: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Run specified models on input image, write outputs, and generate provenance JSON.

    Outputs:
      <output_dir>/<model>_mask.tif
      <output_dir>/provenance.json
    """
    if not models or len(set(models)) != len(models):
        raise ValueError("Choose at least one model without duplicates.")
    for m in models:
        if m not in SUPPORTED_MODELS:
            raise ValueError(f"Unsupported model: {m}. Choose from {SUPPORTED_MODELS}")

    image_path = image_path.resolve()
    image_array, input_file_sha256 = validate_input_image_file(image_path)
    height, width = image_array.shape

    # Bounded pixel hash (raw input byte hash vs pixel content hash)
    input_pixel_sha256 = hashlib.sha256(image_array.tobytes()).hexdigest()

    output_dir = output_dir.resolve()
    if output_dir.exists() and any(output_dir.iterdir()):
        raise ValueError("Output directory must be empty to preserve prior model runs.")
    output_dir.mkdir(parents=True, exist_ok=True)

    provenance_models: dict[str, Any] = {}

    overall_provenance = {
        "tool": "nucleilens-model-masks",
        "description": "Optional local multi-model instance segmentation runner for comparative review",
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "input_image": {
            "path": str(image_path.name),
            "file_sha256": input_file_sha256,
            "pixel_sha256": input_pixel_sha256,
            "dimensions": {"width": width, "height": height},
            "pixel_count": int(image_array.size),
            "dtype": str(image_array.dtype),
        },
        "models": provenance_models,
        "requested_models": list(models),
        "run_status": "running",
        "disclaimer": (
            "Model outputs are non-authoritative machine predictions for comparison and review only. "
            "No ground-truth status, accuracy claim, or algorithmic superiority is asserted. "
            "Instance masks have not been verified by a certified human reader."
        ),
    }

    def save_progress():
        target = output_dir / "provenance.json"
        temporary = output_dir / "provenance.json.tmp"
        temporary.write_text(json.dumps(overall_provenance, indent=2) + "\n")
        temporary.replace(target)

    save_progress()
    for model_name in models:
        custom_script = (custom_worker_scripts or {}).get(model_name)
        try:
            with tempfile.TemporaryDirectory(prefix="nucleilens_input_") as canonical_dir:
                canonical = Path(canonical_dir) / "validated-input.tif"
                tifffile.imwrite(canonical, image_array)
                labels, worker_meta = run_model_inference_in_child(
                    model_name=model_name,
                    input_path=canonical,
                    expected_shape=(height, width),
                    python_executable=python_executable,
                    timeout_seconds=timeout_seconds,
                    custom_worker_script=custom_script,
                )
        except BaseException as exc:
            provenance_models[model_name] = {"status":"failed","error_type":type(exc).__name__}
            overall_provenance["run_status"] = "partial" if any(v.get("status")=="success" for v in provenance_models.values()) else "failed"
            save_progress()
            raise

        mask_out_path = output_dir / f"{model_name}_mask.tif"
        tifffile.imwrite(mask_out_path, labels, dtype=np.uint32)

        # Hash and count statistics
        mask_file_sha256 = compute_sha256(mask_out_path)
        mask_pixel_sha256 = hashlib.sha256(labels.astype("<u4", copy=False).tobytes()).hexdigest()
        unique_labels = np.unique(labels)
        instance_count = int(np.count_nonzero(unique_labels > 0))

        provenance_models[model_name] = {
            "status": "success",
            "instance_count": instance_count,
            "mask_tiff_path": str(mask_out_path.name),
            "mask_file_sha256": mask_file_sha256,
            "mask_pixel_sha256": mask_pixel_sha256,
            "worker_provenance": worker_meta,
        }
        save_progress()

    overall_provenance["run_status"] = "completed"
    prov_path = output_dir / "provenance.json"
    with open(prov_path, "w", encoding="utf-8") as f:
        json.dump(overall_provenance, f, indent=2)

    return overall_provenance


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run optional local neural instance segmentation models (Cellpose / StarDist) on a single image."
    )
    parser.add_argument("image", type=Path, help="Path to input 2D image file (TIFF, PNG, JPEG)")
    parser.add_argument(
        "--output-dir",
        "-o",
        type=Path,
        default=Path("model_output"),
        help="Directory to write output uint32 label TIFFs and provenance.json (default: ./model_output)",
    )
    parser.add_argument(
        "--models",
        nargs="+",
        choices=SUPPORTED_MODELS,
        default=list(SUPPORTED_MODELS),
        help=f"Models to execute (default: {' '.join(SUPPORTED_MODELS)})",
    )
    parser.add_argument(
        "--python",
        type=str,
        default=sys.executable,
        help="Path to Python executable in environment containing cellpose/stardist dependencies",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT_SECONDS,
        help=f"Per-model execution timeout in seconds (default: {DEFAULT_TIMEOUT_SECONDS})",
    )

    args = parser.parse_args()

    try:
        prov = run_pipeline(
            image_path=args.image,
            output_dir=args.output_dir,
            models=args.models,
            python_executable=args.python,
            timeout_seconds=args.timeout,
        )
        print(f"Successfully processed image. Provenance written to {args.output_dir / 'provenance.json'}")
        for m, details in prov["models"].items():
            print(f"  [{m}] Detected {details['instance_count']} instances -> {details['mask_tiff_path']}")
        return 0
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
