import json
from io import BytesIO

import numpy as np
import pytest
from PIL import Image

from nuclei_lens.core import Config, analyze, normalize, probe_specs, tile_counts
from nuclei_lens.raster import decode_image, serialize


def test_empty_image_has_no_detections():
    result = analyze(np.zeros((64, 64), dtype=np.uint16))
    assert result["raw_count"] == result["flagged_regions"] == 0
    assert result["sensitivity_range"] == [0, 0]
    assert len(result["regions"]) == 20
    assert len(serialize(result)["outline_pngs"]) == 9
    assert json.loads(json.dumps(serialize(result)))["quality"]["weak_signal"] is True


def test_two_disks_are_deterministic():
    y, x = np.mgrid[:96, :96]
    image = (((x - 25)**2 + (y - 35)**2 < 100) | ((x - 65)**2 + (y - 65)**2 < 100)).astype(float)
    a, b = analyze(image), analyze(image)
    assert a["raw_count"] == b["raw_count"] == 2
    assert a["input_hash"] == b["input_hash"]
    assert a["regions"] == b["regions"]
    assert tile_counts(a["masks"][0]).sum() == 2


@pytest.mark.parametrize("image", [np.zeros((20, 40)), np.zeros((32, 32, 3)), np.full((32, 32), np.nan), np.zeros((2049, 32))])
def test_invalid_pixels_or_dimensions(image):
    with pytest.raises(ValueError):
        normalize(image)


@pytest.mark.parametrize("factor", [0.4, 1.5])
def test_probes_remain_valid_at_parameter_limits(factor):
    for _, config, _ in probe_specs(Config(threshold_factor=factor)):
        config.validate()


def test_16_bit_decoding_retains_signal():
    image = np.arange(4096, dtype=np.uint16).reshape(64, 64)
    buffer = BytesIO()
    Image.fromarray(image).save(buffer, format="TIFF")
    assert np.array_equal(decode_image(buffer.getvalue()), image)


@pytest.mark.parametrize("payload", [b"", b"not an image", b"x" * (10 * 1024 * 1024 + 1)])
def test_invalid_files_rejected(payload):
    with pytest.raises(ValueError):
        decode_image(payload)
