import os 
from fastapi import FastAPI,Request,File,UploadFile,HTTPException
import uvicorn
from .utils import is_allowed_extension,sanitize_filename,validate_mime_type,get_total_file_size,generate_file_id
import aiofiles
from typing import Dict


app = FastAPI()
file_upload_progress: Dict[str, int] = {}

@app.get("/")
async def read_root(request: Request):
    return {"message": "Hello World"}

@app.post("/sync-upload")
async def sync_upload(file: UploadFile = File(...)):
    UPLOAD_DIR = "uploaded_files_sync"
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    if not is_allowed_extension(file.filename):
        raise HTTPException(status_code=400, detail="Invalid file type")
    file_content = file.file.read(1024) # Read the first 1KB to check MIME type
    valid_mime_type, mime_type = validate_mime_type(file_content)
    if not valid_mime_type:
        raise HTTPException(status_code=400, detail=f"Invalid MIME type: {mime_type}")
    
    sanitized_filename = sanitize_filename(file.filename)
    file_path = os.path.join(UPLOAD_DIR, sanitized_filename)
    with open(file_path, "wb") as buffer:
        buffer.write(file_content) #Write the first 1KB to the file
        buffer.write(file.file.read()) # Write the rest of the file
    return {"message": "File uploaded successfully", "filename": sanitized_filename}

@app.post("/async-upload")
async def async_upload(file: UploadFile = File(...)):
    UPLOAD_DIR = "uploaded_files_async"
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_id = generate_file_id()
   
    if not is_allowed_extension(file.filename):
        raise HTTPException(status_code=400, detail="Invalid file type")
    file_content = await file.read(1024)
    
    total_file_size = get_total_file_size(file)
  
    uploaded_bytes =1024
    valid_mime_type, mime_type = validate_mime_type(file_content)
    if not valid_mime_type:
        raise HTTPException(status_code=400, detail=f"Invalid MIME type: {mime_type}")
    sanitized_filename = sanitize_filename(file.filename)
    file_path = os.path.join(UPLOAD_DIR, sanitized_filename)
    async with aiofiles.open(file_path, "wb") as buffer:
        await buffer.write(file_content) # Write the first 1KB to the file
        while file_content:= await file.read(1024):
            uploaded_bytes += len(file_content)
            file_upload_progress[file_id] = int((uploaded_bytes / total_file_size) * 100)
            print(f"File ID: {file_id}, Progress: {min(file_upload_progress[file_id],100)}%")
            await buffer.write(file_content)
    return {"message": "File uploaded successfully", "filename": sanitized_filename}

@app.get("/upload-progress/{file_id}")
async def upload_progress(file_id: str):
    """
    Endpoint to get the progress of a file upload
    """
    if file_id not in file_upload_progress:
        raise HTTPException(status_code=404, detail="File ID not found")
    current_progress = file_upload_progress[file_id]
    return {"file_id": file_id, "progress": current_progress}