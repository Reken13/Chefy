from rest_framework import serializers
from .models import MiseEnPlaceTask


class MiseEnPlaceTaskSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    recipe_name = serializers.CharField(source='recipe.name', read_only=True)
    assigned_to_name = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    is_overdue = serializers.BooleanField(read_only=True)

    class Meta:
        model = MiseEnPlaceTask
        fields = [
            'id', 'title', 'description', 'recipe', 'recipe_name',
            'assigned_to', 'assigned_to_name', 'created_by', 'created_by_name',
            'status', 'status_display', 'priority', 'priority_display',
            'deadline', 'quantity', 'notes', 'date',
            'completed_at', 'is_overdue', 'created_at', 'updated_at',
        ]
        read_only_fields = ['completed_at', 'created_at', 'updated_at']

    def get_assigned_to_name(self, obj):
        if obj.assigned_to:
            return obj.assigned_to.get_full_name() or obj.assigned_to.username
        return None

    def get_created_by_name(self, obj):
        if obj.created_by:
            return obj.created_by.get_full_name() or obj.created_by.username
        return None
