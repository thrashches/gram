from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CustomUserViewSet, IngredientViewSet, RecipeViewSet,
                    TagViewSet, UserDetail)

router = DefaultRouter()

router.register('recipes', RecipeViewSet, basename='recipes')
router.register('ingredients', IngredientViewSet)
router.register('users', CustomUserViewSet)
router.register('tags', TagViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('users/<int:pk>/', UserDetail.as_view(), name='user_detail'),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
