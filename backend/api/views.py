import datetime as dt

from api.filters import IngredientFilter, RecipeFilter
from api.paginations import CustomPageSizePagination
from api.permissions import AdminOrAuthorOrReadOnly
from api.serializers import (FavoriteRecipeSerializer, IngredientSerialize,
                             RecipeSerializer, TagSerializer)
from django_filters import rest_framework as filters
from recipes.models import (FavoriteRecipe, Ingredient, IngredientsInRecipes,
                            Recipe, Tag)
from rest_framework import filters as rest_filters
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from utils.create_pdf_file import create_pdf


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerialize
    filter_backends = (filters.DjangoFilterBackend, rest_filters.SearchFilter)
    filterset_class = IngredientFilter
    filterset_fields = ('name',)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (AdminOrAuthorOrReadOnly,)
    pagination_class = CustomPageSizePagination
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        if not self.request.data.get('tags'):
            raise ValidationError(detail={'tags': ['обязательное поле']})
        serializer.save(
            author=self.request.user, tags=self.request.data['tags']
        )

    def perform_update(self, serializer):
        if not self.request.data.get('tags'):
            raise ValidationError(detail={'tags': ['обязательное поле']})
        serializer.save(
            author=self.request.user, tags=self.request.data['tags']
        )

    @action(
        detail=False,
        permission_classes=[IsAuthenticated],
        url_path='download_shopping_cart',
    )
    def get_shopping_cart(self, request):
        shopping_cart_to_download = IngredientsInRecipes.objects.filter(
            recipe__favorite__user=self.request.user,
            recipe__favorite__shopping_cart=True,
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit',
            'amount',
        )

        obj_dic = {
            'file_name': '%s_%s.pdf'
            % (
                dt.datetime.utcnow().strftime('%Y-%m-%d'),
                self.request.user.username,
            ),
            'title': 'Список покупок',
            'user': 'Пользователь: %s %s'
            % (
                self.request.user.last_name,
                self.request.user.first_name,
            ),
            'text': [],
        }
        data = {}
        for idx, item in enumerate(shopping_cart_to_download):
            name = item['ingredient__name'].capitalize()
            unit = item['ingredient__measurement_unit']
            amount = item['amount']
            if name not in data:
                data[name] = [amount, unit]
                continue
            data[name][0] += amount

        for idx, (key, value) in enumerate(data.items()):
            obj_dic['text'].append(
                f'{idx + 1}. {key} - ' f'{value[0]} ' f'{value[1]}'
            )
        return create_pdf(obj_dic)

    @action(
        methods=['POST', 'DELETE'],
        detail=False,
        permission_classes=[IsAuthenticated],
        url_path='(?P<id>[0-9]+)/shopping_cart',
    )
    def shopping_cart(self, request, id):
        recipe_by_id = get_object_or_404(Recipe, id=id)
        if request.method == 'POST':
            favorite_recipe = FavoriteRecipe.objects.get_or_create(
                recipe=recipe_by_id, user=self.request.user
            )[0]
            if favorite_recipe.shopping_cart:
                raise ValidationError(
                    detail={'error': ['Рецепт уже был добавлен.']}
                )
            favorite_recipe.shopping_cart = True
            favorite_recipe.save()
            serializer = FavoriteRecipeSerializer(recipe_by_id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        favorite_recipe = FavoriteRecipe.objects.get(
            recipe=recipe_by_id, user=self.request.user
        )
        if not favorite_recipe.shopping_cart:
            raise ValidationError(
                detail={'error': ['Данного рецепта нет в списке покупок.']}
            )
        favorite_recipe.shopping_cart = False
        favorite_recipe.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['POST', 'DELETE'],
        detail=False,
        permission_classes=[IsAuthenticated],
        url_path='(?P<id>[0-9]+)/favorite',
    )
    def favorite(self, request, id):
        recipe_by_id = get_object_or_404(Recipe, id=id)
        if request.method == 'POST':
            favorite_recipe = FavoriteRecipe.objects.get_or_create(
                recipe=recipe_by_id, user=self.request.user
            )[0]
            if favorite_recipe.favorite:
                raise ValidationError(
                    detail={'error': ['Рецепт уже был добавлен в избранные.']}
                )
            favorite_recipe.favorite = True
            favorite_recipe.save()
            serializer = FavoriteRecipeSerializer(recipe_by_id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        favorite_recipe = FavoriteRecipe.objects.get(
            recipe=recipe_by_id, user=self.request.user
        )
        if not favorite_recipe.shopping_cart:
            raise ValidationError(
                detail={'error': ['Данного рецепта нет в избранных.']}
            )
        favorite_recipe.favorite = False
        favorite_recipe.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
