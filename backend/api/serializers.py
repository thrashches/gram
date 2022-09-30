from django.db import transaction
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (Favorites, Follow, Ingredient, Recipe,
                            RecipeIngredient, ShoppingCart, Tag)
from rest_framework import serializers
from users.models import User


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = ('email',
                  'id',
                  'username',
                  'first_name',
                  'last_name',
                  'password',)


class UserListSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email',
                  'id',
                  'username',
                  'first_name',
                  'last_name',
                  'is_subscribed',)

    def get_is_subscribed(self, obj):
        if self.context['request'].auth is None:
            return False
        user = self.context['request'].user
        author = get_object_or_404(User, pk=obj.id)
        return Follow.objects.filter(user=user, author=author).exists()


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email',
                  'id',
                  'username',
                  'first_name',
                  'last_name',
                  'is_subscribed')

    def get_is_subscribed(self, obj):
        if self.context['request'].auth is None:
            return False
        user = self.context['request'].user
        author = get_object_or_404(User, pk=obj.id)
        return Follow.objects.filter(user=user, author=author).exists()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)


class RecipeIngredientsSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class BaseRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(use_url=True, max_length=None)
    tags = TagSerializer(read_only=True, many=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = RecipeIngredientsSerializer(source='recipeingredient_set',
                                              read_only=True, many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def get_is_in_list(self, model, obj):
        if self.context['request'].auth is None:
            return False
        user = self.context['request'].user
        return model.objects.filter(user=user, recipe=obj).exists()


class RecipeSerializer(BaseRecipeSerializer):

    class Meta:
        model = Recipe
        fields = ('id',
                  'tags',
                  'author',
                  'ingredients',
                  'is_favorited',
                  'is_in_shopping_cart',
                  'name',
                  'image',
                  'text',
                  'cooking_time')
        read_only_fields = ('is_favorite', 'is_shopping_cart')

    def get_is_favorited(self, obj):
        return self.get_is_in_list(Favorites, obj)

    def get_is_in_shopping_cart(self, obj):
        return self.get_is_in_list(ShoppingCart, obj)

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError(
                'Список ингредиентов не должен быть пустым')
        ingredient_list = []
        for ingredient in ingredients:
            ingredient_obj = get_object_or_404(Ingredient,
                                               id=ingredient['id'])
            if ingredient_obj in ingredient_list:
                raise serializers.ValidationError(
                    'Нельзя добавлять одинаковые ингредиенты')
            ingredient_list.append(ingredient_obj)
            if int(ingredient['amount']) <= 0:
                raise serializers.ValidationError(
                    'Единица измерения ингредиента должна быть больше 0')
        data['ingredients'] = ingredients

        tags = self.initial_data.get('tags')
        if not tags:
            raise serializers.ValidationError({
                'tags': 'Список тэгов не должен быть пустым'})
        tag_list = []
        for tag in tags:
            tag_obj = get_object_or_404(Tag, id=int(tag))
            if tag_obj in tag_list:
                raise serializers.ValidationError(
                    'Нельзя добавлять одинаковые теги')
            tag_list.append(tag_obj)
        data['tags'] = tags

        return data

    def validate_cooking_time(self, data):
        cooking_time = self.initial_data.get('cooking_time')
        if int(cooking_time) < 1:
            raise serializers.ValidationError()
        return data

    @transaction.atomic
    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        user = self.context['request'].user
        recipe = Recipe.objects.create(author=user, **validated_data)

        recipe.tags.set(tags)

        for ingredient in ingredients:
            ingredient_obj = get_object_or_404(Ingredient,
                                               id=ingredient['id'])
            RecipeIngredient.objects.get_or_create(
                recipe_id=recipe,
                ingredient=ingredient_obj,
                amount=ingredient['amount']
            )

        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance.name = validated_data.get('name')
        instance.text = validated_data.get('text')
        instance.image = validated_data.get('image')
        instance.cooking_time = validated_data.get('cooking_time')
        instance.save()

        RecipeIngredient.objects.filter(recipe=instance).delete()

        instance.tags.set(tags)

        recipe_ingredients = []
        for ingredient in ingredients:
            recipe_ingredients.append(RecipeIngredient(
                recipe=instance,
                ingredient=ingredient["id"],
                amount=ingredient["amount"],
            ))
        RecipeIngredient.objects.bulk_create(recipe_ingredients)

        return instance


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class FavoritesSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='author.id')
    email = serializers.ReadOnlyField(source='author.email')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = ('email',
                  'id',
                  'username',
                  'first_name',
                  'last_name',
                  'is_subscribed',
                  'recipes',
                  'recipes_count')

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        queryset = Recipe.objects.filter(author=obj.author)
        if limit:
            queryset = queryset[:int(limit)]
        return FavoritesSerializer(queryset, many=True).data

    def get_is_subscribed(self, obj):
        return Follow.objects.filter(user=obj.user,
                                     author=obj.author).exists()

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()
