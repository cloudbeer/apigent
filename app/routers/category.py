from fastapi import APIRouter, HTTPException
from typing import List, Optional, Dict, Any
from app.utils.ai import get_embedding
from app.models.category import  ApigentCategoryCreate, ApigentCategoryUpdate
import app.utils.pg as db
from datetime import datetime
import logging

logger = logging.getLogger(__name__)    


router = APIRouter()

@router.get("/")
def read_categories(offset: int = 0, limit: int = 10):
    conditions = db.QueryCondition(
        limit=limit,
        offset=offset,
        cols=("id", "name", "description", "created_at", "updated_at",),
        order_by="id DESC"
    )
    categorys = db.list("apigent_category", conditions)
    total = db.count("apigent_category", conditions)
    return {
        "success": True,
        "data": categorys,
        "total": total
    }


@router.get("/{category_id}")
def read_categories(category_id: int):
    category = db.get_by_id("apigent_category", category_id)
    return {
        "success": True,
        "data": category
    }


@router.post("/")
def create_category(category: ApigentCategoryCreate):
    category.created_at = datetime.now()
    category.updated_at = datetime.now()
    res = db.create("apigent_category", category)
    return {
        "id": res["id"],
        "success": True,
        "data": category
    }

@router.put("/{category_id}")
def update_category(category_id: int, category: ApigentCategoryUpdate):
    category.updated_at = datetime.now()
    db.update("apigent_category", category_id, category)
    return {
        "success": True,
        "data": category
    }

@router.delete("/{category_id}")
def delete_category(category_id: int):
    db.delete("apigent_category", category_id)
    return {
        "success": True
    }