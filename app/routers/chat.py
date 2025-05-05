from fastapi import APIRouter, HTTPException, Header
import logging
from app.utils.retrieve import retrieve_tools_by_text
from app.utils.preproccess import get_tool_schema
from pydantic import BaseModel
from typing import List, Optional
from app.utils.pg import query_one_dict, execute_dict, create, update, delete, detail, list_all
from app.utils.ai import parse_tool_schemas
from app.models.chat import ChatSessionCreate
import json
import uuid
import time
from openai.types.chat import ChatCompletionMessage

logger = logging.getLogger(__name__)    

router = APIRouter()

class Message(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    messages: List[Message]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 1000

@router.post("/")
async def chat(request: ChatCompletionRequest):
    user_messages = [msg.content for msg in request.messages if msg.role == "user"]
    if not user_messages:
        raise HTTPException(status_code=400, detail="No user message found in the request")
    
    text = user_messages[-1]
    logger.info(f"Received chat request: {text}")
    """
    根据用户输入的文本检索相关的工具
    
    Args:
        text: 用户输入的查询文本
        
    Returns:
        List[Dict[str, Any]]: 匹配的工具列表
    """
    try:
        # 调用检索函数获取相关工具
        tools = retrieve_tools_by_text(text, similarity_threshold=0.4)
        for tool in tools:
            logger.info(f"Tool: {tool}")
            tool_schema = get_tool_schema(tool["id"])
            return {"tools": [tool_schema]}
        return {"tools": []}
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

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
        for tool in tools:
            print(f"Tool: {tool}")
            tool_schema = get_tool_schema(tool["id"])
            tool_schemas.append(tool_schema)

        # 打印工具结果
        print("工具结果:")
        print(json.dumps(tool_schemas, ensure_ascii=False, indent=2))
        
        # print(tool_schemas)

        response = parse_tool_schemas(request.messages, tool_schemas)
        
        
        # 直接返回 OpenAI 的响应
        return response
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

