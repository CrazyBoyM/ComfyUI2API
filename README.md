# COMFYUI_API

## 1. 简介
ComfyUI-API-adapter基于本地websocket通信实现数据转发，用于让ComfyUI变成一个通用的API服务。

## 2. 使用
修改配置文件：
```yaml
# -*- coding: utf-8 -*-

WORKDIR = "/data/comfyui_output"

# FileUpload for SIGNURL
DEFAULT_STORAGE = "comfyui-test-stroage"
UPLOAD_SIGN_URL = "https://localhost:8000/filemanager/v1/file/storage/proxy/{storage}/upload/signurl"
APIKEY = "abc-kkk-token"


COMFYUI_ENDPOINT = "127.0.0.1:6006"

```
其中WORKDIR为工作流任务输出目录(临时文件存放)，UPLOAD_SIGN_URL为文件上传接口地址，APIKEY为文件上传接口的鉴权key，COMFYUI_ENDPOINT为comfyui服务的地址。

## 3. 运行
```
pip install websocket-client requests flask
```
启动ComfyUI-API-adapter服务:
```bash
python main.py
```
注意：你可能需要自行修改实现代码中的文件上传逻辑（图片、视频等文件上传），在'./server'目录下也提供了简单的文件上传接口服务样例(原生文件存储服务版本、OSS版本)，可直接用于配合当前代码进行使用。
