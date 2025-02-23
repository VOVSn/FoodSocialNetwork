import django_filters
from django_filters import AllValuesMultipleFilter

from recipes.models import Recipe


class RecipeFilter(django_filters.FilterSet):
    is_favorited = django_filters.ChoiceFilter(
        choices=[(0, 'No'), (1, 'Yes')],
        field_name='favorites__user',
        method='filter_is_favorited'
    )
    is_in_shopping_cart = django_filters.ChoiceFilter(
        choices=[(0, 'No'), (1, 'Yes')],
        field_name='shopping_cart__user',
        method='filter_is_in_shopping_cart'
    )
    tags = AllValuesMultipleFilter(field_name='tags__slug')

    class Meta:
        model = Recipe
        fields = ['author', 'tags']

    def filter_is_favorited(self, queryset, name, value):
        if value == '1' and self.request.user.is_authenticated:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value == '1' and self.request.user.is_authenticated:
            return queryset.filter(shopping_cart__user=self.request.user)
        return queryset
