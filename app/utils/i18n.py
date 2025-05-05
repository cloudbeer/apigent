import os
from babel.support import Translations
from fastapi import Request
import logging

logger = logging.getLogger(__name__)

# 设置翻译目录
TRANSLATIONS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "translations")

def get_translations(lang: str) -> Translations:
    """获取指定语言的翻译
    
    Args:
        lang: 语言代码，如 'zh', 'en'
        
    Returns:
        Translations: 翻译对象
    """
    try:
        translations = Translations.load(TRANSLATIONS_DIR, [lang])
        # 确保翻译对象使用 UTF-8 编码
        translations._catalog = {k: v.encode('utf-8').decode('utf-8') if isinstance(v, str) else v 
                               for k, v in translations._catalog.items()}
        return translations
    except Exception as e:
        logger.error(f"Error loading translations for {lang}: {str(e)}")
        # 如果加载失败，返回空翻译对象
        return Translations()

def get_language_from_request(request: Request) -> str:
    """从请求中获取语言设置
    
    Args:
        request: FastAPI 请求对象
        
    Returns:
        str: 语言代码，如 'zh', 'en'
    """
    if "Custom-Language" in request.headers:
        customLang = request.headers["Custom-Language"].split(",")[0].split("-")[0]
        return customLang
    return request.headers.get("Accept-Language", "zh").split(",")[0].split("-")[0]

def get_translator(request: Request):
    """获取翻译函数
    
    Args:
        request: FastAPI 请求对象
        
    Returns:
        function: 翻译函数
    """
    lang = get_language_from_request(request)
    translations = get_translations(lang)
    return translations.gettext 