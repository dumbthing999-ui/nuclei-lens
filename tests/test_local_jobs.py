import asyncio

import pytest

from nuclei_lens.local_jobs import run_local_analysis


def test_deadline_kills_the_actual_child(monkeypatch):
    processes = []
    start = asyncio.create_subprocess_exec

    async def capture(*args, **kwargs):
        process = await start(*args, **kwargs)
        processes.append(process)
        return process

    monkeypatch.setattr(asyncio, 'create_subprocess_exec', capture)
    with pytest.raises(TimeoutError):
        asyncio.run(run_local_analysis(b'', timeout=.01))
    assert len(processes) == 1
    assert processes[0].returncode is not None
    assert processes[0].returncode != 0


def test_cancellation_kills_the_actual_child(monkeypatch):
    processes = []
    start = asyncio.create_subprocess_exec

    async def scenario():
        created = asyncio.Event()

        async def capture(*args, **kwargs):
            process = await start(*args, **kwargs)
            processes.append(process)
            created.set()
            return process

        monkeypatch.setattr(asyncio, 'create_subprocess_exec', capture)
        task = asyncio.create_task(run_local_analysis(b''))
        await asyncio.wait_for(created.wait(), 5)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        assert processes[0].returncode is not None
        assert processes[0].returncode != 0

    asyncio.run(scenario())
