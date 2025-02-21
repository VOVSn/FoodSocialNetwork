from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.views import IngredientViewSet, RecipeViewSet, TagViewSet, UserViewSet

router = DefaultRouter()

ENDPOINTS = [
    ('users', UserViewSet, 'users'),
    ('recipes', RecipeViewSet, 'recipes'),
    ('tags', TagViewSet, 'tags'),
    ('ingredients', IngredientViewSet, 'ingredients'),
]

for route, viewset, basename in ENDPOINTS:
    router.register(route, viewset, basename=basename)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
