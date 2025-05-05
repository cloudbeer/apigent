from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from app.routers import category, field, pages, tool, chat
from app.utils.pg import init_pool
import os
import logging

# 加载环境变量
load_dotenv(override=True)

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))

logger = logging.getLogger(__name__)

init_pool(os.getenv("DATABASE_URL"))

app = FastAPI(
    title="APIGent",
    description="APIGent Service",
    version="0.1.0"
)

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="static"), name="static")

# API 路由
app.include_router(category.router, prefix="/api/categories", tags=["abigent"])
app.include_router(tool.router, prefix="/api/tools", tags=["abigent"])
app.include_router(field.router, prefix="/api/fields", tags=["abigent"])
app.include_router(chat.router, prefix="/api/chat", tags=["abigent"])
app.include_router(pages.router)

@app.get("/health")
async def health_check():
    """
    健康检查接口
    返回服务状态信息
    """
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "version": "0.1.0",
            "service": "apigent"
        }
    ) 