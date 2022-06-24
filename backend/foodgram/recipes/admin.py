from django.contrib import admin

from recipes import models


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', )
    fields = ('name', 'author', 'text', 'image',
              'cooking_time', 'in_favorite',)
    readonly_fields = ('in_favorite', )
    list_filter = ('name', 'author', 'tags')

    @admin.display(description='How many times in favorites')
    def in_favorite(self, obj):
        return models.Favorites.objects.filter(recipe=obj).count()


admin.site.register(models.Tag)
admin.site.register(models.Recipe, RecipeAdmin)
admin.site.register(models.RecipeIngredients)
admin.site.register(models.ShoppingList)
admin.site.register(models.Ingredient)
admin.site.register(models.Favorites)
admin.site.register(models.RecipeTag)


