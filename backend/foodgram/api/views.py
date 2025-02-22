import io
import os

from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.views.generic import RedirectView
from djoser.views import UserViewSet as DjoserUserViewSet
from dotenv import load_dotenv
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAuthenticated, IsAuthenticatedOrReadOnly, SAFE_METHODS
)
from rest_framework.response import Response

from api.paginations import FoodGramPagination
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (
    SubscriptionSerializer, UserAvatarSerializer, PasswordChangeSerializer,
    TagSerializer, IngredientSerializer, RecipeWriteSerializer,
    RecipeReadSerializer, SubscriptionCreateSerializer,
    ShoppingCartCreateSerializer, FavoriteCreateSerializer
)
from recipes.models import (
    Ingredient, Recipe, RecipeIngredient, ShoppingCart, Tag
)
from users.models import Subscription


load_dotenv()

DOMAIN = os.getenv('DOMAIN', 'localhost')

User = get_user_model()


class UserViewSet(DjoserUserViewSet):
    queryset = User.objects.all()
    pagination_class = FoodGramPagination
    permission_classes = [IsAuthenticatedOrReadOnly]

    @action(
        detail=False,
        permission_classes=[IsAuthenticated],
        url_path='me'
    )
    def me(self, request, *args, **kwargs):
        return super().me(request, *args, **kwargs)

    @action(
        detail=False,
        methods=['put', 'delete'],
        permission_classes=[IsAuthenticated],
        url_path='me/avatar'
    )
    def avatar(self, request):
        user = request.user
        if request.method == 'PUT':
            serializer = UserAvatarSerializer(instance=user, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        if user.avatar:
            user.avatar.delete(save=False)
        user.avatar = None
        user.save(update_fields=['avatar'])
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['post'],
        permission_classes=[IsAuthenticated],
        url_path='set_password'
    )
    def set_password(self, request):
        serializer = PasswordChangeSerializer(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        user = request.user
        current_password = serializer.validated_data.get('current_password')
        if not user.check_password(current_password):
            return Response(
                {'current_password': ['Неверный текущий пароль.']},
                status=status.HTTP_400_BAD_REQUEST
            )
        user.set_password(serializer.validated_data.get('new_password'))
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
        url_path='subscriptions'
    )
    def subscriptions(self, request):
        subscriptions = User.objects.filter(
            subscribers__subscriber=request.user
        )
        page = self.paginate_queryset(subscriptions)
        serializer = SubscriptionSerializer(
            page, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated],
        url_path='subscribe'
    )
    def subscribe(self, request, id=None):
        author = get_object_or_404(User, pk=id)
        serializer = SubscriptionCreateSerializer(
            data={'author': author.id}, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def unsubscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, pk=id)
        subscription = Subscription.objects.filter(
            subscriber=user, author=author
        )
        if subscription.exists():
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'Вы не подписаны на этого автора.'},
            status=status.HTTP_400_BAD_REQUEST
        )


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        name = self.request.query_params.get('name')
        if name:
            queryset = queryset.filter(name__istartswith=name)
        return queryset


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = FoodGramPagination
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def get_queryset(self):
        queryset = Recipe.objects.all()
        request = self.request
        is_favorited = request.query_params.get('is_favorited')
        if is_favorited == '1' and request.user.is_authenticated:
            queryset = queryset.filter(favorites__user=request.user)
        is_in_shopping_cart = request.query_params.get('is_in_shopping_cart')
        if is_in_shopping_cart == '1' and request.user.is_authenticated:
            queryset = queryset.filter(shopping_cart__user=request.user)
        author = request.query_params.get('author')
        if author:
            queryset = queryset.filter(author__id=author)
        tags = request.query_params.getlist('tags')
        if tags:
            queryset = queryset.filter(tags__slug__in=tags).distinct()
        return queryset

    def get_ingredients_list(self, request):
        shopping_cart = ShoppingCart.objects.filter(user=request.user)
        recipe_ids = shopping_cart.values_list('recipe', flat=True)
        ingredients = RecipeIngredient.objects.filter(
            recipe__in=recipe_ids
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(total_amount=Sum('amount'))
        lines = []
        for item in ingredients:
            line = (f'{item["ingredient__name"]} '
                    f'({item["ingredient__measurement_unit"]}) - '
                    f'{item["total_amount"]}')
            lines.append(line)
        return '\n'.join(lines)

    @action(
        detail=True,
        methods=['get'],
        url_path='get-link'
    )
    def get_link(self, request, pk=None):
        recipe = self.get_object()
        if not recipe.short_link:
            recipe.save()
        return Response({'short-link': request.build_absolute_uri(
            f'/s/{recipe.short_link}'
        )})

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
        url_path='download_shopping_cart'
    )
    def download_shopping_cart(self, request):
        content = self.get_ingredients_list(request)
        content_bytes = content.encode('utf-8')
        file = io.BytesIO(content_bytes)
        response = FileResponse(file, content_type='text/plain')
        response[
            'Content-Disposition'] = 'attachment; filename="shopping_cart.txt"'
        return response

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated],
        url_path='shopping_cart'
    )
    def add_to_shopping_cart(self, request, pk=None):
        recipe = self.get_object()
        serializer = ShoppingCartCreateSerializer(
            data={'recipe': recipe.id}, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @add_to_shopping_cart.mapping.delete
    def remove_from_shopping_cart(self, request, pk=None):
        recipe = self.get_object()
        serializer = ShoppingCartCreateSerializer(
            data={'recipe': recipe.id}, context={'request': request}
        )
        if serializer.delete({'recipe': recipe}):
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'Рецепт отсутствует в списке покупок.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated],
        url_path='favorite'
    )
    def add_to_favorite(self, request, pk=None):
        recipe = self.get_object()
        serializer = FavoriteCreateSerializer(
            data={'recipe': recipe.id}, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @add_to_favorite.mapping.delete
    def remove_from_favorite(self, request, pk=None):
        recipe = self.get_object()
        serializer = FavoriteCreateSerializer(
            data={'recipe': recipe.id}, context={'request': request}
        )
        if serializer.delete({'recipe': recipe}):
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'Рецепт отсутствует в избранном.'},
            status=status.HTTP_400_BAD_REQUEST
        )


class ShortLinkRedirectView(RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        recipe = get_object_or_404(Recipe, short_link=kwargs['short_link'])
        return f'/recipes/{recipe.id}/'
