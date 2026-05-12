from rest_framework import serializers
from .models import ProductionTask


class ProductionTaskSerializer(serializers.ModelSerializer):
    recipe_name = serializers.CharField(source='recipe.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    assigned_to_name = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    estimated_cost = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = ProductionTask
        fields = [
            'id', 'recipe', 'recipe_name', 'quantity', 'unit',
            'status', 'status_display', 'assigned_to', 'assigned_to_name',
            'created_by', 'created_by_name', 'scheduled_date', 'estimated_time',
            'notes', 'deduct_inventory', 'inventory_deducted',
            'completed_at', 'created_at', 'estimated_cost',
        ]
        read_only_fields = ['inventory_deducted', 'completed_at', 'created_at']

    def get_assigned_to_name(self, obj):
        if obj.assigned_to:
            return obj.assigned_to.get_full_name() or obj.assigned_to.username
        return None

    def get_created_by_name(self, obj):
        if obj.created_by:
            return obj.created_by.get_full_name() or obj.created_by.username
        return None
