from rest_framework import serializers
from .models import Recipe, RecipeIngredient


class RecipeIngredientReadSerializer(serializers.ModelSerializer):
    ingredient_name = serializers.CharField(source='ingredient.name', read_only=True)
    ingredient_unit = serializers.CharField(source='ingredient.unit', read_only=True)
    ingredient_unit_display = serializers.CharField(source='ingredient.get_unit_display', read_only=True)
    total_cost = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    current_stock = serializers.DecimalField(source='ingredient.current_stock', max_digits=10, decimal_places=3, read_only=True)

    class Meta:
        model = RecipeIngredient
        fields = [
            'id', 'ingredient', 'ingredient_name', 'ingredient_unit',
            'ingredient_unit_display', 'quantity', 'notes', 'total_cost',
            'current_stock',
        ]


class RecipeIngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeIngredient
        fields = ['id', 'recipe', 'ingredient', 'quantity', 'notes']


class RecipeSerializer(serializers.ModelSerializer):
    recipe_ingredients = RecipeIngredientReadSerializer(many=True, read_only=True)
    total_cost = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    cost_per_portion = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    food_cost_percentage = serializers.FloatField(read_only=True)
    margin = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_time = serializers.IntegerField(read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = [
            'id', 'name', 'category', 'category_display', 'description',
            'yield_quantity', 'yield_unit', 'prep_time', 'cook_time', 'total_time',
            'steps', 'notes', 'image', 'sale_price', 'is_active', 'version',
            'created_by', 'created_by_name', 'created_at', 'updated_at',
            'recipe_ingredients', 'total_cost', 'cost_per_portion',
            'food_cost_percentage', 'margin',
        ]
        read_only_fields = ['created_at', 'updated_at', 'version']

    def get_created_by_name(self, obj):
        if obj.created_by:
            return obj.created_by.get_full_name() or obj.created_by.username
        return None
