from django.utils.crypto import get_random_string

from foodgram import constants as c


def generate_unique_short_link():
    from recipes.models import Recipe

    while True:
        candidate = get_random_string(c.SHORT_LINK_LENGTH)
        if not Recipe.objects.filter(short_link=candidate).exists():
            return candidate
