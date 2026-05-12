from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated

from .models import PurchaseList, PurchaseItem
from .serializers import PurchaseListSerializer, PurchaseItemSerializer


class PurchaseListViewSet(viewsets.ModelViewSet):
    queryset = PurchaseList.objects.prefetch_related(
        'items__ingredient'
    ).select_related('created_by').all()
    serializer_class = PurchaseListSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ['name', 'notes']
    filterset_fields = ['status']
    ordering_fields = ['name', 'created_at', 'expected_delivery', 'status']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class PurchaseItemViewSet(viewsets.ModelViewSet):
    queryset = PurchaseItem.objects.select_related('purchase_list', 'ingredient').all()
    serializer_class = PurchaseItemSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ['ingredient__name', 'supplier', 'notes']
    filterset_fields = ['purchase_list', 'ingredient', 'is_purchased']
    ordering_fields = ['ingredient__name', 'quantity_needed', 'is_purchased']

    @action(detail=True, methods=['post'], url_path='mark_purchased')
    def mark_purchased(self, request, pk=None):
        item = self.get_object()
        if item.is_purchased:
            return Response({'detail': 'Item is already marked as purchased.'}, status=status.HTTP_200_OK)
        item.mark_purchased()
        return Response(PurchaseItemSerializer(item).data, status=status.HTTP_200_OK)


router = DefaultRouter()
router.register(r'lists', PurchaseListViewSet, basename='purchaselist')
router.register(r'items', PurchaseItemViewSet, basename='purchaseitem')

urlpatterns = [
    path('', include(router.urls)),
]
