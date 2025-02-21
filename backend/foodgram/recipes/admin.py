from django.contrib import admin

from .models import (
    Favorite, Ingredient, Recipe, RecipeIngredient, ShoppingCart, Tag
)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    min_num = 1
    verbose_name = 'Ингредиент рецепта'
    verbose_name_plural = 'Ингредиенты рецепта'


class FavoriteInline(admin.TabularInline):
    model = Favorite
    extra = 1
    verbose_name = 'Избранный рецепт'
    verbose_name_plural = 'Избранные рецепты'


class ShoppingCartInline(admin.TabularInline):
    model = ShoppingCart
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
    list_display = (
        'id', 'name', 'author', 'time_to_cook', 'short_link', 'favorites_count'
    )
    list_display_links = ('name', 'short_link')
    search_fields = ('name', 'author__username')
    list_filter = ('author', 'tags')
    ordering = ('name',)
    inlines = [RecipeIngredientInline, FavoriteInline, ShoppingCartInline]
    filter_horizontal = ('tags',)
    fieldsets = (
        (None, {
            'fields': (
                'author', 'name', 'pic', 'description', 'tags',
                'time_to_cook', 'short_link'
            )
        }),
    )
