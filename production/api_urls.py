from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated

from .models import ProductionTask
from .serializers import ProductionTaskSerializer


class ProductionTaskViewSet(viewsets.ModelViewSet):
    queryset = ProductionTask.objects.select_related(
        'recipe', 'assigned_to', 'created_by'
    ).all()
    serializer_class = ProductionTaskSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ['recipe__name', 'notes']
    filterset_fields = ['status', 'recipe', 'assigned_to', 'scheduled_date', 'deduct_inventory']
    ordering_fields = ['scheduled_date', 'status', 'created_at', 'recipe__name']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'], url_path='mark_done')
    def mark_done(self, request, pk=None):
        task = self.get_object()
        if task.status == ProductionTask.Status.DONE:
            return Response({'detail': 'Task is already marked as done.'}, status=status.HTTP_200_OK)
        task.mark_done()
        return Response(ProductionTaskSerializer(task).data, status=status.HTTP_200_OK)


router = DefaultRouter()
router.register(r'tasks', ProductionTaskViewSet, basename='productiontask')

urlpatterns = [
    path('', include(router.urls)),
]
