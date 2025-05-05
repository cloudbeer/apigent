
from app.utils.i18n import get_translations

_ = get_translations("zh").gettext


text = _("正在处理第 %(current)s/%(total)s 个变体: %(text)s") % {
    "current": 2,
    "total": 10,
    "text": "test"
}

print(text)