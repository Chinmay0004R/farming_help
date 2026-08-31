from django.conf import settings
from django.utils.translation import get_language


def language_context(request):
    return {
        'language_code': get_language() or settings.LANGUAGE_CODE,
        'available_languages': settings.LANGUAGES,
    }
