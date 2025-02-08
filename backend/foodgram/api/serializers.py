from rest_framework import serializers
from users.models import CustomUser, Favorite, ShoppingList, Subscription
from recipes.models import Recipe, Ingredient, Tag, RecipeIngredient


# Serializers for CustomUser model
class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = (
            'id', 'username', 'first_name', 'last_name', 'email', 'avatar'
        )


# Serializers for Favorite model
class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ('id', 'user', 'recipe')


# Serializers for ShoppingList model
class ShoppingListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingList
        fields = ('id', 'user', 'recipe')


# Serializers for Recipe model
class RecipeIngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeIngredient
        fields = ('ingredient', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(many=True)
    tags = serializers.StringRelatedField(many=True)

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'name', 'description', 'pic', 'time_to_cook', 'tags', 'ingredients')


# Serializers for Ingredient model
class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


# Serializers for Tag model
class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


# Subscription Serializer (for user subscriptions)
class SubscriptionSerializer(serializers.ModelSerializer):
    subscriber = CustomUserSerializer()
    author = CustomUserSerializer()

    class Meta:
        model = Subscription
        fields = ('id', 'subscriber', 'author')

