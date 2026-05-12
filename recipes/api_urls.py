from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Recipe, RecipeIngredient
from .serializers import RecipeSerializer, RecipeIngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.prefetch_related(
        'recipe_ingredients__ingredient'
    ).select_related('created_by').all()
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ['name', 'description', 'notes']
    filterset_fields = ['category', 'is_active']
    ordering_fields = ['name', 'sale_price', 'created_at', 'updated_at']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class RecipeIngredientViewSet(viewsets.ModelViewSet):
    queryset = RecipeIngredient.objects.select_related('recipe', 'ingredient').all()
    serializer_class = RecipeIngredientSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ['ingredient__name', 'recipe__name']
    filterset_fields = ['recipe', 'ingredient']
    ordering_fields = ['recipe', 'ingredient']


router = DefaultRouter()
router.register(r'recipes', RecipeViewSet, basename='recipe')
router.register(r'recipe-ingredients', RecipeIngredientViewSet, basename='recipeingredient')

urlpatterns = [
    path('', include(router.urls)),
]
