from typing import Dict, Any, Optional
from pydantic import BaseModel
from app.models.datetime import DateTimeString


class ChatSession(BaseModel):
    id: int
    session_id: str
    title: str
    case_summary: Optional[str] = None
    status: int = 0
    created_at: DateTimeString
    updated_at: DateTimeString


class ChatSessionCreate(BaseModel):
    session_id: str
    title: str
    case_summary: Optional[str] = None
    status: int = 0


class ChatSessionUpdate(BaseModel):
    title: Optional[str] = None
    case_summary: Optional[str] = None
    status: Optional[int] = None


class ChatHistory(BaseModel):
    id: int
    session_id: str
    request_content: Dict[str, Any]
    response_content: Optional[Dict[str, Any]] = None
    tool_name: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    created_at: DateTimeString
    updated_at: DateTimeString


class ChatHistoryCreate(BaseModel):
    session_id: str
    request_content: Dict[str, Any]
    response_content: Optional[Dict[str, Any]] = None
    tool_name: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None


class ChatHistoryUpdate(BaseModel):
    response_content: Optional[Dict[str, Any]] = None
    tool_name: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None 