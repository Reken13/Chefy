from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated

from .models import MiseEnPlaceTask
from .serializers import MiseEnPlaceTaskSerializer


class MiseEnPlaceTaskViewSet(viewsets.ModelViewSet):
    queryset = MiseEnPlaceTask.objects.select_related(
        'recipe', 'assigned_to', 'created_by'
    ).all()
    serializer_class = MiseEnPlaceTaskSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ['title', 'description', 'notes', 'quantity']
    filterset_fields = ['status', 'priority', 'recipe', 'assigned_to', 'date']
    ordering_fields = ['priority', 'deadline', 'date', 'created_at', 'status']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'], url_path='mark_done')
    def mark_done(self, request, pk=None):
        task = self.get_object()
        if task.status == MiseEnPlaceTask.Status.DONE:
            return Response({'detail': 'Task is already marked as done.'}, status=status.HTTP_200_OK)
        task.mark_done()
        return Response(MiseEnPlaceTaskSerializer(task).data, status=status.HTTP_200_OK)


router = DefaultRouter()
router.register(r'tasks', MiseEnPlaceTaskViewSet, basename='miseenplacetask')

urlpatterns = [
    path('', include(router.urls)),
]
