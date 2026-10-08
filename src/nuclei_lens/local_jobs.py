"""Killable process deadlines for the optional loopback-only API."""
from __future__ import annotations

import asyncio
import json
import sys
from typing import Any

LOCAL_COMPUTE_TIMEOUT = 90.0


async def run_local_analysis(payload: bytes, *, timeout: float = LOCAL_COMPUTE_TIMEOUT) -> dict[str, Any]:
    process = await asyncio.create_subprocess_exec(
        sys.executable, '-m', 'nuclei_lens.local_worker',
        stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.DEVNULL,
    )
    try:
        output, _ = await asyncio.wait_for(process.communicate(payload), timeout=timeout)
        if process.returncode != 0:
            raise RuntimeError('Local analysis process stopped unexpectedly.')
        message = json.loads(output)
        if not message['ok']:
            raise ValueError(message['error'])
        if not isinstance(message['result'], dict):
            raise RuntimeError('Invalid local analysis response.')
        return message['result']
    finally:
        # Cancellation/timeout must release CPU, not leave a detached thread.
        if process.returncode is None:
            try:
                process.kill()
            except ProcessLookupError:
                pass
            await process.communicate()
