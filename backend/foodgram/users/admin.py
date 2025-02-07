from django.contrib import admin
from .models import CustomUser, Favorite, ShoppingList


class FavoriteInline(admin.TabularInline):
    model = Favorite
    extra = 1
    verbose_name = 'Избранный рецепт'
    verbose_name_plural = 'Избранные рецепты'
    fk_name = 'user'


class ShoppingListInline(admin.TabularInline):
    model = ShoppingList
    extra = 1
    verbose_name = 'Рецепт в списке покупок'
    verbose_name_plural = 'Рецепты в списке покупок'
    fk_name = 'user'


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email', 'avatar')
    search_fields = ('username', 'first_name', 'last_name')
    list_filter = ('is_active', 'is_staff')
    ordering = ('username',)
    inlines = [FavoriteInline, ShoppingListInline]
    fieldsets = (
        (None, {
            'fields': (
                'username', 'first_name', 'last_name', 'email', 'avatar'
            )
        }),
        ('Permissions', {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions'
            )
        }),
    )
