from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Tag(models.Model):

    name = models.CharField(
        unique=True,
        max_length=200,
        verbose_name='Название тега',
        help_text='Название тега',
    )
    color = models.CharField(
        unique=True,
        blank=True,
        max_length=7,
        verbose_name='Цвет HEX',
        help_text='Выберите hex-цвет',
    )
    slug = models.SlugField(
        unique=True,
        blank=True,
        max_length=200,
        verbose_name='Идентификатор',
        help_text='Уникальный URL адрес для тега',
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name[:30]


class Ingredient(models.Model):

    name = models.CharField(
        max_length=200,
        verbose_name='Название',
        help_text='Введите название ингредиента'
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единица измерения',
        help_text='Введите единицу измерения ингредиента'
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name} - {self.measurement_unit}'


class Recipe(models.Model):

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта',
        help_text='Автор рецепта',
    )
    name = models.CharField(
        max_length=200,
        db_index=True,
        verbose_name='Название рецепта',
        help_text='Укажите название рецепта',
    )
    image = models.ImageField(
        upload_to='recipes/images',
        max_length=None,
        blank=True,
        null=True,
        verbose_name='Картинка',
        help_text='Загрузите изображение с фотографией готового блюда',
    )
    text = models.TextField(
        verbose_name='Текстовое описание',
        help_text='Напишите рецепт',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингредиенты',
        help_text='Выберите ингредиенты',
    )
    tags = models.ManyToManyField(
        Tag,
        through='RecipeTag',
        verbose_name='Тэги',
        help_text='Выберите теги',
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1, message=settings.VALIDATOR_MESSAGE)
        ],
        verbose_name='Время приготовления в минутах',
        help_text='Время приготовления в минутах'
    )
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name[:30]


class RecipeTag(models.Model):

    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        verbose_name='Тэг',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Тег рецепта'
        verbose_name_plural = 'Теги рецепта'


class RecipeIngredient(models.Model):

    recipe_id = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Название рецепта',
        help_text='Название рецепта'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
        help_text='Название ингредиента'
    )
    amount = models.PositiveSmallIntegerField(
        default=1,
        validators=[
            MinValueValidator(1, message=settings.VALIDATOR_MESSAGE)
        ],
        verbose_name='Количество ингредиентов',
        help_text='Количество ингредиентов'
    )

    class Meta:
        verbose_name = 'Рецепт и ингредиент'
        verbose_name_plural = 'Рецепт и ингредиенты'
        constraints = (
            models.UniqueConstraint(fields=('ingredient', 'recipe_id'),
                                    name='unique_ingredients_recipes'),
        )

    def __str__(self):
        return f'{self.ingredient.name} - {self.amount}'


class Favorites(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Подписчик',
        help_text='Имя подписчика'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Избранный рецепт',
        help_text='Избранный рецепт'
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        constraints = (
            models.UniqueConstraint(fields=('user', 'recipe'),
                                    name='unique_favorite'),
        )

    def __str__(self):
        return f'{self.user.username} - {self.recipe.name}'


class ShoppingCart(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='cart_user',
        verbose_name='Пользователь',
        help_text='Имя пользователя'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='cart_recipe',
        verbose_name='Рецепт',
        help_text='Рецепт в списке покупок'
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Покупка'
        verbose_name_plural = 'Покупки'
        constraints = (
            models.UniqueConstraint(fields=('user', 'recipe'),
                                    name='unique_shopping_cart'),
        )

    def __str__(self):
        return f'{self.user.username} - {self.recipe.name}'


class Follow(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
        help_text='Имя подписчика'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор рецепта',
        help_text='Имя автора рецепта'
    )

    class Meta:
        verbose_name = 'Подписки'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(fields=('user', 'author'),
                                    name='unique_follow'),
        ]

    def __str__(self):
        return f'{self.user.username} - {self.author.username}'
