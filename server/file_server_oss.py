from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import oss2
import uuid
import uvicorn

app = FastAPI()

# 阿里云OSS配置
OSS_ENDPOINT = 'your-oss-endpoint'
OSS_ACCESS_KEY_ID = 'your-access-key-id'
OSS_ACCESS_KEY_SECRET = 'your-access-key-secret'
OSS_BUCKET_NAME = 'your-bucket-name'

# 初始化OSS客户端
auth = oss2.Auth(OSS_ACCESS_KEY_ID, OSS_ACCESS_KEY_SECRET)
bucket = oss2.Bucket(auth, OSS_ENDPOINT, OSS_BUCKET_NAME)

@app.get('/filemanager/v1/file/storage/proxy/{storage}/upload/signurl')
async def get_signed_url(storage: str):
    file_uuid = str(uuid.uuid4())
    filename = f"{storage}/{file_uuid}"
    signed_url = bucket.sign_url('PUT', filename, 60)  # 生成60秒有效期的签名URL
    file_url = f"https://{OSS_BUCKET_NAME}.{OSS_ENDPOINT}/{filename}"
    return JSONResponse({
        "Method": "PUT",
        "SignedUrl": signed_url,
        "FileUrl": file_url
    })

@app.get('/files/{storage}/{file_uuid}')
async def serve_file(storage: str, file_uuid: str):
    filename = f"{storage}/{file_uuid}"
    url = bucket.sign_url('GET', filename, 60)  # 生成60秒有效期的签名URL
    return JSONResponse({"url": url})

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='0.0.0.0')
    parser.add_argument('--port', default=8000, type=int)
    args = parser.parse_args()
    HOST = args.host
    PORT = args.port
    uvicorn.run(app, host=HOST, port=PORT)