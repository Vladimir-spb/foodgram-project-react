from django.db.models import Sum
from django.utils import timezone
from django_filters import rest_framework as filters
from rest_framework import filters as rest_filters
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.filters import IngredientFilter, RecipeFilter
from api.paginations import CustomPageSizePagination
from api.permissions import AdminOrAuthorOrReadOnly
from api.serializers import (FavoriteRecipeSerializer, IngredientSerialize,
                             RecipeSerializer, TagSerializer)
from api.utils import Favoritecreate
from recipes.models import Ingredient, Recipe, Tag
from utils.create_pdf_file import create_pdf


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerialize
    filter_backends = (filters.DjangoFilterBackend, rest_filters.SearchFilter)
    filterset_class = IngredientFilter
    pagination_class = None
    filterset_fields = ('name',)
    search_fields = ('^name',)


class RecipeViewSet(Favoritecreate, viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (AdminOrAuthorOrReadOnly,)
    pagination_class = CustomPageSizePagination
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user
        )

    def perform_update(self, serializer):
        serializer.save(
            author=self.request.user
        )

    @action(
        detail=False,
        permission_classes=[IsAuthenticated],
        url_path='download_shopping_cart',
    )
    def get_shopping_cart(self, request):
        shopping_cart_to_download = Ingredient.objects.filter(
            ingredient_in_recipe__recipe__favorite__user=self.request.user,
            ingredient_in_recipe__recipe__favorite__shopping_cart=True,
        ).annotate(total=Sum('ingredient_in_recipe__amount')).values(
            'name',
            'total',
            'measurement_unit',
        )

        shopping_cart_context = {
            'file_name': '%s_%s.pdf'
            % (
                timezone.now().strftime('%Y-%m-%d'),
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
        for item in shopping_cart_to_download:
            name = item['name'].capitalize()
            unit = item['measurement_unit']
            amount = item['total']
            data[name] = [amount, unit]

        for idx, (key, value) in enumerate(data.items()):
            shopping_cart_context['text'].append(
                f'{idx + 1}. {key} - ' f'{value[0]} ' f'{value[1]}'
            )
        return create_pdf(shopping_cart_context)

    @action(
        methods=['POST', 'DELETE'],
        detail=False,
        permission_classes=[IsAuthenticated],
        url_path='(?P<id>[0-9]+)/shopping_cart',
    )
    def shopping_cart(self, request, id):
        c_def = self.get_or_create_in_favoritrecipe(id)
        try:
            if c_def.shopping_cart:
                raise ValidationError(
                    detail={'error': ['Рецепт уже был добавлен.']}
                )
            c_def.shopping_cart = True
            c_def.save()
            c_def_help = self.get_recipe_by_id(id)
            serializer = FavoriteRecipeSerializer(c_def_help)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception:
            if not c_def.shopping_cart:
                raise ValidationError(
                    detail={'error': ['Данного рецепта нет в списке покупок.']}
                )
            c_def.shopping_cart = False
            c_def.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['POST', 'DELETE'],
        detail=False,
        permission_classes=[IsAuthenticated],
        url_path='(?P<id>[0-9]+)/favorite',
    )
    def favorite(self, request, id):
        c_def = self.get_or_create_in_favoritrecipe(id)
        try:
            if c_def.favorite:
                raise ValidationError(
                    detail={'error': ['Рецепт уже был добавлен в избранные']}
                )
            c_def.favorite = True
            c_def.save()
            c_def_help = self.get_recipe_by_id(id)
            serializer = FavoriteRecipeSerializer(c_def_help)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception:
            if not c_def.favorite:
                raise ValidationError(
                    detail={'error': ['Данного рецепта нет в избранных.']}
                )
            c_def.favorite = False
            c_def.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
