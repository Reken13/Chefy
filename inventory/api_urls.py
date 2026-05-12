from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Category, Ingredient, InventoryMovement
from .serializers import CategorySerializer, IngredientSerializer, InventoryMovementSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    search_fields = ['name']
    filterset_fields = ['name']
    ordering_fields = ['name']


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.select_related('category').all()
    serializer_class = IngredientSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ['name', 'supplier', 'notes']
    filterset_fields = ['category', 'unit', 'location', 'is_active']
    ordering_fields = ['name', 'current_stock', 'cost_per_unit', 'expiry_date', 'updated_at']

    @action(detail=True, methods=['post'], url_path='adjust_stock')
    def adjust_stock(self, request, pk=None):
        ingredient = self.get_object()
        quantity = request.data.get('quantity')
        movement_type = request.data.get('movement_type')
        reason = request.data.get('reason', '')

        if quantity is None or movement_type is None:
            return Response(
                {'error': 'quantity and movement_type are required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            quantity = float(quantity)
        except (TypeError, ValueError):
            return Response({'error': 'quantity must be a number.'}, status=status.HTTP_400_BAD_REQUEST)

        valid_types = [c[0] for c in InventoryMovement.MovementType.choices]
        if movement_type not in valid_types:
            return Response(
                {'error': f'movement_type must be one of: {valid_types}'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        from decimal import Decimal
        previous_stock = ingredient.current_stock

        if movement_type in (InventoryMovement.MovementType.EXIT,
                             InventoryMovement.MovementType.WASTE,
                             InventoryMovement.MovementType.PRODUCTION):
            new_stock = previous_stock - Decimal(str(quantity))
        elif movement_type == InventoryMovement.MovementType.ADJUSTMENT:
            new_stock = Decimal(str(quantity))
        else:
            new_stock = previous_stock + Decimal(str(quantity))

        if new_stock < 0:
            return Response({'error': 'Resulting stock cannot be negative.'}, status=status.HTTP_400_BAD_REQUEST)

        movement = InventoryMovement.objects.create(
            ingredient=ingredient,
            movement_type=movement_type,
            quantity=Decimal(str(quantity)),
            previous_stock=previous_stock,
            new_stock=new_stock,
            cost_per_unit=ingredient.cost_per_unit,
            reason=reason,
            created_by=request.user,
        )

        ingredient.current_stock = new_stock
        ingredient.save(update_fields=['current_stock'])

        return Response(InventoryMovementSerializer(movement).data, status=status.HTTP_201_CREATED)


class InventoryMovementViewSet(viewsets.ModelViewSet):
    queryset = InventoryMovement.objects.select_related('ingredient', 'created_by').all()
    serializer_class = InventoryMovementSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ['ingredient__name', 'reason']
    filterset_fields = ['ingredient', 'movement_type']
    ordering_fields = ['created_at', 'quantity']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'ingredients', IngredientViewSet, basename='ingredient')
router.register(r'movements', InventoryMovementViewSet, basename='inventorymovement')

urlpatterns = [
    path('', include(router.urls)),
]
