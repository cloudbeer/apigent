from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.utils.i18n import get_translations

router = APIRouter()

# 设置模板
templates = Jinja2Templates(directory="pages")



@router.get("/chatbox", response_class=HTMLResponse)
async def chatbox(request: Request, lang: str = "zh"):
    """渲染聊天页面"""
    translations = get_translations(lang)
    return templates.TemplateResponse(
        "chatbox.html",
        {
            "request": request,
            "lang": lang,
            "_": translations.gettext
        }
    )


@router.get("/chatbox-stream", response_class=HTMLResponse)
async def chatbox_stream(request: Request, lang: str = "zh"):
    """渲染流式聊天页面"""
    translations = get_translations(lang)
    return templates.TemplateResponse(
        "chatbox-stream.html",
        {
            "request": request,
            "lang": lang,
            "_": translations.gettext
        }
    )


@router.get("/chat-sessions", response_class=HTMLResponse)
async def chat_sessions(request: Request, lang: str = "zh"):
    """渲染会话列表"""
    translations = get_translations(lang)
    return templates.TemplateResponse(
        "chat-sessions.html",
        {
            "request": request,
            "lang": lang,
            "_": translations.gettext
        }
    )

@router.get("/chat-histories", response_class=HTMLResponse)
async def chat_histories(request: Request, lang: str = "zh"):
    """渲染聊天历史页面"""
    translations = get_translations(lang)
    return templates.TemplateResponse(
        "chat-histories.html",
        {
            "request": request,
            "lang": lang,
            "_": translations.gettext
        }
    )


@router.get("/manage-api", response_class=HTMLResponse)
async def manage_api(request: Request, lang: str = "zh"):
    """渲染主页"""
    translations = get_translations(lang)
    return templates.TemplateResponse(
        "manage-api.html",
        {
            "request": request,
            "lang": lang,
            "_": translations.gettext
        }
    )

@router.get("/categories", response_class=HTMLResponse)
async def categories(request: Request, lang: str = "zh"):
    translations = get_translations(lang)
    return templates.TemplateResponse(
        "categories.html",
        {
            "request": request,
            "lang": lang,
            "_": translations.gettext
        }
    )

@router.get("/tools", response_class=HTMLResponse)
async def tools(request: Request, lang: str = "zh"):
    translations = get_translations(lang)
    return templates.TemplateResponse(
        "tools.html",
        {
            "request": request,
            "lang": lang,
            "_": translations.gettext
        }
    )

@router.get("/fields", response_class=HTMLResponse)
async def fields(request: Request, tool_id: int, lang: str = "zh"):
    translations = get_translations(lang)
    return templates.TemplateResponse(
        "fields.html",
        {
            "request": request,
            "lang": lang,
            "tool_id": tool_id,
            "_": translations.gettext
        }
    )

@router.get("/", response_class=HTMLResponse)
async def index(request: Request, lang: str = "zh"):
    translations = get_translations(lang)
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "lang": lang,
            "_": translations.gettext
        }
    )