import pytest
import fakeredis
from app.main import update_progress, upload_to_s3
from unittest.mock import patch
import json
import asynctest
import aioboto3
from asynctest import CoroutineMock, MagicMock

@pytest.fixture
def mock_redis():
    return fakeredis.FakeRedis(decode_responses=True)


def test_update_progress(mock_redis):
    file_id = "test_file_id"
    progress = 50
    with patch("app.main.redis_client", mock_redis):
        update_progress(file_id, progress)
        retrieved_progress = mock_redis.hget(file_id, "progress")
        assert int(retrieved_progress) == progress

@pytest.mark.asyncio
async def test_upload_s3():
     # Create mock for aioboto3 session and s3 client
    mock_session = asynctest.Mock(aioboto3.Session)
    mock_s3_client = asynctest.Mock()


   