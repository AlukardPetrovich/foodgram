import re

from django.contrib.auth.hashers import make_password
from django.forms import ValidationError
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers, validators

from api.utils import add_ingredients_and_tags
from recipes.models import (
    Favorite, Ingredient, Recipe, RecipeIngredient, RecipeTag, ShoppingList,
    Tag,
)
from users.models import Follow, User


class ModifiedDjoserUserSerializer(UserSerializer):
    """
    Сериализатор для модели User. Наследуется от сериализатора из
    библиотеки Djoser, расширен полем отображающим статус подписки.
    """

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed',)

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return (
            user.is_authenticated
            and Follow.objects.filter(follower=user, following=obj).exists()
        )


class IngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор ингредиентов.
    """

    class Meta:
        model = Ingredient
        fields = ('__all__')


class TagSerializer(serializers.ModelSerializer):
    """
    Сериализатор тэгов.
    """

    name = serializers.ReadOnlyField()
    color = serializers.CharField()
    slug = serializers.SlugField()

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)


class RecipeIngredientsSerializer(serializers.ModelSerializer):
    """
    Сериализатор промежуточной модели связующий ингредиенты и рецепты.
    """

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient'
    )
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'amount', 'measurement_unit')


class WriteRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания рецептов.
    """
    author = serializers.SerializerMethodField()
    ingredients = RecipeIngredientsSerializer(
        many=True,
        source='recipeingredient_set'
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'tags', 'name', 'text', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart', 'image',
                  'cooking_time')

    def get_author(self, obj):
        serializer = ModifiedDjoserUserSerializer(read_only=True)
        return serializer.data

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        return (
            user.is_authenticated
            and Favorite.objects.filter(user=user, recipe=obj).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        return (
            user.is_authenticated
            and ShoppingList.objects.filter(user=user, recipe=obj).exists()
        )

    def create(self, validated_data):
        ingredients = validated_data.pop('recipeingredient_set')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        add_ingredients_and_tags(recipe, ingredients, tags)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('recipeingredient_set')
        tags = validated_data.pop('tags')
        super().update(instance, validated_data)
        RecipeIngredient.objects.filter(recipe=instance).delete()
        RecipeTag.objects.filter(recipe=instance).delete()
        add_ingredients_and_tags(instance, ingredients, tags)
        return instance

    def validate_ingredients(self, value):
        used_ingredients = []
        for ing in value:
            if ing['ingredient'] in used_ingredients:
                wrong_ingredient = ing['ingredient'].name
                raise serializers.ValidationError(
                    f'Задайте ингредиент {wrong_ingredient} одной строкой с'
                    ' общим количеством'
                )
            used_ingredients.append(ing['ingredient'])
        return value


class ReadRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для отображения рецептов.
    """

    author = ModifiedDjoserUserSerializer(read_only=True)
    ingredients = RecipeIngredientsSerializer(
        many=True,
        source='recipeingredient_set'
    )
    tags = TagSerializer(many=True)
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'tags', 'name', 'text', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart', 'image',
                  'cooking_time')

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        return (
            user.is_authenticated
            and Favorite.objects.filter(user=user, recipe=obj).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        return (
            user.is_authenticated
            and ShoppingList.objects.filter(user=user, recipe=obj).exists()
        )


class ShortRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для отображения рецептов.
    Версия с уменьшенным количеством полей.
    """

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class RegistrationSerializer(serializers.ModelSerializer):
    """
    Сериализатор для регистрации новых пользователей.
    """

    email = serializers.EmailField(
        max_length=254,
        validators=[validators.UniqueValidator(queryset=User.objects.all())]
    )
    username = serializers.CharField(
        max_length=150,
        validators=[validators.UniqueValidator(queryset=User.objects.all())]
    )
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    password = serializers.CharField(
        style={"input_type": "password"},
        write_only=True
    )

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password')

    def validate(self, data):
        if not re.match(r'^[\w.@+-]', data['username']):
            raise ValidationError(
                'Имя пользователя может содержать буквы, цифры, '
                'символы '
            )
        return data

    def create(self, validated_data):
        return User.objects.create(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=make_password(validated_data['password'])
        )


class FollowUnfollowSerializer(serializers.ModelSerializer):
    """
    Сериализатор подписок.
    """

    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count'
        )

    def get_is_subscribed(self, obj):
        follower = self.context.get('request').user
        return (
            follower.is_authenticated
            and Follow.objects.filter(
                follower=follower,
                following=obj
            ).exists()
        )

    def get_recipes(self, obj):
        recipes = Recipe.objects.filter(author=obj)
        serializer = ShortRecipeSerializer(recipes, many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()
