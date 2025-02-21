import django_filters
from recipes.models import Recipe


class RecipeFilter(django_filters.FilterSet):
    tags = django_filters.CharFilter(
        field_name='tags__slug', lookup_expr='in', distinct=True, 
        method='filter_by_tags'
    )
    is_favorited = django_filters.BooleanFilter(
        method='filter_is_favorited', label='Is Favorited'
    )
    is_in_shopping_cart = django_filters.BooleanFilter(
        method='filter_is_in_shopping_cart', label='Is in Shopping Cart'
    )
    author = django_filters.NumberFilter(field_name='author__id')

    class Meta:
        model = Recipe
        fields = []

    def filter_by_tags(self, queryset, name, value):
        # Check if tags parameter is passed as a comma-separated list
        tag_slugs = value.split(',')
        return queryset.filter(tags__slug__in=tag_slugs).distinct()

    def filter_is_favorited(self, queryset, name, value):
        # Filter recipes that are favorited by the authenticated user
        if value and self.request.user.is_authenticated:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        # Filter recipes that are in the shopping cart of the authenticated user
        if value and self.request.user.is_authenticated:
            return queryset.filter(shopping_cart__user=self.request.user)
        return queryset
