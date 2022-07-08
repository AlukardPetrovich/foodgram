import django_filters

from recipes.models import Ingredient, Recipe


class IngredientFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class ResipeFilter(django_filters.FilterSet):

    tags = django_filters.AllValuesMultipleFilter(
        field_name='tags__slug',
    )
    is_favorited = django_filters.BooleanFilter()

    is_in_shopping_cart = django_filters.BooleanFilter()

    class Meta:
        model = Recipe
        fields = ['author', 'is_in_shopping_cart', 'is_favorited', 'tags']
