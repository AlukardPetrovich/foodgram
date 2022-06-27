from api.views import (FollowUnfollowViewSet, IngredientViewSet, RecipeViewSet,
                       TagViewSet)
from django.urls import include, path
from rest_framework.routers import DefaultRouter

router_v1 = DefaultRouter()
router_v1.register('tags', TagViewSet)
router_v1.register('ingredients', IngredientViewSet)
router_v1.register('recipes', RecipeViewSet)
router_v1.register('users', FollowUnfollowViewSet, basename='subscription')

urlpatterns = [
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router_v1.urls)),
]
