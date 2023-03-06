from django.contrib import admin

from .models import (Favorite, Ingredient, IngredientInRecipe,
                     Recipe, ShoppingCart, Tag)


class AdminIngredientInRecipe(admin.TabularInline):
    model = IngredientInRecipe


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author', 'ingredients_recipe')
    readonly_fields = ('added_to_favorite',)
    list_filter = ('author', 'name', 'tags',)
    inlines = [
        AdminIngredientInRecipe,
    ]

    @admin.display(description='Добавлено в избранное')
    def added_to_favorite(self, obj):
        return obj.favorites.count()

    @admin.display(description='Ингредиенты')
    def ingredients_recipe(self, obj):
        ingredients_list = []
        for ingredient in obj.ingredients.all():
            ingredients_list.append(ingredient.name)
        return ingredients_list


class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'slug')


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    list_filter = ('name',)


class IngredientInRecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'ingredient', 'amount')


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(IngredientInRecipe, IngredientInRecipeAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
