from fastapi import APIRouter, HTTPException
import app.utils.pg as db
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/")
def read_chat_histories(session_id: str, offset: int = 0, limit: int = 50):
    """获取指定会话的聊天历史记录"""
    # 首先检查会话是否存在
    session_conditions = db.QueryCondition(
        where="session_id = %s",
        params=(session_id,)
    )
    sessions = db.list("apigent_chat_session", session_conditions)
    if not sessions:
        raise HTTPException(status_code=404, detail="聊天会话不存在")
    
    # 获取历史记录
    conditions = db.QueryCondition(
        limit=limit,
        offset=offset,
        cols=("id", "session_id", "request_content", "response_content", "tool_name", "parameters", "created_at", "updated_at"),
        where="session_id = %s",
        params=(session_id,),
        order_by="created_at ASC"
    )
    histories = db.list("apigent_chat_history", conditions)
    total = db.count("apigent_chat_history", conditions)
    return {
        "success": True,
        "data": histories,
        "total": total
    }

@router.get("/{history_id}")
def read_chat_history(history_id: int):
    """获取单条聊天历史记录详情"""
    history = db.get_by_id("apigent_chat_history", history_id)
    if not history:
        raise HTTPException(status_code=404, detail="聊天历史记录不存在")
    return {
        "success": True,
        "data": history
    }

@router.post("/")
def create_chat_history(history: dict):
    """创建新的聊天历史记录"""
    if not history.get("session_id"):
        raise HTTPException(status_code=400, detail="会话ID不能为空")
    if not history.get("request_content"):
        raise HTTPException(status_code=400, detail="请求内容不能为空")
    
    # 检查会话是否存在
    session_conditions = db.QueryCondition(
        where="session_id = %s",
        params=(history["session_id"],)
    )
    sessions = db.list("apigent_chat_session", session_conditions)
    if not sessions:
        raise HTTPException(status_code=404, detail="聊天会话不存在")
    
    # 如果参数是字典，转换为JSON字符串
    if isinstance(history.get("parameters"), dict):
        history["parameters"] = json.dumps(history["parameters"])
    
    history["created_at"] = datetime.now()
    history["updated_at"] = datetime.now()
    
    result = db.create("apigent_chat_history", history)
    
    # 更新会话的更新时间
    db.update_where("apigent_chat_session", session_conditions, {"updated_at": datetime.now()})
    
    return {
        "success": True,
        "data": result
    }

@router.put("/{history_id}")
def update_chat_history(history_id: int, history: dict):
    """更新聊天历史记录"""
    existing = db.get_by_id("apigent_chat_history", history_id)
    if not existing:
        raise HTTPException(status_code=404, detail="聊天历史记录不存在")
    
    # 如果参数是字典，转换为JSON字符串
    if isinstance(history.get("parameters"), dict):
        history["parameters"] = json.dumps(history["parameters"])
    
    history["updated_at"] = datetime.now()
    
    db.update("apigent_chat_history", history_id, history)
    return {
        "success": True,
        "data": history
    }

@router.delete("/{history_id}")
def delete_chat_history(history_id: int):
    """删除单条聊天历史记录"""
    existing = db.get_by_id("apigent_chat_history", history_id)
    if not existing:
        raise HTTPException(status_code=404, detail="聊天历史记录不存在")
    
    db.delete("apigent_chat_history", history_id)
    return {
        "success": True
    }
