# ComfyUI_api

## POST 添加任务

POST /add_task

> Body 请求参数

```json
{
  "task_id": 1,
  "workflow": {}
}
```

### 请求参数

|名称|位置|类型|必选|中文名|说明|
|---|---|---|---|---|---|
|body|body|object| 否 ||none|
|» task_id|body|number| 是 | 任务编号|none|
|» workflow|body|object| 是 | 工作流输入|none|

> 返回示例

> 200 Response

```json
{}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|成功|Inline|

### 返回数据结构

## GET 查询任务结果

GET /get_task_status

### 请求参数

|名称|位置|类型|必选|中文名|说明|
|---|---|---|---|---|---|
|task_id|query|string| 否 ||none|

> 返回示例

> 200 Response

```json
{}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|成功|Inline|

### 返回数据结构

# 数据模型

