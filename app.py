from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from azure.storage.blob import BlobServiceClient
from typing import List
import os
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

AZURE_STORAGE_CONNECTION_STRING = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
CONTAINER_NAME = "rtavoicelens"

blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
container_client = blob_service_client.get_container_client(CONTAINER_NAME)

@app.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    uploaded_filenames = []
    try:
        for file in files:
            file_content = await file.read()
            blob_client = container_client.get_blob_client(file.filename)
            blob_client.upload_blob(file_content, overwrite=True)

            uploaded_filenames.append(file.filename)

        return JSONResponse(content={"message": "Files uploaded successfully", "files": uploaded_filenames})

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
