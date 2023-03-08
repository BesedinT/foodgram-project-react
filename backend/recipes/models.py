from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from users.models import User

LENGHT_TEXT = settings.MODELS_LENGHT_TEXT


class Tag(models.Model):
    name = models.CharField(
        'Название',
        max_length=LENGHT_TEXT,
        unique=True
    )
    color = models.CharField(
        'Цвет в HEX',
        max_length=7,
        unique=True
    )
    slug = models.SlugField(
        'Уникальный слаг',
        max_length=LENGHT_TEXT,
        unique=True
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        'Название',
        max_length=LENGHT_TEXT
    )
    measurement_unit = models.CharField(
        'Единицы измерения',
        max_length=LENGHT_TEXT
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)
        constraints = [models.UniqueConstraint(fields=['name',
                                                       'measurement_unit'],
                       name='unique_unit_of_measurement')]

    def __str__(self):
        return self.name


class Recipe(models.Model):
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Список тегов',
        related_name='recipes'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Список ингредиентов',
        related_name='recipes',
        through='IngredientInRecipe'
    )
    name = models.CharField(
        'Название',
        max_length=LENGHT_TEXT
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='recipe/'
    )
    text = models.TextField(
        'Описание',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления (в минутах)',
        validators=[MinValueValidator(1,
                    message='Минимальное время приготовления 1 минута')]
    )
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name[:30]


class IngredientInRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        related_name='ingredient_list',
        on_delete=models.CASCADE)
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиенты',
        on_delete=models.CASCADE)
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[MinValueValidator(1,
                    message='Количество должно быть не меньше одного')]
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'
        ordering = ('recipe',)

    def __str__(self):
        return (f'{self.ingredient.name} - {self.amount} '
                f'{self.ingredient.measurement_unit}')


class BaseSelect(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Выбор рецепта'
        verbose_name_plural = 'Выбор рецептов'
        abstract = True
        ordering = ('user',)

    def __str__(self):
        return f'"{self.recipe}" добавил {self.user}'


class Favorite(BaseSelect):

    class Meta(BaseSelect.Meta):
        default_related_name = 'favorites'
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [models.UniqueConstraint(fields=['user', 'recipe'],
                       name='already_favourite')]

    def __str__(self):
        return f'"{self.recipe}" добавил {self.user}'


class ShoppingCart(BaseSelect):

    class Meta(BaseSelect.Meta):
        default_related_name = 'shopping_cart'
        verbose_name = 'Корзина покупок'
        verbose_name_plural = 'Корзина покупок'
        constraints = [models.UniqueConstraint(fields=['user', 'recipe'],
                       name='already_shopping_cart')]
