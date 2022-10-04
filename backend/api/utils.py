from django.shortcuts import get_object_or_404

from recipes.models import FavoriteRecipe, Recipe


class Favoritecreate():
    def get_or_create_in_favoritrecipe(self, id):
        recipe_by_id = get_object_or_404(Recipe, id=id)
        return FavoriteRecipe.objects.get_or_create(
            recipe=recipe_by_id, user=self.request.user
        )[0]
