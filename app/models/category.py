from pydantic import BaseModel
from app.models.datetime import DateTimeString


class ApigentCategoryCreate(BaseModel):
    name: str 
    description: str | None = None
    created_at: DateTimeString | None = None
    updated_at: DateTimeString | None = None

class ApigentCategoryUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    updated_at: DateTimeString | None = None
