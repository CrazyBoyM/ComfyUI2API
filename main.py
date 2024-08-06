import json
from queue import Queue
import threading
from flask import Flask, request
import time

from generate import generate

app = Flask(__name__)

from logging import getLogger

logger = getLogger(__name__)
logger.setLevel("INFO")

# 创建一个消费队列，用于接收任务、执行任务
task_queue = Queue(maxsize=10)
task_results = {}


def consumer_queue(q):
    while True:
        task = q.get()
        task_id, workflow = task
        logger.info(f"开始执行任务：{task_id}")
        start = time.time()
        try:
            task_result = generate(task_id, workflow)
            task_results[task_id] = {"status": "ok", "result": task_result}
        except Exception as e:
            task_results[task_id] = {"status": "error", "message": str(e)}
            logger.info(f"任务执行失败：{task_id}, 错误信息：{e}")

        logger.info(task_results)
        logger.info(f"任务执行完成：{task_id}，耗时：{time.time() - start}")
        q.task_done()


# 启动一个线程来消费队列中的任务
threading.Thread(target=consumer_queue, args=(task_queue,)).start()


def task_exists(task_id):
    for task in task_queue.queue:
        if task[0] == task_id:
            return True
    return task_id in task_results


def error_message(task_id):
    return json.dumps(
        {"status": "error", "message": f"task_id {task_id} already exists"}
    )


# 添加任务到消费队列中
@app.route("/add_task", methods=["POST"])
def add_task():
    data = request.get_json()
    task_id = data["task_id"]
    workflow = data["workflow"]

    if task_exists(task_id):
        return error_message(task_id)

    task_queue.put((task_id, workflow))
    logger.info(f"添加任务：{data}")
    logger.info(f"队列长度：{task_queue.qsize()}")
    logger.info(f"队满：{task_queue.full()}")
    logger.info(f"队空：{task_queue.empty()}")
    return json.dumps({"status": "ok"})


# 获取任务状态
@app.route("/get_task_status", methods=["GET"])
def get_task_status():
    task_id = str(request.args.get("task_id"))
    if task_id is None:
        return json.dumps({"status": "error", "message": "task_id is required"})
    for task in task_queue.queue:
        if task[0] == task_id:
            return json.dumps({"status": "pending"})
    if task_id in task_results:
        return json.dumps({"status": task_results[task_id]["status"]})
    return json.dumps({"status": "error", "message": f"task_id {task_id} not found"})


# 获取任务结果
@app.route("/get_task_result", methods=["GET"])
def get_task_result():
    task_id = str(request.args.get("task_id"))
    if task_id is None:
        return json.dumps({"status": "error", "message": "task_id is required"})
    if task_id in task_results:
        return json.dumps(task_results[task_id])
    return json.dumps({"status": "error", "message": f"task_id {task_id} not found"})


if __name__ == "__main__":
    app.run()
