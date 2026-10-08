"""Tests for optional local multi-model mask runner.

NOTE: These tests verify process isolation, timeout enforcement, geometry validation,
integer label safety, bounded pixel restrictions, and provenance hashing.
They use mock worker adapters and do NOT execute real neural models or download heavy weights.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest
import tifffile

# Allow importing scripts directory when run from repository root or pytest
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.run_model_masks import (  # noqa: E402 - repository script import after explicit root path
    compute_sha256,
    run_model_inference_in_child,
    run_pipeline,
    validate_input_image_file,
    validate_instance_label_array,
)


@pytest.fixture
def sample_image_path(tmp_path: Path) -> Path:
    img_path = tmp_path / "test_nuclei.tif"
    # Create simple 64x64 uint16 synthetic image
    arr = (np.random.RandomState(42).rand(64, 64) * 5000).astype(np.uint16)
    tifffile.imwrite(img_path, arr)
    return img_path


def test_sha256_computation(tmp_path: Path):
    test_file = tmp_path / "sample.bin"
    test_file.write_bytes(b"NucleiLens provenance test")
    hash_from_file = compute_sha256(test_file)
    hash_from_bytes = compute_sha256(b"NucleiLens provenance test")
    assert hash_from_file == hash_from_bytes
    assert len(hash_from_file) == 64


def test_input_validation_bounds(tmp_path: Path):
    # Oversized image (> 1,048,576 pixels)
    oversized = tmp_path / "oversized.tif"
    arr = np.zeros((1025, 1025), dtype=np.uint8)
    tifffile.imwrite(oversized, arr)
    with pytest.raises(ValueError, match="exceed bounds"):
        validate_input_image_file(oversized)

    # Too small image (< 32x32)
    too_small = tmp_path / "tiny.tif"
    tifffile.imwrite(too_small, np.zeros((16, 16), dtype=np.uint8))
    with pytest.raises(ValueError, match="at least 32x32"):
        validate_input_image_file(too_small)


def test_validate_instance_labels():
    expected_shape = (64, 64)
    # Valid uint32 labels
    labels = np.zeros(expected_shape, dtype=np.uint32)
    labels[10:20, 10:20] = 1
    labels[30:40, 30:40] = 2
    res = validate_instance_label_array(labels, expected_shape)
    assert res.dtype == np.uint32
    assert res.shape == expected_shape

    # Negative labels rejected
    labels_neg = np.zeros(expected_shape, dtype=np.int32)
    labels_neg[0, 0] = -1
    with pytest.raises(ValueError, match="non-negative"):
        validate_instance_label_array(labels_neg, expected_shape)

    # Float labels rejected (prevent non-integer mask confusion)
    labels_float = np.zeros(expected_shape, dtype=np.float32)
    with pytest.raises(ValueError, match="must be integer"):
        validate_instance_label_array(labels_float, expected_shape)

    # Wrong shape rejected
    with pytest.raises(ValueError, match="does not match input"):
        validate_instance_label_array(labels, (32, 32))


def test_timeout_and_process_termination(sample_image_path: Path):
    """Verify that a hanging model process is killed when exceeding timeout."""
    hanging_script = """\
import time
import sys

# Simulate hanging / unresponsive model worker
time.sleep(30.0)
"""
    with pytest.raises(TimeoutError, match="timed out after 0.5 seconds; process group stopped"):
        run_model_inference_in_child(
            model_name="cellpose_nuclei",
            input_path=sample_image_path,
            expected_shape=(64, 64),
            timeout_seconds=0.5,
            custom_worker_script=hanging_script,
        )


def test_mock_pipeline_execution_and_provenance(sample_image_path: Path, tmp_path: Path):
    """Test full pipeline run using mock worker scripts (no heavy weights)."""
    output_dir = tmp_path / "pipeline_output"

    mock_cellpose_script = """\
import sys
import json
import numpy as np
import tifffile

input_img, out_mask, out_meta = sys.argv[1], sys.argv[2], sys.argv[3]
# Generate mock 2-instance label mask
mask = np.zeros((64, 64), dtype=np.uint32)
mask[5:15, 5:15] = 1
mask[25:35, 25:35] = 2
tifffile.imwrite(out_mask, mask, dtype=np.uint32)

meta = {
    "framework": "cellpose",
    "framework_version": "3.1.0-mock",
    "model_type": "nuclei",
    "diameter_estimated": 17.0,
    "elapsed_seconds": 0.05,
    "device": "cpu",
}
with open(out_meta, "w") as f:
    json.dump(meta, f)
"""

    mock_stardist_script = """\
import sys
import json
import numpy as np
import tifffile

input_img, out_mask, out_meta = sys.argv[1], sys.argv[2], sys.argv[3]
# Generate mock 1-instance label mask
mask = np.zeros((64, 64), dtype=np.uint32)
mask[40:50, 40:50] = 1
tifffile.imwrite(out_mask, mask, dtype=np.uint32)

meta = {
    "framework": "stardist",
    "framework_version": "0.9.2-mock",
    "pretrained_model": "2D_versatile_fluo",
    "elapsed_seconds": 0.04,
    "device": "cpu",
}
with open(out_meta, "w") as f:
    json.dump(meta, f)
"""

    custom_scripts = {
        "cellpose_nuclei": mock_cellpose_script,
        "stardist_2d_fluo": mock_stardist_script,
    }

    provenance = run_pipeline(
        image_path=sample_image_path,
        output_dir=output_dir,
        models=["cellpose_nuclei", "stardist_2d_fluo"],
        timeout_seconds=5.0,
        custom_worker_scripts=custom_scripts,
    )

    # Check files created
    assert (output_dir / "cellpose_nuclei_mask.tif").exists()
    assert (output_dir / "stardist_2d_fluo_mask.tif").exists()
    assert (output_dir / "provenance.json").exists()

    # Validate output TIFF masks
    cp_mask = tifffile.imread(output_dir / "cellpose_nuclei_mask.tif")
    assert cp_mask.dtype == np.uint32
    assert cp_mask.shape == (64, 64)
    assert set(np.unique(cp_mask)) == {0, 1, 2}

    sd_mask = tifffile.imread(output_dir / "stardist_2d_fluo_mask.tif")
    assert sd_mask.dtype == np.uint32
    assert sd_mask.shape == (64, 64)
    assert set(np.unique(sd_mask)) == {0, 1}

    # Validate provenance honesty
    assert provenance["tool"] == "nucleilens-model-masks"
    assert "disclaimer" in provenance
    assert "No ground-truth status" in provenance["disclaimer"]
    assert provenance["input_image"]["dimensions"] == {"width": 64, "height": 64}
    assert provenance["models"]["cellpose_nuclei"]["instance_count"] == 2
    assert provenance["models"]["stardist_2d_fluo"]["instance_count"] == 1
    assert "mask_file_sha256" in provenance["models"]["cellpose_nuclei"]
    assert "mask_pixel_sha256" in provenance["models"]["cellpose_nuclei"]


def test_uint32_overflow_and_timeout_bounds(sample_image_path):
    for timeout in (float("nan"),float("inf"),0,-1,601):
        with pytest.raises(ValueError, match="timeout"):
            run_model_inference_in_child("cellpose_nuclei",sample_image_path,(64,64),timeout_seconds=timeout)
    labels = np.zeros((2,2),dtype=np.uint64)
    labels[0,0] = 2**32
    with pytest.raises(ValueError,match="32-bit"):
        validate_instance_label_array(labels,(2,2))


def test_partial_run_is_not_claimed_complete(sample_image_path,tmp_path):
    import json
    good = """import sys,json,numpy as np,tifffile
mask=np.zeros((64,64),dtype=np.uint32)
mask[4:8,4:8]=1
tifffile.imwrite(sys.argv[2],mask)
open(sys.argv[3],'w').write(json.dumps({'framework':'explicit-test-adapter'}))
"""
    output=tmp_path/'partial'
    with pytest.raises(RuntimeError,match="returncode"):
        run_pipeline(sample_image_path,output,["cellpose_nuclei","stardist_2d_fluo"],custom_worker_scripts={"cellpose_nuclei":good,"stardist_2d_fluo":"raise RuntimeError('intentional adapter failure')"})
    record=json.loads((output/'provenance.json').read_text())
    assert record['run_status']=='partial'
    assert record['models']['cellpose_nuclei']['status']=='success'
    assert record['models']['stardist_2d_fluo']['status']=='failed'
    with pytest.raises(ValueError,match="empty"):
        run_pipeline(sample_image_path,output,["cellpose_nuclei"])


def test_cleanup_tolerates_already_exited_process_group(sample_image_path,monkeypatch):
    import subprocess

    from scripts import run_model_masks as module
    class Process:
        pid=12345
        calls=0
        def communicate(self,timeout=None):
            self.calls+=1
            if self.calls==1:
                raise subprocess.TimeoutExpired('test-adapter',timeout)
            return '', ''
    monkeypatch.setattr(module.subprocess,'Popen',lambda *args,**kwargs:Process())
    def exited(*args):
        raise ProcessLookupError('simulated already-exited group')
    monkeypatch.setattr(module.os,'killpg',exited)
    with pytest.raises(TimeoutError,match='process group stopped'):
        run_model_inference_in_child('cellpose_nuclei',sample_image_path,(64,64),timeout_seconds=0.5)
