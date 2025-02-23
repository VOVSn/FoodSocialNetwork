import re

from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer as DjoserUserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from foodgram import constants as c
from recipes.models import (
    Favorite, Ingredient, Recipe, RecipeIngredient, ShoppingCart, Tag
)
from users.models import Subscription


User = get_user_model()


class RecipeShortSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(source='pic', read_only=True)
    cooking_time = serializers.IntegerField(
        source='time_to_cook', read_only=True
    )

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        extra_kwargs = {
            'name': {'help_text': 'Название рецепта'},
        }


class UserSerializer(DjoserUserSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    avatar = serializers.SerializerMethodField()

    class Meta(DjoserUserSerializer.Meta):
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'avatar'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return (
            request.user.is_authenticated
            and obj.subscribers.filter(subscriber=request.user).exists()
        )

    def get_avatar(self, obj):
        if obj.avatar:
            return self.context['request'].build_absolute_uri(obj.avatar.url)
        return None


class SubscriptionSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(source='recipes.count')

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('recipes', 'recipes_count',)

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')
        recipes_qs = obj.recipes.all()
        if recipes_limit and recipes_limit.isdigit():
            recipes_qs = recipes_qs[:int(recipes_limit)]
        serializer = RecipeShortSerializer(
            recipes_qs, many=True, context=self.context
        )
        return serializer.data


class SubscriptionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ('author',)

    def validate_author(self, author):
        user = self.context['request'].user
        if user == author:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя.')
        if Subscription.objects.filter(
            subscriber=user,
            author=author
        ).exists():
            raise serializers.ValidationError(
                'Вы уже подписаны на этого автора.')
        return author

    def to_representation(self, instance):
        request = self.context.get('request')
        return SubscriptionSerializer(
            instance.author, context={'request': request}
        ).data


class UserAvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = ('avatar',)


class UserCreateSerializer(DjoserUserSerializer):
    username = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=c.NAME_MAX_LENGTH,
        help_text='Введите имя пользователя (буквы, цифры, ., @, +, - и _)',
    )
    email = serializers.EmailField(
        required=True,
        help_text='Введите электронную почту'
    )
    password = serializers.CharField(
        write_only=True, required=True, help_text='Пароль'
    )

    class Meta(DjoserUserSerializer.Meta):
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'password'
        )
        extra_kwargs = {
            'first_name': {'help_text': 'Введите имя пользователя'},
            'last_name': {'help_text': 'Введите фамилию пользователя'},
        }

    def validate_username(self, value):
        if not re.match(c.USERNAME_REGEX, value):
            raise serializers.ValidationError(
                'Имя пользователя может содержать только буквы, цифры и '
                'символы . @ + - _'
            )
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('Имя пользователя уже занято.')
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                'Пользователь с таким email уже существует.'
            )
        return value

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(
        write_only=True, required=True, help_text='Текущий пароль'
    )
    new_password = serializers.CharField(
        write_only=True, required=True, help_text='Новый пароль'
    )


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = serializers.ImageField(source='pic', read_only=True)
    text = serializers.CharField(source='description', read_only=True)
    cooking_time = serializers.IntegerField(
        source='time_to_cook', read_only=True
    )

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )

    def get_ingredients(self, obj):
        recipe_ingredients = obj.recipe_ingredients.all()
        return RecipeIngredientSerializer(
            recipe_ingredients, many=True
        ).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return request.user.is_authenticated and obj.favorites.filter(
            user=request.user
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return request.user.is_authenticated and obj.shopping_cart.filter(
            user=request.user
        ).exists()


class RecipeWriteSerializer(serializers.ModelSerializer):
    ingredients = serializers.ListField(
        child=serializers.DictField(), write_only=True
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    image = Base64ImageField(source='pic')
    text = serializers.CharField(source='description')
    cooking_time = serializers.IntegerField(source='time_to_cook')
    author = UserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'name', 'image', 'text',
            'cooking_time'
        )

    def validate(self, data):
        ingredients_data = data.get('ingredients')
        if not ingredients_data:
            raise serializers.ValidationError('Ингредиенты обязательны.')
        if 'tags' not in data or not data['tags']:
            raise serializers.ValidationError('Теги обязательны.')
        ingredient_ids = [
            ingredient.get('id') for ingredient in ingredients_data]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError(
                'Ингредиенты не могут повторяться.'
            )
        seen_ingredients = set()
        for ingredient in ingredients_data:
            ingredient_id = ingredient.get('id')
            amount = ingredient.get('amount')
            if amount < c.MIN_INGR_AMOUNT:
                raise serializers.ValidationError(
                    'Количество ингредиента должно быть >= '
                    f'{c.MIN_INGR_AMOUNT}'
                )
            if not Ingredient.objects.filter(id=ingredient_id).exists():
                raise serializers.ValidationError(
                    f'Ингредиент с id {ingredient_id} не существует.'
                )
            seen_ingredients.add(ingredient_id)
        tags = data.get('tags')
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError('Теги не могут повторяться.')
        return data

    def validate_cooking_time(self, value):
        if value < c.MIN_TIME_TO_COOK:
            raise serializers.ValidationError(
                f'Время должно быть >= {c.MIN_TIME_TO_COOK}'
            )
        return value

    def validate_image(self, value):
        if not value:
            raise serializers.ValidationError(
                'Изображение не может быть пустым.'
            )
        return value

    def to_representation(self, instance):
        serializer = RecipeReadSerializer(instance, context=self.context)
        return serializer.data

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        request = self.context.get('request')
        recipe = Recipe.objects.create(author=request.user, **validated_data)
        recipe.tags.set(tags)
        self._create_recipe_ingredients(recipe, ingredients_data)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        request = self.context.get('request')
        instance.author = request.user
        instance.tags.set(tags)
        instance.recipe_ingredients.all().delete()
        self._create_recipe_ingredients(instance, ingredients_data)
        return super().update(instance, validated_data)

    def _create_recipe_ingredients(self, recipe, ingredients_data):
        recipe_ingredients = [
            RecipeIngredient(
                recipe=recipe,
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount')
            ) for ingredient in ingredients_data
        ]
        RecipeIngredient.objects.bulk_create(recipe_ingredients)


class RecipeActionSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('recipe', 'user')

    def validate_recipe(self, recipe):
        user = self.context['request'].user
        if self.Meta.model.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError('Рецепт уже в списке покупок.')
        return recipe

    def delete(self, validated_data):
        user = self.context['request'].user
        recipe = validated_data['recipe']
        action_item = self.Meta.model.objects.filter(user=user, recipe=recipe)
        if action_item.exists():
            action_item.delete()
            return True
        return False

    def to_representation(self, instance):
        request = self.context.get('request')
        return RecipeShortSerializer(
            instance.recipe, context={'request': request}
        ).data


class ShoppingCartSerializer(RecipeActionSerializer):
    class Meta(RecipeActionSerializer.Meta):
        model = ShoppingCart


class FavoriteSerializer(RecipeActionSerializer):
    class Meta(RecipeActionSerializer.Meta):
        model = Favorite
