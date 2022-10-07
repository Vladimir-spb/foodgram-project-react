from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from api.serializers import FavoriteRecipeSerializer
from recipes.models import FavoriteRecipe, Recipe


class FavoriteCreate:
    def get_recipe_by_id(self, id):
        return get_object_or_404(Recipe, id=id)

    def get_or_create_in_favoritrecipe(self, id):
        c_def_help = self.get_recipe_by_id(id)
        return FavoriteRecipe.objects.get_or_create(
            recipe=c_def_help, user=self.request.user
        )[0]

    def add_to_list_or_delete(self, type_of_list, c_def, add=True):
        if type_of_list == 'FAVORITE':
            c_def.favorite = add
        if type_of_list == 'SHOPPING_CART':
            c_def.shopping_cart = add

    def recipe_favorite_or_shopping(self, request, id, type_of_list, help):
        c_def = self.get_or_create_in_favoritrecipe(id)
        if help is False:
            self.add_to_list_or_delete(type_of_list, c_def)
            c_def.save()
            c_def_help = self.get_recipe_by_id(id)
            serializer = FavoriteRecipeSerializer(c_def_help)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            self.add_to_list_or_delete(type_of_list, c_def, add=False)
            c_def.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
