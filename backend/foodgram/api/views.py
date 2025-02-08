from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from users.models import CustomUser, Favorite, ShoppingList, Subscription
from recipes.models import Recipe, Ingredient, Tag
from .serializers import (
    CustomUserSerializer,
    FavoriteSerializer,
    ShoppingListSerializer,
    RecipeSerializer,
    IngredientSerializer,
    TagSerializer,
    SubscriptionSerializer
)


# ViewSet for User model
class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer


# ViewSet for Recipe model
class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    @action(detail=True, methods=['post'])
    def add_to_favorites(self, request, pk=None):
        user = request.user
        recipe = self.get_object()
        favorite, created = Favorite.objects.get_or_create(user=user, recipe=recipe)
        if created:
            return Response({"status": "added to favorites"})
        return Response({"status": "already in favorites"})

    @action(detail=True, methods=['post'])
    def add_to_shopping_list(self, request, pk=None):
        user = request.user
        recipe = self.get_object()
        shopping_list, created = ShoppingList.objects.get_or_create(user=user, recipe=recipe)
        if created:
            return Response({"status": "added to shopping list"})
        return Response({"status": "already in shopping list"})


# ViewSet for Ingredient model
class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


# ViewSet for Tag model
class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


# ViewSet for Favorite model
class FavoriteViewSet(viewsets.ModelViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer


# ViewSet for ShoppingList model
class ShoppingListViewSet(viewsets.ModelViewSet):
    queryset = ShoppingList.objects.all()
    serializer_class = ShoppingListSerializer


# ViewSet for Subscription model (user subscriptions)
class SubscriptionViewSet(viewsets.ModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
