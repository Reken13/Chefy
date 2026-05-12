from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Equipment, EquipmentIssue
from .serializers import EquipmentSerializer, EquipmentIssueSerializer


class EquipmentViewSet(viewsets.ModelViewSet):
    queryset = Equipment.objects.prefetch_related('issues').all()
    serializer_class = EquipmentSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ['name', 'location', 'brand', 'model', 'serial_number']
    filterset_fields = ['is_active', 'location']
    ordering_fields = ['name', 'location', 'brand']


class EquipmentIssueViewSet(viewsets.ModelViewSet):
    queryset = EquipmentIssue.objects.select_related(
        'equipment', 'reported_by', 'assigned_to'
    ).all()
    serializer_class = EquipmentIssueSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ['equipment__name', 'equipment_name', 'description', 'location']
    filterset_fields = ['equipment', 'priority', 'status']
    ordering_fields = ['reported_at', 'priority', 'status']

    def perform_create(self, serializer):
        serializer.save(reported_by=self.request.user)

    @action(detail=True, methods=['post'], url_path='resolve')
    def resolve(self, request, pk=None):
        issue = self.get_object()
        if issue.status == EquipmentIssue.Status.RESOLVED:
            return Response({'detail': 'Issue is already resolved.'}, status=status.HTTP_200_OK)
        notes = request.data.get('notes', '')
        issue.resolve(notes=notes)
        return Response(EquipmentIssueSerializer(issue).data, status=status.HTTP_200_OK)


router = DefaultRouter()
router.register(r'equipment', EquipmentViewSet, basename='equipment')
router.register(r'issues', EquipmentIssueViewSet, basename='equipmentissue')

urlpatterns = [
    path('', include(router.urls)),
]
