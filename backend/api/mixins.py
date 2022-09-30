from django.shortcuts import get_object_or_404
from recipes.models import Recipe
from rest_framework.response import Response
from rest_framework.status import (HTTP_201_CREATED, HTTP_204_NO_CONTENT,
                                   HTTP_400_BAD_REQUEST)

from .serializers import FavoritesSerializer


class AddDelMixin:

    def create_obj(self, model, user, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        if model.objects.filter(user=user, recipe=recipe).exists():
            return Response(
                {'errors': f'{recipe.name} '
                           f'уже добавлен в список у {user.username}!'},
                status=HTTP_400_BAD_REQUEST)
        model.objects.create(user=user, recipe=recipe)
        serializer = FavoritesSerializer(recipe)
        return Response(serializer.data, status=HTTP_201_CREATED)

    def delete_obj(self, model, user, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        obj = model.objects.filter(user=user, recipe__id=pk)
        if obj.exists():
            obj.delete()
            return Response(status=HTTP_204_NO_CONTENT)
        return Response({
            'errors': f'{recipe.name} не оказалось в списке у {user.username}!'
        }, status=HTTP_400_BAD_REQUEST)
