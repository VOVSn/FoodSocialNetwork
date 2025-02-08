from django.contrib import admin

from .models import (
    Tag, Ingredient, Recipe, RecipeIngredient, Favorite, ShoppingList
)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    verbose_name = 'Ингредиент рецепта'
    verbose_name_plural = 'Ингредиенты рецепта'


class FavoriteInline(admin.TabularInline):
    model = Favorite
    extra = 1
    verbose_name = 'Избранный рецепт'
    verbose_name_plural = 'Избранные рецепты'


class ShoppingListInline(admin.TabularInline):
    model = ShoppingList
    extra = 1
    verbose_name = 'Рецепт в списке покупок'
    verbose_name_plural = 'Рецепты в списке покупок'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')
    search_fields = ('name', 'slug')
    list_display_links = ('name',)
    ordering = ('name',)
    fieldsets = (
        (None, {
            'fields': ('name', 'slug')
        }),
    )


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('name', 'measurement_unit')
    list_display_links = ('name',)
    ordering = ('name',)
    fieldsets = (
        (None, {
            'fields': ('name', 'measurement_unit')
        }),
    )


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    readonly_fields = ('short_link',)
    list_display = ('id', 'name', 'author', 'time_to_cook', 'short_link')
    search_fields = ('name', 'author__username')
    list_filter = ('author', 'tags')
    ordering = ('name',)
    inlines = [RecipeIngredientInline, FavoriteInline, ShoppingListInline]
    filter_horizontal = ('tags',)
    fieldsets = (
        (None, {
            'fields': (
                'author', 'name', 'pic', 'description', 'tags',
                'time_to_cook', 'short_link'
            )
        }),
    )
