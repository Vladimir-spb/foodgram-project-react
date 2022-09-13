from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.utils.datastructures import MultiValueDictKeyError
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (FavoriteRecipe, Ingredient, IngredientsInRecipes,
                            Recipe, RecipesTags, Tag)
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueTogetherValidator
from users.models import Follow, User
from users.serializers import CustomUserSerializer


class TagSerializer(serializers.ModelSerializer):
    """
    Сериализатор для тегов.
    """

    class Meta:
        model = Tag
        fields = ('name', 'color', 'slug')


class IngredientSerialize(serializers.ModelSerializer):
    """
    Сериализатор для ингредиентов.
    """

    class Meta:
        model = Ingredient
        fields = ('name', 'measurement_unit')


class IngredientsInRecipesSerialize(serializers.ModelSerializer):
    """
    Сериализатор для вывода количества ингредиентов в рецепте.
    """

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientsInRecipes
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для рецептов.
    """

    author = CustomUserSerializer(
        read_only=True, default=serializers.CurrentUserDefault()
    )
    image = Base64ImageField()
    tags = TagSerializer(read_only=True, many=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        exclude = ['created', 'pub_date']

        validators = [
            UniqueTogetherValidator(
                queryset=Recipe.objects.all(),
                fields=('name', 'author'),
                message='Вы уже добавляли рецепт с данным именем',
            )
        ]

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        recipe = FavoriteRecipe.objects.filter(
            user__id=user.id, recipe__id=obj.id
        ).first()
        return recipe.favorite if recipe else False

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        recipe = FavoriteRecipe.objects.filter(
            user__id=user.id, recipe__id=obj.id
        ).first()
        return recipe.shopping_cart if recipe else False

    def get_ingredients(self, obj):
        qs = IngredientsInRecipes.objects.filter(recipe=obj)
        return IngredientsInRecipesSerialize(qs, many=True).data

    def validate(self, data):
        if 'ingredients' not in self.initial_data:
            raise serializers.ValidationError(
                {'error': 'Отсутствует информация об ингредиентах'}
            )
        lst_unique_ingredients = []
        for ingredient_item in self.initial_data['ingredients']:
            try:
                ingredient = Ingredient.objects.get(id=ingredient_item['id'])
            except ObjectDoesNotExist:
                raise serializers.ValidationError(
                    {'error': 'Данного ингредиента нет в базе'}
                )
            if int(ingredient_item['amount']) < 1:
                raise serializers.ValidationError(
                    {
                        'amount': 'Убедитесь, что это значение не меньше 1.'
                    }
                )
            if ingredient in lst_unique_ingredients:
                raise serializers.ValidationError(
                    {'error': 'Ингредиенты должны быть уникальными'}
                )
            lst_unique_ingredients.append(ingredient)
        data['ingredients'] = self.initial_data['ingredients']
        tags_ids = Tag.objects.all().values_list('id', flat=True)
        unexp_tags_ids = [
            idx for idx in self.initial_data['tags'] if idx not in tags_ids
        ]
        if unexp_tags_ids:
            raise ValidationError(
                detail={
                    'tags': [f'{unexp_tags_ids} - данных тегов нет в базе']
                }
            )
        return data

    @transaction.atomic
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags_ids = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient in ingredients:
            IngredientsInRecipes.objects.update_or_create(
                recipe=recipe,
                ingredient=Ingredient.objects.get(id=ingredient['id']),
                amount=ingredient['amount'],
            )
        for tags_id in tags_ids:
            RecipesTags.objects.update_or_create(
                recipe=recipe, tag=Tag.objects.get(id=tags_id)
            )
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.ingredients.clear()
        instance.tags.clear()

        ingredients = validated_data.pop('ingredients')
        tags_ids = validated_data.pop('tags')
        for ingredient in ingredients:
            IngredientsInRecipes.objects.create(
                recipe=instance,
                ingredient=Ingredient.objects.get(id=ingredient['id']),
                amount=ingredient['amount'],
            )
        for tags_id in tags_ids:
            RecipesTags.objects.create(
                recipe=instance, tag=Tag.objects.get(id=tags_id)
            )
        return super().update(instance, validated_data)


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для избранных рецептов.
    """

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(serializers.ModelSerializer):
    """
    Сериализатор для подписок.
    """
    recipes = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'id',
            'recipes',
            'is_subscribed',
            'username',
            'first_name',
            'last_name',
            'email',
            'recipes_count'
        )
        model = User

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(author=obj, user=user).exists()

    def get_recipes(self, obj):
        recipes = Recipe.objects.filter(author=obj).all()
        try:
            limit = int(self.context['request'].query_params['recipes_limit'])
            recipes = recipes[:limit]
        except MultiValueDictKeyError:
            pass
        return FavoriteRecipeSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()
