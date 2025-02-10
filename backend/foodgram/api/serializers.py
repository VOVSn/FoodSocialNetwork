from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField

from recipes.models import Recipe, Tag, Ingredient, RecipeIngredient
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


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar',
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


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, help_text='Пароль'
    )

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
            'avatar',
        )
        extra_kwargs = {
            'email': {
                'help_text': 'Адрес электронной почты'
            },
            'username': {
                'help_text': 'Уникальный юзернейм'
            },
            'first_name': {
                'help_text': 'Имя'
            },
            'last_name': {
                'help_text': 'Фамилия'
            },
        }

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserAvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = ('avatar',)


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
        return obj.shopping_list.filter(user=request.user).exists()


class RecipeWriteSerializer(serializers.ModelSerializer):
    ingredients = serializers.ListField(
        child=serializers.DictField(), write_only=True
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    image = Base64ImageField()
    text = serializers.CharField(source='description')
    cooking_time = serializers.IntegerField(source='time_to_cook')

    class Meta:
        model = Recipe
        fields = (
            'ingredients', 'tags', 'image', 'name', 'text', 'cooking_time'
        )

    def validate_cooking_time(self, value):
        if value < 1:
            raise serializers.ValidationError(
                'Время приготовления должно быть >= 1'
            )
        return value

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
            if ingredient_id is None or amount is None:
                raise serializers.ValidationError(
                    'Каждый ингредиент должен иметь id и amount.'
                )
            ingredient_obj = get_object_or_404(
                Ingredient, id=ingredient_id
            )
            RecipeIngredient.objects.create(
                recipe=recipe, ingredient=ingredient_obj, amount=amount
            )
