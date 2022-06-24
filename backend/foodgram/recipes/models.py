from django.db import models

from users.models import User


class Ingredient(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.TextField(blank=False, null=False)
    measurement_unit = models.TextField(blank=False, null=False)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class RecipeIngredients(models.Model):
    id = models.AutoField(primary_key=True)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.PROTECT)
    amount = models.IntegerField()
    recipe = models.ForeignKey('Recipe', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Ингредиент для рецепта'
        verbose_name_plural = 'Ингредиенты для рецепта'

    def __str__(self):
        return (f'для {self.recipe} требуется {self.ingredient.name},'
                f' {self.amount} {self.ingredient.measurement_unit}')


class Tag(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.TextField(
        max_length=200,
        null=False,
        blank=False,
        unique=True
    )
    color = models.CharField(
        max_length=7,
        null=False,
        blank=False,
        unique=True
    )
    slug = models.TextField(
        max_length=200,
        null=False,
        blank=False,
        unique=True,
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return f'{self.name}'


class RecipeTag(models.Model):
    id = models.AutoField(primary_key=True)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    recipe = models.ForeignKey('Recipe', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Тег для рецепта'
        verbose_name_plural = 'Теги для рецептов'

    def __str__(self):
        return f'{self.recipe} содержит тег {self.tag}'


class Recipe(models.Model):
    id = models.AutoField(primary_key=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=False,
        blank=False
    )
    name = models.TextField()
    text = models.TextField()
    image = models.ImageField(upload_to='images/')
    ingredients = models.ManyToManyField(
        Ingredient,
        through=RecipeIngredients
    )
    tags = models.ManyToManyField(Tag, through=RecipeTag)
    cooking_time = models.IntegerField()

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f'рецепт {self.name} от {self.author}'


class Favorites(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=False,
        blank=False
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        null=False,
        blank=False
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
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=False,
        blank=False
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        null=False,
        blank=False
    )

    class Meta:
        verbose_name = 'Рецепт в списке покупок'
        verbose_name_plural = 'Рецепты в списке покупок'

    def __str__(self):
        return f'{self.recipe} в списке покупок у {self.user}'
