from typing import Optional, Dict, Any
from pydantic import BaseModel
from app.models.datetime import DateTimeString


class AbigentTool(BaseModel):
    id: int
    name: str
    description: str
    url: str
    http_method: str
    http_context: Dict[str, Any]
    category_id: int | None = None
    embedding: list[float] | None = None
    created_at: DateTimeString
    updated_at: DateTimeString

class AbigentToolCreate(BaseModel):
    name: str
    description: str
    url: str | None = None
    http_method: str | None = None
    category_id: int | None = None
    http_context: Dict[str, Any] | None = None
    embedding: list[float] | None = None
    created_at: DateTimeString | None = None
    updated_at: DateTimeString | None = None

# Update
class AbigentToolUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    url: str | None = None
    http_method: str | None = None
    category_id: int | None = None
    http_context: Dict[str, Any] | None = None
    embedding: list[float] | None = None
    updated_at: DateTimeString | None = None