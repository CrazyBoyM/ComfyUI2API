from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import os
import uuid
import uvicorn

app = FastAPI()

UPLOAD_FOLDER = '/path/to/upload/folder'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.get('/filemanager/v1/file/storage/proxy/{storage}/upload/signurl')
async def get_signed_url(storage: str):
    file_uuid = str(uuid.uuid4())
    signed_url = f"http://{HOST}:{PORT}/upload/{storage}/{file_uuid}"
    file_url = f"http://{HOST}:{PORT}/files/{storage}/{file_uuid}"
    return JSONResponse({
        "Method": "PUT",
        "SignedUrl": signed_url,
        "FileUrl": file_url
    })

@app.put('/upload/{storage}/{file_uuid}')
async def upload_file(storage: str, file_uuid: str, file: UploadFile = File(...)):
    if not allowed_file(file.filename):
        raise HTTPException(status_code=400, detail="File type not allowed")
    filename = f"{file_uuid}{os.path.splitext(file.filename)[1]}"
    storage_folder = os.path.join(UPLOAD_FOLDER, storage)
    if not os.path.exists(storage_folder):
        os.makedirs(storage_folder)
    file_path = os.path.join(storage_folder, filename)
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
    return JSONResponse({"message": "File uploaded successfully"})

@app.get('/files/{storage}/{file_uuid}')
async def serve_file(storage: str, file_uuid: str):
    storage_folder = os.path.join(UPLOAD_FOLDER, storage)
    for filename in os.listdir(storage_folder):
        if filename.startswith(file_uuid):
            file_path = os.path.join(storage_folder, filename)
            return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="File not found")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='0.0.0.0')
    parser.add_argument('--port', default=8000, type=int)
    args = parser.parse_args()
    HOST = args.host
    PORT = args.port
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    uvicorn.run(app, host=HOST, port=PORT)