from django.core.validators import MinValueValidator
from django.db import models
from users.models import User


class Ingredient(models.Model):
    name = models.TextField()
    measurement_unit = models.TextField()

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class RecipeIngredient(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        related_name='recipe_ingredient',
        on_delete=models.PROTECT
        )
    amount = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)]
    )
    recipe = models.ForeignKey('Recipe', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Ингредиент для рецепта'
        verbose_name_plural = 'Ингредиенты для рецепта'
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='unique_ingredient_for_recipe',
            ),
        ]

    def __str__(self):
        return (f'для {self.recipe} требуется {self.ingredient.name},'
                f' {self.amount} {self.ingredient.measurement_unit}')


class Tag(models.Model):
    name = models.TextField(
        max_length=200,
        unique=True
    )
    color = models.CharField(
        max_length=7,
        unique=True
    )
    slug = models.TextField(
        max_length=200,
        unique=True,
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return f'{self.name}'


class RecipeTag(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.PROTECT)
    recipe = models.ForeignKey('Recipe', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Тег для рецепта'
        verbose_name_plural = 'Теги для рецептов'
        constraints = [
            models.UniqueConstraint(
                fields=['tag', 'recipe'],
                name='unique_tag_for_recipe',
            ),
        ]

    def __str__(self):
        return f'{self.recipe} содержит тег {self.tag}'


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    name = models.TextField()
    text = models.TextField()
    image = models.ImageField(upload_to='images/')
    ingredients = models.ManyToManyField(
        Ingredient,
        through=RecipeIngredient
    )
    tags = models.ManyToManyField(Tag, through=RecipeTag)
    cooking_time = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)]
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f'рецепт {self.name} от {self.author}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='single_favorite',
            ),
        ]

    def __str__(self):
        return f'{self.recipe} в избранном у {self.user}'


class ShoppingList(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Рецепт в списке покупок'
        verbose_name_plural = 'Рецепты в списке покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_recipe_in_shopping_list',
            ),
        ]

    def __str__(self):
        return f'{self.recipe} в списке покупок у {self.user}'
