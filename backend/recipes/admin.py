from django.contrib import admin

from .models import (Favorites, Follow, Ingredient, Recipe, RecipeIngredient,
                     RecipeTag, ShoppingCart, Tag)

admin.site.empty_value_display = '--Пусто--'


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient


class RecipeTagInline(admin.TabularInline):
    model = RecipeTag


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'author', 'name', 'add_to_favorites')
    search_fields = ('name',)
    list_filter = ('name', 'author', 'tags')
    fields = ('name',
              'author',
              'text',
              'image',
              'cooking_time',
              'add_to_favorites',
              )
    readonly_fields = ('add_to_favorites',)
    inlines = (RecipeIngredientInline, RecipeTagInline,)

    def add_to_favorites(self, obj):
        return obj.favorites.count()

    add_to_favorites.short_description = "В избранном, раз"


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'color', 'slug')
    list_filter = ('name',)
    search_fields = ('name',)


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'recipe_id', 'amount', 'ingredient')
    search_fields = ('ingredient__name',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(Favorites)
class FavoritesAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')
    search_fields = ('user',)
    list_filter = ('user',)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'author')
    search_fields = ('user', 'author')
    list_filter = ('user', 'author')


@admin.register(RecipeTag)
class RecipeTagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'tag', 'recipe')
    search_fields = ('tag',)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')
    search_fields = ('user',)
    list_filter = ('user',)
