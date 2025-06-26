# APIGent 流式聊天API文档

## 概述

APIGent 现在支持流式聊天API，允许客户端实时接收AI响应，提供更好的用户体验。流式API使用Server-Sent Events (SSE) 格式返回数据。

## 新增端点

### 流式聊天完成
```
POST /api/chat/completions/stream
```

## 请求格式

### 请求头
```
Content-Type: application/json
Session-Id: {会话ID}
Tool: {工具名称}  // 可选
```

### 请求体
```json
{
  "messages": [
    {
      "role": "user",
      "content": "用户消息内容"
    }
  ],
  "temperature": 0.7,
  "max_tokens": 1000,
  "stream": true
}
```

## 响应格式

### 响应头
```
Content-Type: text/plain; charset=utf-8
Cache-Control: no-cache
Connection: keep-alive
```

### 响应体 (SSE格式)

流式响应使用Server-Sent Events格式，每个数据块的格式为：
```
data: {JSON数据}

```

#### 数据块结构
```json
{
  "id": "chatcmpl-xxx",
  "object": "chat.completion.chunk",
  "created": 1698155432,
  "model": "gpt-3.5-turbo",
  "choices": [
    {
      "index": 0,
      "delta": {
        "role": "assistant",
        "content": "部分响应内容",
        "tool_calls": [
          {
            "index": 0,
            "id": "call_xxx",
            "type": "function",
            "function": {
              "name": "function_name",
              "arguments": "部分参数"
            }
          }
        ]
      },
      "finish_reason": null
    }
  ]
}
```

#### 结束标记
流式响应结束时会发送：
```
data: [DONE]

```

## 使用示例

### JavaScript/TypeScript
```javascript
async function streamChat(messages, sessionId) {
  const response = await fetch('/api/chat/completions/stream', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Session-Id': sessionId
    },
    body: JSON.stringify({
      messages: messages,
      temperature: 0.7,
      max_tokens: 1000,
      stream: true
    })
  });

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const chunk = decoder.decode(value);
    const lines = chunk.split('\n');

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const data = line.slice(6);
        
        if (data === '[DONE]') {
          console.log('Stream completed');
          return;
        }

        try {
          const parsed = JSON.parse(data);
          const delta = parsed.choices?.[0]?.delta;
          
          if (delta?.content) {
            console.log(delta.content); // 输出部分内容
          }
          
          if (delta?.tool_calls) {
            console.log('Tool calls:', delta.tool_calls);
          }
        } catch (e) {
          console.error('Parse error:', e);
        }
      }
    }
  }
}
```

### Python
```python
import requests
import json

def stream_chat(messages, session_id):
    url = "http://localhost:8000/api/chat/completions/stream"
    headers = {
        "Content-Type": "application/json",
        "Session-Id": session_id
    }
    data = {
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 1000,
        "stream": True
    }
    
    response = requests.post(url, headers=headers, json=data, stream=True)
    
    for line in response.iter_lines(decode_unicode=True):
        if line and line.startswith("data: "):
            data_content = line[6:]
            
            if data_content == "[DONE]":
                break
            
            try:
                chunk_data = json.loads(data_content)
                delta = chunk_data.get("choices", [{}])[0].get("delta", {})
                
                if "content" in delta:
                    print(delta["content"], end="", flush=True)
                
                if "tool_calls" in delta:
                    print(f"\nTool calls: {delta['tool_calls']}")
                    
            except json.JSONDecodeError:
                continue
```

### cURL
```bash
curl -X POST "http://localhost:8000/api/chat/completions/stream" \
  -H "Content-Type: application/json" \
  -H "Session-Id: test_session_123" \
  -d '{
    "messages": [
      {
        "role": "user", 
        "content": "你好，请帮我查询天气"
      }
    ],
    "temperature": 0.7,
    "max_tokens": 1000,
    "stream": true
  }' \
  --no-buffer
```

## 错误处理

### 错误响应格式
```json
{
  "error": {
    "message": "错误描述",
    "type": "error_type",
    "code": "error_code"
  }
}
```

### 常见错误类型
- `session_error`: 会话相关错误
- `api_error`: OpenAI API错误
- `stream_error`: 流式处理错误
- `internal_error`: 内部服务器错误

## 性能特点

### 优势
- **实时响应**: 用户可以立即看到AI开始生成的内容
- **更好的用户体验**: 避免长时间等待
- **支持工具调用**: 完整支持工具调用的流式输出
- **错误处理**: 完善的错误处理和恢复机制

### 注意事项
- 流式响应需要保持连接，确保网络稳定
- 客户端需要正确处理SSE格式的数据
- 工具调用信息可能分多个chunk传输
- 需要在客户端重新组装完整的响应内容

## 数据库存储

流式API会在响应完成后将完整的对话记录存储到数据库中，包括：
- 用户请求内容
- AI完整响应
- 工具调用信息
- 会话状态更新

## 测试

使用提供的测试脚本：
```bash
python test_stream.py
```

选择测试类型：
1. 流式API测试
2. 普通API测试  
3. 两者对比测试

## 兼容性

流式API与现有的普通API完全兼容，可以根据需要选择使用：
- `/api/chat/completions` - 普通API，一次性返回完整响应
- `/api/chat/completions/stream` - 流式API，实时返回响应片段
