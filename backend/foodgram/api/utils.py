from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

import api.serializers as serializers
from recipes.models import Recipe, RecipeIngredient, RecipeTag


def add_ingredients_and_tags(recipe, ingredients, tags):
    """
    Функция привязывающая к рецепту ингредиенты и теги
    при создании или обновлении рецепта.
    """
    recipeingredients = [
        RecipeIngredient(
            recipe=recipe,
            amount=data.pop('amount'),
            ingredient=data.pop('ingredient')
        ) for data in ingredients
    ]
    RecipeIngredient.objects.bulk_create(recipeingredients)
    tag_list = [
        RecipeTag(
            tag=tag,
            recipe=recipe
        ) for tag in tags
    ]
    RecipeTag.objects.bulk_create(tag_list)


def add_or_remove_from_list(list_model, request, pk):
    """
    Функция добавляющая или удаляющая связь рецепта с пользователем
    в избранном или в списке покупок.
    """
    user = request.user
    recipe = get_object_or_404(Recipe, id=pk)
    if request.method == 'POST':
        list_model.objects.create(user=user, recipe=recipe)
        serializer = serializers.ShortRecipeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    if request.method == 'DELETE':
        list_model.objects.filter(user=user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
