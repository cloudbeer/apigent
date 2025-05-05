from pydantic import BaseModel
from app.models.datetime import DateTimeString

class ToolEmbedding(BaseModel):
    id: int | None
    tool_id: int
    text_variant: str
    is_original: bool
    embedding: list[float]
    created_at: DateTimeString
    updated_at: DateTimeString

class ToolEmbeddingCreate(BaseModel):
    tool_id: int
    text_variant: str
    is_original: bool = False
    embedding: list[float]
    category_id: int | None = None
    created_at: DateTimeString | None = None
    updated_at: DateTimeString | None = None

class ToolEmbeddingUpdate(BaseModel):
    text_variant: str | None = None
    is_original: bool | None = None
    category_id: int | None = None
    embedding: list[float] | None = None
    updated_at: DateTimeString | None = None
