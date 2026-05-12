from rest_framework import serializers
from .models import WasteLog


class WasteLogSerializer(serializers.ModelSerializer):
    ingredient_name = serializers.CharField(source='ingredient.name', read_only=True)
    ingredient_unit = serializers.CharField(source='ingredient.unit', read_only=True)
    reason_display = serializers.CharField(source='get_reason_display', read_only=True)
    reported_by_name = serializers.SerializerMethodField()

    class Meta:
        model = WasteLog
        fields = [
            'id', 'ingredient', 'ingredient_name', 'ingredient_unit',
            'quantity', 'reason', 'reason_display', 'description',
            'cost', 'reported_by', 'reported_by_name', 'date', 'created_at',
        ]
        read_only_fields = ['created_at']

    def get_reported_by_name(self, obj):
        if obj.reported_by:
            return obj.reported_by.get_full_name() or obj.reported_by.username
        return None
