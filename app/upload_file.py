import os
import aioboto3
import asyncio
from botocore.exceptions import ClientError
from dotenv import load_dotenv,find_dotenv
import threading 
load_dotenv(find_dotenv())

class ProgressPercentage:
    def __init__(self, filename):
        self._filename = filename
        self._size = float(os.path.getsize(filename))
        self._seen_so_far = 0
        self._lock = threading.Lock()

    def __call__(self, bytes_amount):
        # To simplify, we'll assume this is hooked up to a file upload
        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = (self._seen_so_far / self._size) * 100
            print(f"{self._filename} upload progress: {percentage:.2f}%")



async def upload_file(file, bucket_name, object_name=None):
    """Upload a file to an S3 bucket with progress tracking"""
    print ("Uploading file")
    # Use the file name if no object name is provided
    if object_name is None:
        object_name = os.path.basename(file_path)
    
    # Asynchronous session with aioboto3
    session = aioboto3.Session(
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
        aws_secret_access_key=os.getenv("AWS_SECRET_KEY"),
        region_name=os.getenv("S3_REGION_NAME")
    )
    
    # Instantiate the progress tracking object
    progress = ProgressPercentage(file_path)

    try:
        async with session.client('s3') as s3_client:
            # Upload the file and attach the progress tracker
            await s3_client.upload_file(
                Filename=file_path, 
                Bucket=bucket_name, 
                Key=object_name,
                Callback=progress
            )
            print(f"Upload of {file_path} completed successfully.")
    except ClientError as e:
        print(f"Error uploading file: {e}")
        return False
    file_exists=await check_file_exists(bucket_name, 'test_data.csv')
    if file_exists:
       print(f"File {object_name} exists in the bucket")
    else:
        print(f"File {object_name} does not exist in the bucket.")
    return True


async def check_file_exists(bucket_name, object_name):
    print ("Checking file exists")
    """Check if a file exists in an S3 bucket"""
     # Asynchronous session with aioboto3
    session = aioboto3.Session(
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
        aws_secret_access_key=os.getenv("AWS_SECRET_KEY"),
        region_name=os.getenv("S3_REGION_NAME")
    )

    try:
        async with session.client('s3') as s3_client:
            # HeadObject retrieves metadata, which will fail if the object does not exist
            await s3_client.head_object(Bucket=bucket_name, Key=object_name)
            print(f"{object_name} exists in {bucket_name}.")
            return True
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            print(f"{object_name} does not exist in {bucket_name}.")
        else:
            print(f"Error checking file: {e}")
        return False

# Example usage
async def main():
    file_path = 'test_data.csv'
    bucket_name =os.getenv("S3_BUCKET_NAME")
    await upload_file(file_path, bucket_name)
 

# # Run the asyncio loop
asyncio.run(main())
