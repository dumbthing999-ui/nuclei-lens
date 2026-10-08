import base64
import zlib

import numpy as np

from nuclei_lens.core import analyze
from nuclei_lens.raster import serialize


def test_lossless_mask_assets_preserve_exact_ids_and_do_not_change_analysis():
    result = analyze(np.zeros((64, 64), dtype=np.uint16))
    original = result['masks'][0].copy()
    response = serialize(result)
    assets = response['label_maps']
    assert assets['encoding'] == 'zlib-base64-uint32-le'
    assert len(assets['runs']) == len(result['masks']) == 9
    for actual, encoded in zip(result['masks'], assets['runs'], strict=True):
        decoded = np.frombuffer(zlib.decompress(base64.b64decode(encoded)), dtype='<u4').reshape(64, 64)
        np.testing.assert_array_equal(decoded, actual)
    np.testing.assert_array_equal(result['masks'][0], original)
    assert 'label_maps' not in serialize(result, assets=False)
