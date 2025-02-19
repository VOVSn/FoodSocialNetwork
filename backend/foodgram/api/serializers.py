import re

from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.shortcuts import get_object_or_404
from djoser.serializers import UserSerializer as DjoserUserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
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
        extra_kwargs = {
            'first_name': {
                'help_text': 'Введите имя пользователя'
            },
            'last_name': {
                'help_text': 'Введите фамилию пользователя'
            },
            'avatar': {
                'help_text': 'Загрузите аватар пользователя'
            },
        }

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Subscription.objects.filter(
            subscriber=request.user, author=obj
        ).exists()

    def get_avatar(self, obj):
        if obj.avatar:
            return self.context['request'].build_absolute_uri(obj.avatar.url)
        return None


class SubscriptionSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

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

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class UserAvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = ('avatar',)


class UserCreateSerializer(DjoserUserSerializer):
    username = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=150,
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
        if not re.match(r'^[\w.@+-]+\Z', value):
            raise serializers.ValidationError(
                'Имя пользователя может содержать только буквы, цифры и '
                'символы . @ + - _'
            )
        if len(value) > 150:
            raise serializers.ValidationError(
                'Имя пользователя не должно превышать 150 символов.'
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
        try:
            return User.objects.create_user(**validated_data)
        except IntegrityError:
            raise serializers.ValidationError({
                'username': 'Имя пользователя уже занято.'
            })


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
        extra_kwargs = {
            'name': {'help_text': 'Введите название тега'},
            'slug': {'help_text': 'Введите слаг для тега'},
        }


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
        extra_kwargs = {
            'name': {
                'help_text': 'Введите название ингредиента'
            },
            'measurement_unit': {
                'help_text': 'Введите единицу измерения ингредиента'
            },
        }


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )
    amount = serializers.FloatField()

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
        if not request or request.user.is_anonymous:
            return False
        return obj.favorites.filter(user=request.user).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return obj.shopping_cart.filter(user=request.user).exists()


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
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    author = UserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return obj.favorites.filter(user=request.user).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return obj.shopping_cart.filter(user=request.user).exists()

    def validate(self, data):
        if 'ingredients' not in data or not data['ingredients']:
            raise serializers.ValidationError('Ингредиенты обязательны.')
        if 'tags' not in data or not data['tags']:
            raise serializers.ValidationError('Теги обязательны.')
        return data

    def validate_cooking_time(self, value):
        if value < 1:
            raise serializers.ValidationError(
                'Время приготовления должно быть >= 1'
            )
        return value

    def validate_ingredients(self, ingredients_data):
        if not ingredients_data:
            raise serializers.ValidationError(
                'Ингредиенты не могут быть пустыми.'
            )
        seen_ingredients = set()
        for ingredient in ingredients_data:
            ingredient_id = ingredient.get('id')
            amount = ingredient.get('amount')
            if amount < 1:
                raise serializers.ValidationError(
                    'Количество ингредиента должно быть больше 0.'
                )
            if not Ingredient.objects.filter(id=ingredient_id).exists():
                raise serializers.ValidationError(
                    f'Ингредиент с id {ingredient_id} не существует.'
                )
            if ingredient_id in seen_ingredients:
                raise serializers.ValidationError(
                    'Ингредиенты не могут повторяться.'
                )
            seen_ingredients.add(ingredient_id)
        return ingredients_data

    def validate_tags(self, tags):
        if not tags:
            raise serializers.ValidationError('Теги не могут быть пустыми.')
        tag_ids = [tag.id for tag in tags]
        if len(tag_ids) != len(set(tag_ids)):
            raise serializers.ValidationError('Теги не могут повторяться.')

        return tags

    def validate_image(self, value):
        if not value:
            raise serializers.ValidationError(
                'Изображение не может быть пустым.'
            )
        return value

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['tags'] = TagSerializer(instance.tags, many=True).data
        recipe_ingredients = instance.recipe_ingredients.all()
        representation['ingredients'] = RecipeIngredientSerializer(
            recipe_ingredients, many=True
        ).data

        return representation

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        request = self.context.get('request')
        recipe = Recipe.objects.create(author=request.user, **validated_data)
        recipe.tags.set(tags)
        self._create_recipe_ingredients(recipe, ingredients_data)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', None)
        tags = validated_data.pop('tags', None)
        request = self.context.get('request')
        instance.author = request.user
        if tags is not None:
            instance.tags.set(tags)
        if ingredients_data is not None:
            instance.recipe_ingredients.all().delete()
            self._create_recipe_ingredients(instance, ingredients_data)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def _create_recipe_ingredients(self, recipe, ingredients_data):
        for ingredient in ingredients_data:
            ingredient_id = ingredient.get('id')
            amount = ingredient.get('amount')
            ingredient_obj = get_object_or_404(Ingredient, id=ingredient_id)
            RecipeIngredient.objects.create(
                recipe=recipe, ingredient=ingredient_obj, amount=amount
            )
