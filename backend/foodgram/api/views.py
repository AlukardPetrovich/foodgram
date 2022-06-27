from api.filters import ResipeFilter
from api.permissions import IsAuthor, ReadOnly
from api.serializers import (FollowUnfollowSerializer, IngredientSerializer,
                             ReadRecipeSerializer, TagSerializer,
                             WriteRecipeSerializer)
from api.utils import add_or_remove_from_list
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from recipes.models import Favorite, Ingredient, Recipe, ShoppingList, Tag
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from users.models import Follow, User


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [ReadOnly, ]


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [ReadOnly, ]


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = WriteRecipeSerializer

    permission_classes = [IsAuthor | ReadOnly]
    filterset_class = ResipeFilter

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PATCH']:
            return WriteRecipeSerializer
        return ReadRecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='favorite',
        permission_classes=[IsAuthor, ]
    )
    def favorite_endpoint(self, request, pk):
        return add_or_remove_from_list(Favorite, request, pk)

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='shopping_cart',
        permission_classes=[IsAuthor, ]
    )
    def shoping_list_endpoint(self, request, pk):
        return add_or_remove_from_list(ShoppingList, request, pk)

    @action(
        detail=False,
        url_path='download_shopping_cart',
        permission_classes=[IsAuthor, ]
    )
    def download_shopping_cart(self, request):
        list = ShoppingList.objects.filter(
            user=request.user
        ).values(
            'recipe__ingredients__name',
            'recipe__ingredients__measurement_unit'
        ).annotate(
            total_amount=Sum('recipe__recipeingredient__amount')
        )
        data = []
        for line in list:
            name = line['recipe__ingredients__name']
            amount = line['total_amount']
            measurement_unit = line['recipe__ingredients__measurement_unit']
            data.append(f'{name}, {amount} {measurement_unit}')
        response_context = '\n'.join(data)
        response = HttpResponse(response_context, content_type='text/plain')
        response['Content-Disposition'] = ('attachment;'
                                           'filename=shopping_list.txt')
        return response


class FollowUnfollowViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = FollowUnfollowSerializer
    permission_classes = [permissions.IsAuthenticated, ]

    @action(
        detail=False,
        methods=['post', 'delete'],
        url_path=r'(?P<id>\d+)/subscribe',
        permission_classes=[IsAuthor, ]
    )
    def follow_unfollow_endpoint(self, request, id):
        user = request.user
        following = get_object_or_404(User, id=id)
        if request.method == 'POST':
            Follow.objects.create(follower=user, following=following)
            serializer = FollowUnfollowSerializer(following)
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.method == 'DELETE':
            Follow.objects.filter(follower=user, following=following).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
