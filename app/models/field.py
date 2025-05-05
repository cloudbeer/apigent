from typing import Dict, Any, List
from pydantic import BaseModel
from app.models.datetime import DateTimeString


class Field(BaseModel):
    id: int
    tool_id: int
    name: str
    description: str
    data_type: str
    format: str | None = None
    is_required: bool = False
    is_array: bool = False
    array_items_type: str | None = None
    array_items_format: str | None = None
    default_value: str | None = None
    enum_values: List[Any] | None = None
    minimum: float | None = None
    maximum: float | None = None
    exclusive_minimum: bool = False
    exclusive_maximum: bool = False
    min_length: int | None = None
    max_length: int | None = None
    pattern: str | None = None
    min_items: int | None = None
    max_items: int | None = None
    unique_items: bool = False
    multiple_of: float | None = None
    nullable: bool = False
    deprecated: bool = False
    allow_empty_value: bool = False
    style: str | None = None
    explode: bool = False
    allow_reserved: bool = False
    schema_ref: str | None = None
    example: str | None = None
    reference_tool_id: int | None = None
    reference_path: str | None = None
    created_at: DateTimeString
    updated_at: DateTimeString


class FieldCreate(BaseModel):
    tool_id: int
    name: str
    description: str
    data_type: str
    format: str | None = None
    is_required: bool = False
    is_array: bool = False
    array_items_type: str | None = None
    array_items_format: str | None = None
    default_value: str | None = None
    enum_values: List[Any] | None = None
    minimum: float | None = None
    maximum: float | None = None
    exclusive_minimum: bool = False
    exclusive_maximum: bool = False
    min_length: int | None = None
    max_length: int | None = None
    pattern: str | None = None
    min_items: int | None = None
    max_items: int | None = None
    unique_items: bool = False
    multiple_of: float | None = None
    nullable: bool = False
    deprecated: bool = False
    allow_empty_value: bool = False
    style: str | None = None
    explode: bool = False
    allow_reserved: bool = False
    schema_ref: str | None = None
    example: str | None = None
    reference_tool_id: int | None = None
    reference_path: str | None = None


class FieldUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    data_type: str | None = None
    format: str | None = None
    is_required: bool | None = None
    is_array: bool | None = None
    array_items_type: str | None = None
    array_items_format: str | None = None
    default_value: str | None = None
    enum_values: List[Any] | None = None
    minimum: float | None = None
    maximum: float | None = None
    exclusive_minimum: bool | None = None
    exclusive_maximum: bool | None = None
    min_length: int | None = None
    max_length: int | None = None
    pattern: str | None = None
    min_items: int | None = None
    max_items: int | None = None
    unique_items: bool | None = None
    multiple_of: float | None = None
    nullable: bool | None = None
    deprecated: bool | None = None
    allow_empty_value: bool | None = None
    style: str | None = None
    explode: bool | None = None
    allow_reserved: bool | None = None
    schema_ref: str | None = None
    example: str | None = None
    reference_tool_id: int | None = None
    reference_path: str | None = None

