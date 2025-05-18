# apigent

## 运行项目

```shell
uv sync
```

```shell
source .venv/bin/activate
```

```shell
fastapi run main.py

# or dev
fastapi dev main.py
```

## 前端 API 访问说明

### 聊天完成 API

#### 发送聊天请求
```
POST /api/chat/completions
```

**请求头：**
```
Content-Type: application/json
Session-ID: {会话ID} 
Tool: {工具名称}      // 可选，指定使用的工具
```

**请求体：**
```json
{
  "messages": [
    {
      "role": "user",
      "content": "用户消息内容"
    },
    {
      "role": "assistant",
      "content": "助手回复内容"
    },
    // 更多消息...
  ]
}
```

**响应：**
```json
{
  "openai_response": {
    "id": "chatcmpl-123456789",
    "object": "chat.completion",
    "created": 1698155432,
    "model": "gpt-3.5-turbo",
    "choices": [
      {
        "index": 0,
        "message": {
          "role": "assistant",
          "content": "助手回复内容",
          "tool_calls": [
            {
              "id": "call_abc123",
              "type": "function",
              "function": {
                "name": "function_name",
                "arguments": "{\"arg1\": \"value1\", \"arg2\": \"value2\"}"
              }
            }
          ]
        },
        "finish_reason": "stop"
      }
    ],
    "usage": {
      "prompt_tokens": 100,
      "completion_tokens": 50,
      "total_tokens": 150
    }
  },
  "timestamp": 1698155432,
  "model": "gpt-3.5-turbo",
  "tools_used": ["function_name1", "function_name2"]
}
```

### 聊天历史结果 API

#### 获取会话工具调用结果（用于异步获取记录）
```
GET /api/chat-histories/result/?session_id={session_id}
```

- 此调用只会返回工具名称和参数和结果不为空的记录。

**请求参数：**
- `session_id`: 会话ID，用于获取特定会话的工具调用结果

**响应：**
```json
{
  "success": true,
  "data": [
    {
      "id": 14,
      "session_id": "chat_matb6qom_pjkrsm_moz",
      "tool_name": "shoe-01",
      "parameters": {
        "a": "2"
      },
      "created_at": "2025-05-18T07:08:08.129803+00:00",
      "updated_at": "2025-05-18T07:08:11.786744+00:00"
    }
  ]
}
```

**说明：**
- `success`: 表示请求是否成功
- `data`: 包含会话中的工具调用结果列表
  - `id`: 结果记录ID
  - `session_id`: 会话ID
  - `tool_name`: 使用的工具名称
  - `parameters`: 工具调用的参数
  - `created_at`: 创建时间
  - `updated_at`: 更新时间

## 环境变量配置

开发环境下，请按照以下步骤配置环境变量：

1. 在项目根目录下复制 `.env.example` 文件并重命名为 `.env`
   ```shell
   cp .env.example .env
   ```

2. 编辑 `.env` 文件，填入您的实际配置信息

### 环境变量说明

```
# 应用运行端口， 默认 8000
PORT=8081

# 数据库连接字符串
# 格式：postgresql://用户名:密码@主机地址:端口/数据库名?sslmode=disable
DATABASE_URL=postgresql://username:password@host:port/database?sslmode=disable

# OpenAI API密钥（必填）
OPENAI_API_KEY=your_openai_api_key

# OpenAI API基础URL（可选，用于自定义API端点）
OPENAI_API_BASE_URL=your_api_base_url

# 嵌入模型名称
EMBEDDING_MODEL=model_name

# 文本生成模型名称
TEXT_GENERATION_MODEL=model_name

# 日志级别（DEBUG, INFO, WARNING, ERROR, CRITICAL）
LOG_LEVEL=ERROR
```
