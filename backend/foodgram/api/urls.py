from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.conf import settings
from django.conf.urls.static import static

from api.views import (
    UserViewSet, RecipeViewSet, TagViewSet, IngredientViewSet
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')

urlpatterns = [
    path('', include(router.urls)),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
