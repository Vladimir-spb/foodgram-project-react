import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipes', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipe', to=settings.AUTH_USER_MODEL, verbose_name='Автор'),
        ),
        migrations.AddField(
            model_name='recipe',
            name='ingredients',
            field=models.ManyToManyField(related_name='recipes', through='recipes.IngredientsInRecipes', to='recipes.Ingredient'),
        ),
        migrations.AddField(
            model_name='recipe',
            name='tags',
            field=models.ManyToManyField(related_name='recipes', through='recipes.RecipesTags', to='recipes.Tag'),
        ),
        migrations.AddField(
            model_name='ingredientsinrecipes',
            name='ingredient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ingredient_in_recipe', to='recipes.ingredient'),
        ),
        migrations.AddField(
            model_name='ingredientsinrecipes',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ingredient_in_recipe', to='recipes.recipe'),
        ),
        migrations.AddField(
            model_name='favoriterecipe',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorite', to='recipes.recipe', verbose_name='Рецепт'),
        ),
        migrations.AddField(
            model_name='favoriterecipe',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorite', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
        migrations.AddConstraint(
            model_name='recipe',
            constraint=models.UniqueConstraint(fields=('author', 'name'), name='unique_author_name'),
        ),
        migrations.AddConstraint(
            model_name='ingredientsinrecipes',
            constraint=models.UniqueConstraint(fields=('ingredient', 'recipe'), name='ingredient_recipe_relations'),
        ),
        migrations.AddConstraint(
            model_name='favoriterecipe',
            constraint=models.UniqueConstraint(fields=('user', 'recipe'), name='unique_user_recipe'),
        ),
    ]
