from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import WasteLog
from .serializers import WasteLogSerializer


class WasteLogViewSet(viewsets.ModelViewSet):
    queryset = WasteLog.objects.select_related('ingredient', 'reported_by').all()
    serializer_class = WasteLogSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ['ingredient__name', 'description']
    filterset_fields = ['ingredient', 'reason', 'date']
    ordering_fields = ['date', 'created_at', 'cost', 'quantity']

    def perform_create(self, serializer):
        serializer.save(reported_by=self.request.user)


router = DefaultRouter()
router.register(r'logs', WasteLogViewSet, basename='wastelog')

urlpatterns = [
    path('', include(router.urls)),
]
