from hashlib import sha256
from io import BytesIO
from zipfile import ZipFile

import numpy as np
import pytest
from PIL import Image

from nuclei_lens.external import ExternalField


def png(array):
    output = BytesIO()
    Image.fromarray(array).save(output, format='PNG')
    return output.getvalue()


def fixture(tmp_path, overlap=False):
    image = png(np.zeros((32, 32), dtype=np.uint8))
    first = np.zeros((32, 32), dtype=np.uint8)
    first[3:6, 3:6] = 255
    first[8, 8] = 255  # One annotated instance may have disconnected pixels.
    second = first if overlap else np.rot90(first, 2)
    target = tmp_path / 'synthetic-unit-fixture.zip'
    with ZipFile(target, 'w') as archive:
        archive.writestr('field/images/field.png', image)
        archive.writestr('field/masks/one.png', png(first))
        archive.writestr('field/masks/two.png', png(second))
    return target, {'id': 'field', 'image_path': 'field/images/field.png',
                    'image_sha256': sha256(image).hexdigest(), 'width': 32, 'height': 32}


def test_external_identity_and_individual_reference_masks(tmp_path):
    target, row = fixture(tmp_path)
    with ZipFile(target) as archive:
        field = ExternalField(archive, row)
        assert field.image('field').shape == (32, 32)
        labels = field.annotations('field')
        assert set(np.unique(labels)) == {0, 1, 2}
        assert labels[3, 3] == labels[8, 8] != 0
        with pytest.raises(ValueError, match='outside'):
            field.image('other')
        with pytest.raises(ValueError, match='partition'):
            field.filenames('test')


def test_external_overlaps_are_not_silently_rewritten(tmp_path):
    target, row = fixture(tmp_path, overlap=True)
    with ZipFile(target) as archive, pytest.raises(ValueError, match='overlap'):
        ExternalField(archive, row).annotations('field')


def test_external_hash_mismatch_stops_the_assessment(tmp_path):
    target, row = fixture(tmp_path)
    row['image_sha256'] = 'wrong'
    with ZipFile(target) as archive, pytest.raises(ValueError, match='frozen'):
        ExternalField(archive, row).image('field')
