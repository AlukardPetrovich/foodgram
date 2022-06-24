import re

from django.contrib.auth.hashers import make_password
from django.forms import ValidationError
from djoser.serializers import UserSerializer
from rest_framework import serializers, validators

from api.fields import CustomImageField
from recipes.models import (Favorites, Ingredient, Recipe, RecipeIngredients,
                            RecipeTag, ShoppingList, Tag)
from users.models import Follow, User


class ModifiedDjoserUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed',)

    def get_is_subscribed(self, obj):
        try:
            user = self.context['request'].user
        except KeyError:
            return False
        if Follow.objects.filter(follower=user, following=obj).exists():
            return True
        return False


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('__all__')


class TagSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    color = serializers.CharField()
    slug = serializers.SlugField()

    class Meta:
        model = Tag
        fields = ('name', 'color', 'slug')


class RecipeTagSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all())

    class Meta:
        model = RecipeTag
        fields = ('id',)


class RecipeIngredientsSerializer(serializers.ModelSerializer):

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
        )
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'amount')

    def to_representation(self, instance):
        representation = {
            'id': instance.id,
            'name': instance.ingredient.name,
            'amount': instance.amount,
            'measurement_unit': instance.ingredient.measurement_unit
        }
        return representation


class RecipeSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    ingredients = RecipeIngredientsSerializer(
        many=True,
        source='recipeingredients_set'
    )
    tags = TagSerializer(read_only=True, many=True)
    image = CustomImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'tags', 'name', 'text', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart', 'image',
                  'cooking_time')

    def get_author(self, obj):
        serializer = ModifiedDjoserUserSerializer(obj.author)
        return serializer.data

    def get_is_favorited(self, obj):
        if Favorites.objects.filter(
            user=self.context.get('request').user,
            recipe=obj
        ).exists():
            return True
        return False

    def get_is_in_shopping_cart(self, obj):
        if ShoppingList.objects.filter(
            user=self.context.get('request').user,
            recipe=obj
        ).exists():
            return True
        return False

    def create(self, validated_data):
        ingredients = validated_data.pop('recipeingredients_set')
        tags = self.initial_data.get('tags')
        recipe = Recipe.objects.create(**validated_data)
        for data in ingredients:
            amount = data.pop('amount')
            ingredient = data.pop('id')
            RecipeIngredients.objects.create(
                ingredient=ingredient,
                recipe=recipe,
                amount=amount
            )
        for tag in tags:
            tag = Tag.objects.get(id=tag)
            RecipeTag.objects.create(tag=tag, recipe=recipe)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.name = validated_data.get('name')
        instance.text = validated_data.get('text')
        instance.cooking_time = validated_data.get('cooking_time')
        RecipeIngredients.objects.filter(recipe=instance).delete()
        for data in ingredients:
            amount = data.pop('amount')
            ingredient = data.pop('id')
            RecipeIngredients.objects.create(
                ingredient=ingredient,
                recipe=instance,
                amount=amount
            )
        Tag.objects.filter(recipe=instance).delete()
        for tag in tags:
            RecipeTag.objects.get_or_create(tag=tag, recipe=instance)
        return instance


class ShortRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class RegistrationSerializer(serializers.ModelSerializer):
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
        user = User.objects.create(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=make_password(validated_data['password'])
        )
        return user


class FollowSerializer(serializers.Serializer):

    class Meta:
        model = Follow
        fields = ('foloowing')


class FollowUnfollowSerializer(serializers.ModelSerializer):
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
        return True

    def get_recipes(self, obj):
        recipes = Recipe.objects.filter(author=obj)
        serializer = ShortRecipeSerializer(recipes, many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        count = Recipe.objects.filter(author=obj).count()
        return count
