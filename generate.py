import urllib.request
import websocket
import uuid
import json
from datetime import datetime
from utils.upload import upload_file_from_path

import config

# 设置工作目录和项目相关的路径
WORKING_DIR = config.WORKDIR
COMFYUI_ENDPOINT = config.COMFYUI_ENDPOINT

client_id = str(uuid.uuid4())  # 生成一个唯一的客户端ID


def get_data(filename, subfolder, folder_type):
    data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
    url_values = urllib.parse.urlencode(data)
    with urllib.request.urlopen(
        f"http://{COMFYUI_ENDPOINT}/view?{url_values}"
    ) as response:
        return response.read()


def queue_task(prompt):
    p = {"prompt": prompt, "client_id": client_id}
    data = json.dumps(p).encode("utf-8")
    req = urllib.request.Request(f"http://{COMFYUI_ENDPOINT}/prompt", data=data)
    return json.loads(urllib.request.urlopen(req).read())


def write_and_upload_file(task_id, file_data, file_type):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    file_name = f"{WORKING_DIR}/{task_id}_{timestamp}.{file_type}"
    print(f"file_name:{file_name}")
    with open(file_name, "wb") as binary_file:
        binary_file.write(file_data)
    return upload_file_from_path(
        task_id=task_id, filepath=file_name, ext=f".{file_type}"
    )


def run_workflow(ws, workflow):
    prompt_id = queue_task(workflow)["prompt_id"]
    print(f"prompt_id:{prompt_id}")
    output_files = {}

    while True:
        out = ws.recv()
        if isinstance(out, str):
            message = json.loads(out)
            if message["type"] == "executing":
                data = message["data"]
                if data["node"] is None and data["prompt_id"] == prompt_id:
                    print("执行完成")
                    break
        else:
            continue

    with urllib.request.urlopen(
        f"http://{COMFYUI_ENDPOINT}/history/{prompt_id}"
    ) as response:
        history = json.loads(response.read())[prompt_id]
    print(history)

    # 获取所有输出文件
    for node_id, node_output in history["outputs"].items():
        if "images" in node_output:
            output_files[node_id] = []
            for image in node_output["images"]:
                file_data = get_data(
                    image["filename"], image["subfolder"], image["type"]
                )
                url = write_and_upload_file(prompt_id, file_data, "png")
                output_files[node_id].append(url)
        if "videos" in node_output:
            output_files[node_id] = []
            for video in node_output["videos"]:
                file_data = get_data(
                    video["filename"], video["subfolder"], video["type"]
                )
                url = write_and_upload_file(prompt_id, file_data, "gif")
                output_files[node_id].append(url)

    return output_files


def generate(task_id, workflow):
    ws = websocket.WebSocket()
    ws.connect(f"ws://{COMFYUI_ENDPOINT}/ws?clientId={client_id}")
    return run_workflow(ws, workflow)
