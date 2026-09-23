import pytest
from app.services.jobs import JobQueue

@pytest.mark.asyncio
async def test_job_queue_key_is_configurable() -> None:
    queue = JobQueue("redis://localhost:6379/0", "atlasai:test-jobs")
    assert queue.queue_name == "atlasai:test-jobs"
    await queue.close()
