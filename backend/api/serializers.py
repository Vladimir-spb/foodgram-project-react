from django.db import transaction
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (FavoriteRecipe, Ingredient, IngredientsInRecipes,
                            Recipe, RecipesTags, Tag)
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
        source='ingredient'
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
    tags = TagSerializer(read_only=True,
                         many=True,
                         )
    ingredients = IngredientsInRecipesSerialize(
        many=True, source='ingredient_in_recipe'
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
        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError(
                {'error': 'Отсутствует информация об ингредиентах'}
            )
        lst_unique_ingredients = []
        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            if ingredient_id in lst_unique_ingredients:
                raise serializers.ValidationError({
                    'ingredients': 'Ингредиенты должны быть уникальными!'
                })
            lst_unique_ingredients.append(ingredient_id)
            amount = ingredient['amount']
            if int(amount) <= 0:
                raise serializers.ValidationError({
                    'amount': 'Количество ингредиента должно быть больше нуля!'
                })
        tags_ids = self.initial_data.get('tags')
        if not tags_ids:
            raise serializers.ValidationError({
                'tags': 'Нужно выбрать хотя бы один тэг!'
            })
        tags_list = []
        for tag in tags_ids:
            if tag in tags_list:
                raise serializers.ValidationError({
                    'tags': 'Тэги должны быть уникальными!'
                })
            tags_list.append(tag)
        return data

    def create_ingredient_tags_in_recipe(self, recipe, ingredients, tags_ids):
        ingredient_recipe_list = [IngredientsInRecipes(
            recipe=recipe,
            ingredient=ingredient['ingredient'],
            amount=ingredient['amount']) for ingredient in ingredients]
        IngredientsInRecipes.objects.bulk_create(ingredient_recipe_list)
        tag_list = [RecipesTags(
            recipe=recipe,
            tag=Tag.objects.get(id=tags_id)) for tags_id in tags_ids]
        RecipesTags.objects.bulk_create(tag_list)

    @transaction.atomic
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredient_in_recipe')
        tags_ids = self.initial_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        self.create_ingredient_tags_in_recipe(recipe, ingredients, tags_ids)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.ingredients.clear()
        instance.tags.clear()

        ingredients = validated_data.pop('ingredient_in_recipe')
        tags_ids = self.initial_data.pop('tags')
        self.create_ingredient_tags_in_recipe(instance, ingredients, tags_ids)
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
        return FavoriteRecipeSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()
