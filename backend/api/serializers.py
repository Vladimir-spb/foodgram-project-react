from django.db import transaction
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (FavoriteRecipe, Ingredient, IngredientsInRecipes,
                            Recipe, Tag)
from users.models import Follow, User
from users.serializers import CustomUserSerializer


class TagSerializer(serializers.ModelSerializer):
    """
    Сериализатор для тегов.
    """

    class Meta:
        model = Tag
        fields = '__all__'
        lookup_field = 'slug'


class IngredientSerialize(serializers.ModelSerializer):
    """
    Сериализатор для ингредиентов.
    """

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientsInRecipesSerialize(serializers.ModelSerializer):
    """
    Сериализатор для вывода количества ингредиентов в рецепте.
    """

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient.id'
    )
    name = serializers.CharField(
        read_only=True,
        source='ingredient.name'
    )
    measurement_unit = serializers.CharField(
        read_only=True,
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
    ingredients = IngredientsInRecipesSerialize(
        many=True
    )
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

    def validate(self, data):
        if data['cooking_time'] < 1:
            raise ValidationError(
                {'error': 'Время приготовления не может быть меньше 1 минуты!'}
            )
        if len(data['ingredients']) == 0:
            raise ValidationError(
                {'error': 'Нужно выбрать хотя бы один ингредиент!'}
            )
        if len(data['tags']) == 0:
            raise ValidationError(
                {'error': 'Нужно выбрать хотя бы один тэг!'}
            )
        if len(data['tags']) > len(set(data['tags'])):
            raise ValidationError({'error': 'Теги не могут повторяться!'})
        lst_unique_ingredients = []
        for ingredient_item in data['ingredients']:
            if ingredient_item['amount'] < 1:
                raise ValidationError(
                    {'error': 'Колличество ингредиента должно быть больше 1'}
                )
            lst_unique_ingredients.append(ingredient_item['id'])
        if len(lst_unique_ingredients) > len(set(lst_unique_ingredients)):
            raise ValidationError(
                {'error': 'Ингредиенты должны быть уникальными'}
            )
        tags_list = []
        for tag in data['tags']:
            if tag in tags_list:
                raise serializers.ValidationError(
                    {'error': 'Тэги должны быть уникальными!'}
                )
            tags_list.append(tag)
        return data

    @transaction.atomic
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags_ids = validated_data.pop('tags')
        return Recipe.objects.bulk_create(
            ingredient=ingredients,
            tag=tags_ids,
        )

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.ingredients.clear()
        instance.tags.clear()

        ingredients = validated_data.pop('ingredients')
        tags_ids = validated_data.pop('tags')
        Recipe.objects.bulk_create(
            ingredient=ingredients,
            tag=tags_ids,
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
        limit = int(self.context['request'].query_params['recipes_limit'])
        recipes = recipes[:limit]
        return FavoriteRecipeSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()
