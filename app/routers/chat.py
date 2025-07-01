from fastapi import APIRouter, HTTPException, Header
from fastapi.responses import StreamingResponse
import logging
from app.utils.retrieve import retrieve_tools_by_text
from app.utils.preproccess import get_tool_schema
from pydantic import BaseModel
from typing import List, Optional, AsyncGenerator
from app.utils.pg import query_one_dict, execute_dict, create, update, delete, detail, list_all, execute_none
from app.utils.ai import parse_tool_schemas, parse_tool_schemas_stream
from app.models.chat import ChatSessionCreate, ChatHistoryCreate
import json
import uuid
import time
# from psycopg.types.json import Jsonb
# from openai.types.chat import ChatCompletionMessage

logger = logging.getLogger(__name__)    

router = APIRouter()

class Message(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    messages: List[Message]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 1000
    stream: Optional[bool] = False

# @router.post("/")
# async def chat(request: ChatCompletionRequest):
#     user_messages = [msg.content for msg in request.messages if msg.role == "user"]
#     if not user_messages:
#         raise HTTPException(status_code=400, detail="No user message found in the request")
    
#     text = user_messages[-1]
#     logger.info(f"Received chat request: {text}")
#     """
#     根据用户输入的文本检索相关的工具
    
#     Args:
#         text: 用户输入的查询文本
        
#     Returns:
#         List[Dict[str, Any]]: 匹配的工具列表
#     """
#     try:
#         # 调用检索函数获取相关工具
#         tools = retrieve_tools_by_text(text, similarity_threshold=0.4)
#         for tool in tools:
#             logger.info(f"Tool: {tool}")
#             tool_schema = get_tool_schema(tool["id"])
#             return {"tools": [tool_schema]}
#         return {"tools": []}
#     except Exception as e:
#         logger.error(f"Error in chat endpoint: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))





@router.post("/completions")
async def chat_completions(
    request: ChatCompletionRequest,
    session_id: str = Header(..., alias="Session-Id"),
    tool: str | None = Header(None, alias="Tool")
):
    if not session_id:
        raise HTTPException(status_code=400, detail="Session-Id is required")
    
    # 检查会话状态
    session = query_one_dict(
        "SELECT status FROM apigent_chat_session WHERE session_id = %s",
        (session_id,)
    )
    
    if session:
        # 会话存在，检查状态
        if session["status"] == 1:
            raise HTTPException(status_code=400, detail="Session is already completed")
    else:
        # 会话不存在，创建新会话
        create("apigent_chat_session", ChatSessionCreate(
            session_id=session_id,
            title=f"会话 {str(uuid.uuid4())[:8]}",
            status=0
        ))
    
    # 提取用户消息
    user_messages = [msg for msg in request.messages if msg.role == "user"]
    if not user_messages:
        raise HTTPException(status_code=400, detail="No user message found in the request")
    
    # 获取最后一条用户消息
    # user_text = user_messages[-1].content
    # combile all user messages with weights
    user_text = ""
    total_weight = 0
    for i, msg in enumerate(user_messages):
        # 使用指数衰减，最近的消息权重更高
        weight = 2 ** (len(user_messages) - i - 1)
        user_text += msg.content + "\n" * weight
        total_weight += weight
    
    try:
        # 调用检索函数获取相关工具
        tools = retrieve_tools_by_text(user_text, similarity_threshold=0.4)
        tool_schemas = []
        used_tool_name = None
        parameters = None
        
        for tool in tools:
            logger.info(f"Tool: {tool}")
            tool_schema = get_tool_schema(tool["id"])
            tool_schemas.append(tool_schema)
            # 如果有工具被使用，记录第一个工具的名称
            if not used_tool_name and tool:
                used_tool_name = tool.get("name")
                # 如果有参数，也记录下来
                if "parameters" in tool:
                    parameters = tool.get("parameters")

        # 打印工具结果
        logger.info("工具结果:")
        logger.info(json.dumps(tool_schemas, ensure_ascii=False, indent=2))
        
        # 保存用户请求到聊天历史
        chat_history_create = ChatHistoryCreate(
            session_id=session_id,
            request_content={"messages": request.messages},
            # request_content=Jsonb({"messages": [msg.model_dump() for msg in request.messages]}),
            tool_name=used_tool_name,
            parameters=parameters
        )

        # print(chat_history_create)
        
        # 创建聊天历史记录
        history_record = create("apigent_chat_history", chat_history_create)
        history_id = history_record["id"]
        print(history_id)
        
        # 获取AI响应
        response = parse_tool_schemas(request.messages, tool_schemas)
        
        # 检查响应中是否包含工具调用信息
        if response and "openai_response" in response:
            openai_response = response["openai_response"]
            if "choices" in openai_response and len(openai_response["choices"]) > 0:
                choice = openai_response["choices"][0]
                if "message" in choice and "tool_calls" in choice["message"]:
                    tool_calls = choice["message"]["tool_calls"]
                    if tool_calls and len(tool_calls) > 0:
                        # 获取第一个工具调用
                        tool_call = tool_calls[0]
                        if "function" in tool_call:
                            # 更新工具名称和参数
                            used_tool_name = tool_call["function"].get("name")
                            parameters_str = tool_call["function"].get("arguments")
                            
                            # 尝试解析参数JSON
                            try:
                                parameters = json.loads(parameters_str) if parameters_str else None
                            except:
                                parameters = parameters_str
                            
                            # 更新聊天历史记录中的工具信息
                            execute_none(
                                "UPDATE apigent_chat_history SET tool_name = %s, parameters = %s WHERE id = %s",
                                (used_tool_name, json.dumps(parameters) if parameters else None, history_id)
                            )
        
        # 更新聊天历史记录，添加AI响应
        execute_none(
            "UPDATE apigent_chat_history SET response_content = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s",
            (json.dumps(response), history_id)
        )
        
        # 更新会话的更新时间
        execute_none(
            "UPDATE apigent_chat_session SET updated_at = CURRENT_TIMESTAMP WHERE session_id = %s",
            (session_id,)
        )
        
        # 直接返回 OpenAI 的响应
        return response
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/completions/stream")
async def chat_completions_stream(
    request: ChatCompletionRequest,
    session_id: str = Header(..., alias="Session-Id"),
    tool: str | None = Header(None, alias="Tool")
):
    """
    流式聊天完成API
    支持Server-Sent Events (SSE)格式的流式响应
    """
    if not session_id:
        raise HTTPException(status_code=400, detail="Session-Id is required")
    
    # 检查会话状态
    session = query_one_dict(
        "SELECT status FROM apigent_chat_session WHERE session_id = %s",
        (session_id,)
    )
    
    if session:
        # 会话存在，检查状态
        if session["status"] == 1:
            raise HTTPException(status_code=400, detail="Session is already completed")
    else:
        # 会话不存在，创建新会话
        create("apigent_chat_session", ChatSessionCreate(
            session_id=session_id,
            title=f"会话 {str(uuid.uuid4())[:8]}",
            status=0
        ))
    
    # 提取用户消息
    user_messages = [msg for msg in request.messages if msg.role == "user"]
    if not user_messages:
        raise HTTPException(status_code=400, detail="No user message found in the request")
    
    # 获取最后一条用户消息
    user_text = ""
    total_weight = 0
    for i, msg in enumerate(user_messages):
        # 使用指数衰减，最近的消息权重更高
        weight = 2 ** (len(user_messages) - i - 1)
        user_text += msg.content + "\n" * weight
        total_weight += weight
    
    async def generate_stream() -> AsyncGenerator[str, None]:
        history_id = None
        complete_response = {
            "openai_response": {
                "id": f"chatcmpl-{uuid.uuid4().hex[:29]}",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": "",
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "",
                        "tool_calls": []
                    },
                    "finish_reason": None
                }],
                "usage": {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0
                }
            },
            "timestamp": int(time.time()),
            "model": "",
            "tools_used": []
        }
        
        try:
            # 调用检索函数获取相关工具
            tools = retrieve_tools_by_text(user_text, similarity_threshold=0.4)
            tool_schemas = []
            used_tool_name = None
            parameters = None
            
            for tool in tools:
                logger.info(f"Tool: {tool}")
                tool_schema = get_tool_schema(tool["id"])
                tool_schemas.append(tool_schema)
                # 如果有工具被使用，记录第一个工具的名称
                if not used_tool_name and tool:
                    used_tool_name = tool.get("name")
                    # 如果有参数，也记录下来
                    if "parameters" in tool:
                        parameters = tool.get("parameters")

            # 打印工具结果
            logger.info("工具结果:")
            logger.info(json.dumps(tool_schemas, ensure_ascii=False, indent=2))
            
            # 保存用户请求到聊天历史
            chat_history_create = ChatHistoryCreate(
                session_id=session_id,
                request_content={"messages": request.messages},
                tool_name=used_tool_name,
                parameters=parameters
            )
            
            # 创建聊天历史记录
            history_record = create("apigent_chat_history", chat_history_create)
            history_id = history_record["id"]
            
            # 准备工具使用信息
            tools_used = [{"name": tool["function"]["name"], "key": tool["function"]["key"]} for tool in tool_schemas] if tool_schemas else []
            complete_response["tools_used"] = tools_used
            
            # 首先发送工具使用信息
            if tools_used:
                tools_info = {
                    "tools_used": tools_used,
                    "timestamp": int(time.time()),
                    "type": "tools_info"
                }
                yield f"data: {json.dumps(tools_info, ensure_ascii=False)}\n\n"
            
            # 获取流式AI响应 - 立即转发，不做阻塞处理
            async for chunk in parse_tool_schemas_stream(request.messages, tool_schemas):
                # 立即发送每个chunk，不做任何处理
                if "error" in chunk:
                    yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
                    yield "data: [DONE]\n\n"
                    return
                
                # 🚀 关键：立即发送SSE格式的数据，不做任何阻塞处理
                chunk_json = json.dumps(chunk, ensure_ascii=False)
                yield f"data: {chunk_json}\n\n"
                
                # 异步处理数据收集，不阻塞流式输出
                try:
                    # 更新完整响应用于后续数据库保存（异步处理）
                    if "choices" in chunk and len(chunk["choices"]) > 0:
                        choice = chunk["choices"][0]
                        if "delta" in choice:
                            delta = choice["delta"]
                            
                            # 更新内容
                            if "content" in delta and delta["content"]:
                                complete_response["openai_response"]["choices"][0]["message"]["content"] += delta["content"]
                            
                            # 更新工具调用
                            if "tool_calls" in delta:
                                for tool_call_delta in delta["tool_calls"]:
                                    if "index" in tool_call_delta:
                                        index = tool_call_delta["index"]
                                        # 确保工具调用列表有足够的元素
                                        while len(complete_response["openai_response"]["choices"][0]["message"]["tool_calls"]) <= index:
                                            complete_response["openai_response"]["choices"][0]["message"]["tool_calls"].append({
                                                "id": "",
                                                "type": "function",
                                                "function": {"name": "", "arguments": ""}
                                            })
                                        
                                        # 更新工具调用信息
                                        if "id" in tool_call_delta:
                                            complete_response["openai_response"]["choices"][0]["message"]["tool_calls"][index]["id"] = tool_call_delta["id"]
                                        if "function" in tool_call_delta:
                                            func_delta = tool_call_delta["function"]
                                            if "name" in func_delta:
                                                complete_response["openai_response"]["choices"][0]["message"]["tool_calls"][index]["function"]["name"] += func_delta["name"]
                                            if "arguments" in func_delta:
                                                complete_response["openai_response"]["choices"][0]["message"]["tool_calls"][index]["function"]["arguments"] += func_delta["arguments"]
                            
                            # 更新完成原因
                            if "finish_reason" in choice:
                                complete_response["openai_response"]["choices"][0]["finish_reason"] = choice["finish_reason"]
                    
                    # 更新模型信息
                    if "model" in chunk:
                        complete_response["openai_response"]["model"] = chunk["model"]
                        complete_response["model"] = chunk["model"]
                    
                    # 更新使用统计
                    if "usage" in chunk:
                        complete_response["openai_response"]["usage"] = chunk["usage"]
                        
                except Exception as process_error:
                    # 数据处理错误不应该影响流式输出
                    logger.warning(f"Chunk processing error: {str(process_error)}")
                    continue
            
            # 发送结束标记
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            logger.error(f"Error in streaming chat endpoint: {str(e)}")
            error_data = {
                "error": {
                    "message": str(e),
                    "type": "internal_error",
                    "code": "stream_error"
                }
            }
            yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"
        finally:
            # 在finally块中处理数据库更新，避免阻塞流式输出
            if history_id:
                try:
                    # 处理工具调用信息并更新数据库
                    if complete_response["openai_response"]["choices"][0]["message"]["tool_calls"]:
                        tool_calls = complete_response["openai_response"]["choices"][0]["message"]["tool_calls"]
                        if tool_calls and len(tool_calls) > 0:
                            # 获取第一个工具调用
                            tool_call = tool_calls[0]
                            if "function" in tool_call:
                                # 更新工具名称和参数
                                used_tool_name = tool_call["function"].get("name")
                                parameters_str = tool_call["function"].get("arguments")
                                
                                # 尝试解析参数JSON
                                try:
                                    parameters = json.loads(parameters_str) if parameters_str else None
                                except:
                                    parameters = parameters_str
                                
                                # 更新聊天历史记录中的工具信息
                                execute_none(
                                    "UPDATE apigent_chat_history SET tool_name = %s, parameters = %s WHERE id = %s",
                                    (used_tool_name, json.dumps(parameters) if parameters else None, history_id)
                                )
                    
                    # 更新聊天历史记录，添加AI响应
                    execute_none(
                        "UPDATE apigent_chat_history SET response_content = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s",
                        (json.dumps(complete_response), history_id)
                    )
                    
                    # 更新会话的更新时间
                    execute_none(
                        "UPDATE apigent_chat_session SET updated_at = CURRENT_TIMESTAMP WHERE session_id = %s",
                        (session_id,)
                    )
                except Exception as db_error:
                    logger.error(f"Database update error: {str(db_error)}")
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/plain; charset=utf-8"
        }
    )

