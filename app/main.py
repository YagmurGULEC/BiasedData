import os 
from fastapi import FastAPI,Request,File,UploadFile,HTTPException,Form,Depends
from fastapi_csrf_protect import CsrfProtect
from fastapi_csrf_protect.exceptions import CsrfProtectError
import uvicorn
import aiofiles
from typing import Dict,List
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import aioredis
import aioboto3
import asyncio
import uuid
import io
import pandas as pd

app = FastAPI()
APP_DIR= os.path.dirname(__file__)
STATIC_DIR = os.path.join(APP_DIR, "static/")
TEMPLATES_DIR = os.path.join(APP_DIR, "templates/")
templates = Jinja2Templates(directory=TEMPLATES_DIR)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
# Use environment variables for Redis host and port
redis_host = os.getenv("REDIS_HOST", "localhost")
redis_port = int(os.getenv("REDIS_PORT", 6379))

ENV=os.getenv("ENV","local")
if ENV=="local":
    UPLOAD_DIR = "uploaded_files"
    os.makedirs(UPLOAD_DIR, exist_ok=True)
else:
    UPLOAD_DIR=None
    s3_bucket_name=os.getenv("S3_BUCKET_NAME")
    s3_region_name=os.getenv("S3_REGION_NAME")


@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse(
        "index.html",{"request": request,'title': "File Upload"}
    )

@app.post("/async-upload")
async def async_upload(file: UploadFile = File(...),filename:str=Form(...),columns:List[str]=Form(...),size:int=Form(...)):
   
    
    try:
        session = aioboto3.Session(
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
        aws_secret_access_key=os.getenv("AWS_SECRET_KEY"),
        region_name=s3_region_name
        
        )
        async with session.client("s3") as s3_client:

            upload_id = str(uuid.uuid4())
            key = f"{upload_id}/{filename}"
            # Create a unique upload ID for progress tracking
           
            # Upload the file in chunks
            content=await file.read()
            # Upload the file in one part
            await s3_client.put_object(
                Bucket=s3_bucket_name,
                Key=key,
                Body=content
            )
        return {"message": "File uploaded successfully", "upload_id": upload_id, "filename": filename,"url":f"{key}", "columns": columns, "size": size}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error occurred during file upload: {e}")

@app.post("/detect-bias")
async def detect(file_key:str=Form(...),label_column:str=Form(...),sensitive_column:str=Form(...)):
    try:
        session = aioboto3.Session(
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
        aws_secret_access_key=os.getenv("AWS_SECRET_KEY"),region_name=s3_region_name)
        async with session.client("s3") as s3_client:
            response = await s3_client.get_object(Bucket=s3_bucket_name, Key=file_key)
             # Read the file content asynchronously
            content = await response['Body'].read()
             # Load CSV data into a Pandas DataFrame
            csv_buffer = io.StringIO(content.decode('utf-8'))
            df = pd.read_csv(csv_buffer)
            
        return {"message": "Bias detected successfully", "label_column": label_column, "sensitive_column": sensitive_column}
    except Exception as e:  
        raise HTTPException(status_code=500, detail=f"Error occurred : {e}")
    

