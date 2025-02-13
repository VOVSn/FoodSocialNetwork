from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import FoodgramUser, Subscription
from recipes.models import Favorite, ShoppingCart


class FavoriteInline(admin.TabularInline):
    model = Favorite
    extra = 1
    verbose_name = 'Избранный рецепт'
    verbose_name_plural = 'Избранные рецепты'
    fk_name = 'user'


class ShoppingCartInline(admin.TabularInline):
    model = ShoppingCart
    extra = 1
    verbose_name = 'Рецепт в списке покупок'
    verbose_name_plural = 'Рецепты в списке покупок'
    fk_name = 'user'


class SubscriptionAsSubscriberInline(admin.TabularInline):
    model = Subscription
    extra = 1
    verbose_name = 'Подписка'
    verbose_name_plural = 'Подписки'
    fk_name = 'subscriber'


class SubscriptionAsAuthorInline(admin.TabularInline):
    model = Subscription
    extra = 1
    verbose_name = 'Подписчик'
    verbose_name_plural = 'Подписчики'
    fk_name = 'author'


@admin.register(FoodgramUser)
class CustomUserAdmin(UserAdmin):
    list_display = (
        'username', 'first_name', 'last_name', 'email', 'avatar'
    )
    search_fields = ('username', 'first_name', 'last_name')
    list_filter = ('is_active', 'is_staff')
    ordering = ('username',)
    inlines = [
        FavoriteInline, ShoppingCartInline,
        SubscriptionAsSubscriberInline, SubscriptionAsAuthorInline,
    ]
    fieldsets = (
        (None, {
            'fields': (
                'username', 'first_name', 'last_name', 'email', 'avatar'
            )
        }),
        ('Permissions', {
            'fields': (
                'is_active', 'is_staff', 'is_superuser', 'groups',
                'user_permissions'
            )
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined')
        }),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'first_name', 'last_name', 'email', 'avatar',
                'password1', 'password2'
            )
        }),
    )
