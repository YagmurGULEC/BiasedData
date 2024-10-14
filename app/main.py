import os 
from fastapi import FastAPI,Request,File,UploadFile,HTTPException,Form,Depends
import uvicorn
import aiofiles
from typing import Dict,List
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import aioboto3
import asyncio
import uuid
import io
import pandas as pd
from dotenv import load_dotenv,find_dotenv
from .tasks import data_analysis_task
from celery.result import AsyncResult

load_dotenv(find_dotenv())
app = FastAPI()
APP_DIR= os.path.dirname(__file__)
STATIC_DIR = os.path.join(APP_DIR, "static/")
TEMPLATES_DIR = os.path.join(APP_DIR, "templates/")
templates = Jinja2Templates(directory=TEMPLATES_DIR)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

s3_bucket_name=os.getenv("S3_BUCKET_NAME")
s3_region_name=os.getenv("S3_REGION_NAME")
s3_region_name=os.getenv("S3_REGION_NAME")
s3_session = aioboto3.Session(
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
    aws_secret_access_key=os.getenv("AWS_SECRET_KEY"),
    region_name=s3_region_name
    )

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse(
        "index.html",{"request": request,'title': "File Upload"}
    )

@app.post("/delete-file")
async def delete_file(file_key:str=Form(...)):
    try:
        async with s3_session.client("s3") as s3_client:
            await s3_client.delete_object(Bucket=s3_bucket_name, Key=file_key)
        return {"message": "File deleted successfully", "key": file_key}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error occurred during file deletion: {e}")

@app.get("/check-task/{task_id}")
async def check_task(task_id:str):
    task = AsyncResult(task_id)
    if task.state == "SUCCESS":
        return {"task_id": task.id, "task_status": task.status, "task_result": task.result}
    return {"task_id": task.id, "task_status": task.status}

@app.post("/async-upload")
async def async_upload(file: UploadFile = File(...)):
    filename = file.filename
    try:
        async with s3_session.client("s3") as s3_client:
            upload_id = str(uuid.uuid4())
            key = f"{upload_id}/{filename}"
            content=await file.read()
            # Upload the file in one part
            await s3_client.put_object(
                Bucket=s3_bucket_name,
                Key=key,
                Body=content
            )
        return {"message": "File uploaded successfully", "upload_id": upload_id, "key": key}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error occurred during file upload: {e}")

@app.post("/detect-bias")
async def detect(file_key:str=Form(...),label_column:str=Form(...),sensitive_column:str=Form(...)):
    try:
        async with s3_session.client("s3") as s3_client:
            response = await s3_client.get_object(Bucket=s3_bucket_name, Key=file_key)
             # Read the file content asynchronously
            content = await response['Body'].read()
            csv_buffer = io.StringIO(content.decode('utf-8'))
            serialized_csv = csv_buffer.getvalue()
            task=data_analysis_task.delay(serialized_csv,sensitive_column,label_column)
           
        return {"message": "Data analysis started", "label_column": label_column, "sensitive_column": sensitive_column, "task_id": task.id}
    except Exception as e:  
        raise HTTPException(status_code=500, detail=f"Error occurred : {e}")
   
    

