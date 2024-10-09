import pytest
import httpx
from app.main import app
from httpx import AsyncClient
import redis

# Set up the Redis client


@pytest.mark.asyncio
async def test_async_upload_file():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as async_client:
        # Step 1: Upload a file
        response = await async_client.post("/async-upload", files={"file": ("test_data.csv", open("test_data.csv", "rb"))})
        assert response.status_code == 200
        file_id = response.json()["file_id"]
        # Step 2: Check the upload progress
        progress_response = await async_client.get(f"/upload-progress/{file_id}")
        assert progress_response.status_code == 200
        assert int(progress_response.json()["progress"]) <=100



@pytest.fixture(scope="session")
def setup_redis_container():
    # Assuming Redis is running (e.g., via Docker), you could set this up manually or as part of CI
    client = redis.Redis(host='localhost', port=6379, decode_responses=True,db=1)
    yield client
    client.flushdb()  # Clean up after tests

   

