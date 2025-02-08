from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CustomUserViewSet,
    RecipeViewSet,
    IngredientViewSet,
    TagViewSet,
    FavoriteViewSet,
    ShoppingListViewSet,
    SubscriptionViewSet
)

router = DefaultRouter()
router.register(r'users', CustomUserViewSet)
router.register(r'recipes', RecipeViewSet)
router.register(r'ingredients', IngredientViewSet)
router.register(r'tags', TagViewSet)
router.register(r'favorites', FavoriteViewSet)
router.register(r'shopping-list', ShoppingListViewSet)
router.register(r'subscriptions', SubscriptionViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]
