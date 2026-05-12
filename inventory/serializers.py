from rest_framework import serializers
from .models import Category, Ingredient, InventoryMovement


class CategorySerializer(serializers.ModelSerializer):
    ingredient_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'color', 'icon', 'ingredient_count']

    def get_ingredient_count(self, obj):
        return obj.ingredients.filter(is_active=True).count()


class IngredientSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)
    is_expiring_soon = serializers.BooleanField(read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    stock_percentage = serializers.IntegerField(read_only=True)
    total_value = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    unit_display = serializers.CharField(source='get_unit_display', read_only=True)
    location_display = serializers.CharField(source='get_location_display', read_only=True)

    class Meta:
        model = Ingredient
        fields = [
            'id', 'name', 'category', 'category_name', 'unit', 'unit_display',
            'current_stock', 'minimum_stock', 'cost_per_unit', 'expiry_date',
            'location', 'location_display', 'supplier', 'notes', 'image',
            'is_active', 'is_low_stock', 'is_expiring_soon', 'is_expired',
            'stock_percentage', 'total_value', 'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']


class InventoryMovementSerializer(serializers.ModelSerializer):
    ingredient_name = serializers.CharField(source='ingredient.name', read_only=True)
    ingredient_unit = serializers.CharField(source='ingredient.unit', read_only=True)
    movement_type_display = serializers.CharField(source='get_movement_type_display', read_only=True)
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = InventoryMovement
        fields = [
            'id', 'ingredient', 'ingredient_name', 'ingredient_unit',
            'movement_type', 'movement_type_display', 'quantity',
            'previous_stock', 'new_stock', 'cost_per_unit',
            'reason', 'created_by', 'created_by_name', 'created_at',
        ]
        read_only_fields = ['previous_stock', 'new_stock', 'created_at']

    def get_created_by_name(self, obj):
        if obj.created_by:
            return obj.created_by.get_full_name() or obj.created_by.username
        return None
