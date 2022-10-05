from django.shortcuts import get_object_or_404

from recipes.models import FavoriteRecipe, Recipe


class Favoritecreate():
    def get_recipe_by_id(self, id):
        return get_object_or_404(Recipe, id=id)

    def get_or_create_in_favoritrecipe(self, id):
        c_def_help = self.get_recipe_by_id(id)
        return FavoriteRecipe.objects.get_or_create(
            recipe=c_def_help, user=self.request.user
        )[0]
