from rest_framework import serializers
from .models import Equipment, EquipmentIssue


class EquipmentSerializer(serializers.ModelSerializer):
    open_issues_count = serializers.SerializerMethodField()

    class Meta:
        model = Equipment
        fields = [
            'id', 'name', 'location', 'brand', 'model',
            'serial_number', 'notes', 'is_active', 'open_issues_count',
        ]

    def get_open_issues_count(self, obj):
        return obj.issues.exclude(status=EquipmentIssue.Status.RESOLVED).count()


class EquipmentIssueSerializer(serializers.ModelSerializer):
    equipment_display_name = serializers.CharField(source='display_name', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    reported_by_name = serializers.SerializerMethodField()
    assigned_to_name = serializers.SerializerMethodField()

    class Meta:
        model = EquipmentIssue
        fields = [
            'id', 'equipment', 'equipment_name', 'equipment_display_name',
            'description', 'priority', 'priority_display', 'status', 'status_display',
            'location', 'image', 'reported_by', 'reported_by_name',
            'assigned_to', 'assigned_to_name', 'reported_at',
            'resolved_at', 'resolution_notes',
        ]
        read_only_fields = ['reported_at', 'resolved_at']

    def get_reported_by_name(self, obj):
        if obj.reported_by:
            return obj.reported_by.get_full_name() or obj.reported_by.username
        return None

    def get_assigned_to_name(self, obj):
        if obj.assigned_to:
            return obj.assigned_to.get_full_name() or obj.assigned_to.username
        return None
