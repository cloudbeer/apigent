from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.utils.i18n import get_translations

router = APIRouter()

# 设置模板
templates = Jinja2Templates(directory="pages")



@router.get("/chatbox", response_class=HTMLResponse)
async def manage_api(request: Request, lang: str = "zh"):
    """渲染主页"""
    translations = get_translations(lang)
    return templates.TemplateResponse(
        "chatbox.html",
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