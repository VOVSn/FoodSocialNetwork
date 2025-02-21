from django.conf import settings
from rest_framework.pagination import PageNumberPagination


class FoodGramPagination(PageNumberPagination):
    page_size_query_param = 'limit'
    page_size = settings.PAGE_SIZE
