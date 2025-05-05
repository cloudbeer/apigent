from fastapi import APIRouter, HTTPException, Request
from app.utils.ai import get_embedding, gen_text_variant
from app.models.tool import AbigentToolCreate, AbigentToolUpdate
from app.models.tool_embedding import ToolEmbeddingCreate
import app.utils.pg as db
from datetime import datetime
import logging
import json
from fastapi.responses import StreamingResponse
import asyncio
from app.utils.i18n import get_translator

logger = logging.getLogger(__name__)    

router = APIRouter()

@router.get("/")
def read_tools(offset: int = 0, limit: int = 10):

    conditions = db.QueryCondition(
        limit=limit,
        offset=offset,
        cols=("id", "name", "url", "http_method", "category_id", "updated_at"),
        order_by="id DESC"
    )
    tools = db.list("apigent_tool", conditions)
    total = db.count("apigent_tool", conditions)
    return {
        "success": True,
        "data": tools,
        "total": total
    }

@router.get("/{tool_id}")
def read_tool(tool_id: int):
    tool = db.get_by_id("apigent_tool", tool_id)
    return {
        "success": True,
        "data": tool
    }

@router.get("/{tool_id}/variants")
def read_tool_variants(tool_id: int):
    conditions = db.QueryCondition(
        cols=("id", "text_variant", "is_original"),
        where=f"tool_id = {tool_id}",
        order_by="is_original DESC, id ASC"
    )
    variants = db.list("apigent_tool_embedding", conditions)
    return {
        "success": True,
        "data": variants
    }

@router.post("/variants/")
def create_variant(variant: ToolEmbeddingCreate):
    print("--------------------------------")
    print(variant)
    print("--------------------------------")
    if variant.text_variant is None or variant.text_variant.strip() == "":
        raise HTTPException(status_code=400, detail="文本变体不能为空")
    variant.embedding = get_embedding(variant.text_variant)
    variant.is_original = False
    db.create("apigent_tool_embedding", variant)
    return {
        "success": True,
        "data": variant
    }

@router.put("/variants/{variant_id}")
def update_variant(variant_id: int, variant: ToolEmbeddingCreate):
    if variant.text_variant is None or variant.text_variant.strip() == "":
        raise HTTPException(status_code=400, detail="文本变体不能为空")
    variant.embedding = get_embedding(variant.text_variant)
    db.update("apigent_tool_embedding", variant_id, variant)
    return {
        "success": True,
        "data": variant
    }

@router.delete("/variants/{variant_id}")
def delete_variant(variant_id: int):
    db.delete("apigent_tool_embedding", variant_id)
    return {
        "success": True
    }

@router.post("/")
async def create_tool(tool: AbigentToolCreate, request: Request = None):
    _ = get_translator(request)
    async def event_generator():
        if tool.http_context is not None:
            tool.http_context = json.dumps(tool.http_context)
        
        tool.created_at = datetime.now()
        tool.updated_at = datetime.now()
        
        res = None
        try:
            res = db.create("apigent_tool", tool)
        except Exception as e:
            yield f"data: {json.dumps({
                'status': 'error',
                'message': _('创建工具失败: %(error)s') % {'error': str(e)}
            })}\n\n"
            await asyncio.sleep(0.1)
            return
        
        
        yield f"data: {json.dumps({'status': 'processing', 'message': _('开始生成文本变体')})}\n\n"
        await asyncio.sleep(0.1)
        
        system_prompt = _('text_variant_system_prompt')
        print(system_prompt)
        text_vars = gen_text_variant(tool.description, system_prompt)
        print(text_vars)
        
        for i, line in enumerate(text_vars):
            yield f"data: {json.dumps({
                'status': 'processing',
                'message': _('%(current)s/%(total)s: %(text)s') % {
                    'current': i+1,
                    'total': len(text_vars),
                    'text': line
                },
            })}\n\n"
            # print(i,line)
            embedding = get_embedding(line)
            dataCreate = ToolEmbeddingCreate(
                tool_id=res["id"],
                text_variant=line,
                embedding=embedding,
                category_id=tool.category_id
            )
            if i == 0:
                dataCreate.is_original = True
            db.create("apigent_tool_embedding", dataCreate)
            await asyncio.sleep(0.1)
        
        yield f"data: {json.dumps({
            'status': 'completed',
            'message': _('工具创建完成'),
            'data': res
        })}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@router.put("/{tool_id}")
def update_tool(tool_id: int, tool: AbigentToolUpdate):
    if tool.http_context is not None:
        tool.http_context = json.dumps(tool.http_context)
    
    tool.updated_at = datetime.now()
    db.update("apigent_tool", tool_id, tool)
    return {
        "success": True,
        "data": tool
    }

@router.delete("/{tool_id}")
def delete_tool(tool_id: int):
    conditions = db.QueryCondition(
        where="tool_id=%s",
        params=(tool_id,)
    )
    db.delete_where("apigent_tool_embedding", conditions)
    db.delete_where("apigent_field",conditions)
    db.delete("apigent_tool", tool_id)
    return {
        "success": True
    }
