from fastapi import APIRouter, HTTPException
import app.utils.pg as db
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/")
def read_chat_sessions(offset: int = 0, limit: int = 10):
    """获取聊天会话列表"""
    conditions = db.QueryCondition(
        limit=limit,
        offset=offset,
        cols=("id", "session_id", "title", "case_summary", "status", "created_at", "updated_at"),
        order_by="updated_at DESC"
    )
    sessions = db.list("apigent_chat_session", conditions)
    total = db.count("apigent_chat_session", conditions)
    return {
        "success": True,
        "data": sessions,
        "total": total
    }

@router.get("/{session_id}")
def read_chat_session(session_id: str):
    """获取单个聊天会话详情"""
    conditions = db.QueryCondition(
        where="session_id = %s",
        params=(session_id,)
    )
    sessions = db.list("apigent_chat_session", conditions)
    if not sessions:
        raise HTTPException(status_code=404, detail="聊天会话不存在")
    return {
        "success": True,
        "data": sessions[0]
    }

@router.post("/")
def create_chat_session(session: dict):
    """创建新的聊天会话"""
    if not session.get("session_id"):
        raise HTTPException(status_code=400, detail="会话ID不能为空")
    if not session.get("title"):
        raise HTTPException(status_code=400, detail="会话标题不能为空")
    
    session["created_at"] = datetime.now()
    session["updated_at"] = datetime.now()
    
    result = db.create("apigent_chat_session", session)
    return {
        "success": True,
        "data": result
    }

@router.put("/{session_id}")
def update_chat_session(session_id: str, session: dict):
    """更新聊天会话信息"""
    conditions = db.QueryCondition(
        where="session_id = %s",
        params=(session_id,)
    )
    existing = db.list("apigent_chat_session", conditions)
    if not existing:
        raise HTTPException(status_code=404, detail="聊天会话不存在")
    
    session["updated_at"] = datetime.now()
    
    db.update_where("apigent_chat_session", conditions, session)
    return {
        "success": True,
        "data": session
    }

@router.delete("/{session_id}")
def delete_chat_session(session_id: str):
    """删除聊天会话及其历史记录"""
    conditions = db.QueryCondition(
        where="session_id = %s",
        params=(session_id,)
    )
    existing = db.list("apigent_chat_session", conditions)
    if not existing:
        raise HTTPException(status_code=404, detail="聊天会话不存在")
    
    # 删除会话（级联删除会自动删除相关的历史记录）
    db.delete_where("apigent_chat_session", conditions)
    return {
        "success": True
    }
