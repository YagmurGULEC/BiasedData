import pytest
from app.main import app
import os
from httpx import AsyncClient
from app.main import app
from httpx import ASGITransport

TEST_DIR= os.path.dirname(__file__)

@pytest.mark.asyncio
async def test_upload_file():
    async with AsyncClient(transport=ASGITransport(app), base_url="http://test") as async_client:
        file_path = os.path.join(TEST_DIR, "../app/test_data.csv")
        with open(file_path, "rb") as file:
            response = await async_client.post("/async-upload", files={"file": ("test_data.csv", file)})
        assert response.status_code==200
        assert 'upload_id' in response.json()
        assert 'key' in response.json()
        key = response.json()['key']
        sensitive_column='Gender'
        label_column='Hired'
        response = await async_client.post("/detect-bias",data={"file_key":key,"label_column":label_column,"sensitive_column":sensitive_column})
        print (response.json())

   

