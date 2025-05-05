from fastapi import APIRouter, HTTPException
from typing import List, Optional, Dict, Any
from app.models.field import Field, FieldCreate, FieldUpdate
import app.utils.pg as db
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)    

router = APIRouter()

@router.get("/")
def read_fields(tool_id: int, offset: int = 0, limit: int = 10):
    where = []
    params = []
    if tool_id is not None:
        where.append(f"tool_id = %s")
        params.append(tool_id)
    
    conditions = db.QueryCondition(
        limit=limit,
        offset=offset,
        where=" AND ".join(where),
        params=params,
        cols=(
            "id", "tool_id", "name", "description", "data_type", "format",
            "is_required", "is_array", "array_items_type", "array_items_format",
            "default_value", "enum_values", "minimum", "maximum",
            "exclusive_minimum", "exclusive_maximum", "min_length", "max_length",
            "pattern", "min_items", "max_items", "unique_items", "multiple_of",
            "nullable", "deprecated", "allow_empty_value", "style", "explode",
            "allow_reserved", "schema_ref", "example", "reference_tool_id",
            "reference_path", "created_at", "updated_at"
        ),
        order_by="id ASC"
    )
    
    fields = db.list("apigent_field", conditions)
    total = db.count("apigent_field", conditions)
    
    return {
        "success": True,
        "data": fields,
        "total": total
    }

@router.get("/{field_id}")
def read_field(field_id: int):
    field = db.get_by_id("apigent_field", field_id)
    if not field:
        raise HTTPException(status_code=404, detail="Field not found")
    return {
        "success": True,
        "data": field
    }

@router.post("/")
def create_field(field: FieldCreate):
    if field.enum_values is not None:
        field.enum_values = json.dumps(field.enum_values)
    
    res = db.create("apigent_field", field)
    return {
        "success": True,
        "data": res
    }

@router.put("/{field_id}")
def update_field(field_id: int, field: FieldUpdate):
    if field.enum_values is not None:
        field.enum_values = json.dumps(field.enum_values)
    
    db.update("apigent_field", field_id, field)
    updated_field = db.get_by_id("apigent_field", field_id)
    return {
        "success": True,
        "data": updated_field
    }

@router.delete("/{field_id}")
def delete_field(field_id: int):
    db.delete("apigent_field", field_id)
    return {
        "success": True
    }
