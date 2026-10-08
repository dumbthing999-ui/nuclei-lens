"""One-shot isolated local analysis; stdin image bytes, stdout JSON only."""
from __future__ import annotations

import json
import sys

from .core import analyze
from .raster import MAX_FILE_BYTES, decode_image, serialize


def main() -> None:
    payload = sys.stdin.buffer.read(MAX_FILE_BYTES + 1)
    try:
        if len(payload) > MAX_FILE_BYTES:
            raise ValueError('Image file exceeds 10 MB.')
        result = serialize(analyze(decode_image(payload)))
        message = {'ok': True, 'result': result}
    except ValueError as error:
        message = {'ok': False, 'error': str(error)[:500]}
    sys.stdout.write(json.dumps(message, separators=(',', ':')))


if __name__ == '__main__':
    main()
