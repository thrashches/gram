from django.db.models import Sum
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.serializers import SetPasswordSerializer
from recipes.models import (Favorites, Follow, Ingredient, Recipe,
                            RecipeIngredient, ShoppingCart, Tag)
from rest_framework import generics, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import (HTTP_201_CREATED, HTTP_204_NO_CONTENT,
                                   HTTP_400_BAD_REQUEST)
from users.models import User

from .filters import IngredientSearchFilter, RecipeFilter
from .mixins import AddDelMixin
from .pagination import CustomListPagination
from .permissions import AuthorOrReadOnly
from .serializers import (CustomUserCreateSerializer, CustomUserSerializer,
                          FollowSerializer, IngredientSerializer,
                          RecipeSerializer, TagSerializer)


class BaseRecipeViewSet(viewsets.ModelViewSet, AddDelMixin):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = CustomListPagination
    permission_classes = (AuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def add_del_obj(self, model, request, pk=None):
        if request.method == 'POST':
            return self.create_obj(model, request.user, pk)
        elif request.method == 'DELETE':
            return self.delete_obj(model, request.user, pk)
        return None


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)


class RecipeViewSet(BaseRecipeViewSet):

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, pk=None):
        return self.add_del_obj(Favorites, request, pk)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        return self.add_del_obj(ShoppingCart, request, pk)

    @action(
        detail=False, url_path='download_shopping_cart',
        permission_classes=[permissions.IsAuthenticated])
    def download_shopping_cart(self, request):
        user = request.user
        ingredients = RecipeIngredient.objects.filter(
            recipe_id__cart_recipe__user=user).values_list(
            'ingredient__name',
            'ingredient__measurement_unit').annotate(Sum('amount'))
        shopping_cart = 'Ваш список покупок:\n\n'
        for ingredient in ingredients:
            shopping_cart += (
                f'{ingredient[0].capitalize()}'
                f' - {ingredient[2]} {ingredient[1]}\n'
            )
        filename = "shopping_cart.txt"
        response = HttpResponse(shopping_cart, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    pagination_class = CustomListPagination
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CustomUserCreateSerializer
        return CustomUserSerializer

    @action(detail=False, permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        user = request.user
        serializer = CustomUserSerializer(user, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def subscribe(self, request, pk):
        if request.method == 'POST':
            author = get_object_or_404(User, id=pk)
            if Follow.objects.filter(
                    user=request.user, author=author
            ).exists():
                return Response(
                    {'errors': f'{request.user.username} '
                               f'уже подписан на {author.username}'},
                    status=HTTP_400_BAD_REQUEST
                )
            if request.user == author:
                return Response(
                    {'errors': 'Нельзя подписаться на самого себя'},
                    status=HTTP_400_BAD_REQUEST
                )
            follow = Follow.objects.create(user=request.user, author=author)
            serializer = FollowSerializer(follow,
                                          context={'request': request})
            return Response(serializer.data, status=HTTP_201_CREATED)

        if request.method == 'DELETE':
            author = get_object_or_404(User, id=pk)
            obj = Follow.objects.filter(user=request.user, author__id=pk)
            if obj.exists():
                obj.delete()
                return Response(status=HTTP_204_NO_CONTENT)
            return Response(
                {'errors': f'{request.user.username} '
                           f'не подписан на {author.username}'},
                status=HTTP_400_BAD_REQUEST
            )
        return None

    @action(detail=False, methods=["post"],
            permission_classes=[permissions.IsAuthenticated], )
    def set_password(self, request):
        serializer = SetPasswordSerializer(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)

        self.request.user.set_password(serializer.data["new_password"])
        self.request.user.save()

        return Response(status=HTTP_204_NO_CONTENT)

    @action(detail=False, url_path='subscriptions', url_name='subscriptions',
            permission_classes=[permissions.IsAuthenticated],
            serializer_class=FollowSerializer)
    def subscriptions(self, request):
        user = request.user
        queryset = Follow.objects.filter(user=user)
        pages = self.paginate_queryset(queryset)
        serializer = FollowSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permissions_classes = [permissions.IsAuthenticated]


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [IngredientSearchFilter]
    search_fields = ['^name']
