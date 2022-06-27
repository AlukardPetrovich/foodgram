import django_filters
from recipes.models import Recipe


class ResipeFilter(django_filters.FilterSet):

    is_favorited = django_filters.BooleanFilter(
        field_name='is_favorited',
        method='favorite_filter'
    )
    is_in_shopping_cart = django_filters.BooleanFilter(
        field_name='is_in_shopping_cart',
        method='shopping_cart_filter'
    )
    tags = django_filters.AllValuesMultipleFilter(field_name='tags__id')

    def favorite_filter(self, queryset, name, value):
        if value and not self.request.user.is_anonymous:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def shopping_cart_filter(self, queryset, name, value):
        if value and not self.request.user.is_anonymous:
            return queryset.filter(shoppinglist__user=self.request.user)
        return queryset

    class Meta:
        model = Recipe
        fields = ('author', )
