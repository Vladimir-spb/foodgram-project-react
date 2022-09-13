from django.contrib import admin

from .models import (FavoriteRecipe, Ingredient, IngredientsInRecipes, Recipe,
                     RecipesTags, Tag)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'slug',
        'name',
        'color',
    )
    list_display_links = (
        'pk',
        'slug',
    )
    list_editable = ('name',)
    search_fields = (
        'slug',
        'name',
    )


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'measurement_unit',
    )
    list_display_links = (
        'pk',
        'name',
    )
    list_editable = ('measurement_unit',)
    search_fields = ('name',)


@admin.register(IngredientsInRecipes)
class IngredientInRecipeAdmin(admin.ModelAdmin):
    autocomplete_fields = (
        'recipe',
        'ingredient',
    )
    list_display = (
        'recipe',
        'ingredient',
        'amount',
    )
    search_fields = (
        'ingredient__name',
        'recipe__name',
    )


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'author',
        'cooking_time',
        'favorites',
    )
    list_display_links = (
        'pk',
        'name',
    )
    list_filter = (
        'author',
        'name',
        'tags',
    )
    search_fields = (
        'author',
        'name',
    )
    empty_value_display = '-пусто-'

    @staticmethod
    def favorites(obj):
        return obj.favorite.filter(favorite=True).count()


@admin.register(FavoriteRecipe)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'user',
        'recipe',
        'shopping_cart',
        'favorite',
    )


@admin.register(RecipesTags)
class RecipesTags(admin.ModelAdmin):
    autocomplete_fields = (
        'recipe',
        'tag',
    )
    search_fields = (
        'recipe__name',
        'tag__name',
    )
