from rest_framework import serializers
from .models import PurchaseList, PurchaseItem


class PurchaseItemSerializer(serializers.ModelSerializer):
    ingredient_name = serializers.CharField(source='ingredient.name', read_only=True)
    ingredient_unit = serializers.CharField(source='ingredient.unit', read_only=True)
    estimated_cost = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = PurchaseItem
        fields = [
            'id', 'purchase_list', 'ingredient', 'ingredient_name', 'ingredient_unit',
            'quantity_needed', 'unit_price', 'supplier', 'notes',
            'is_purchased', 'purchased_at', 'estimated_cost',
        ]
        read_only_fields = ['purchased_at']


class PurchaseListSerializer(serializers.ModelSerializer):
    items = PurchaseItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    total_estimated_cost = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    items_count = serializers.IntegerField(read_only=True)
    pending_items = serializers.IntegerField(read_only=True)
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseList
        fields = [
            'id', 'name', 'status', 'status_display', 'notes',
            'expected_delivery', 'created_by', 'created_by_name',
            'created_at', 'updated_at', 'items', 'total_estimated_cost',
            'items_count', 'pending_items',
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_created_by_name(self, obj):
        if obj.created_by:
            return obj.created_by.get_full_name() or obj.created_by.username
        return None
