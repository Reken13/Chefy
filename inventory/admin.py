from django.contrib import admin
from .models import Category, Ingredient, InventoryMovement


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'icon']
    search_fields = ['name']


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'current_stock', 'minimum_stock', 'unit', 'location', 'cost_per_unit', 'is_active']
    list_filter = ['category', 'location', 'unit', 'is_active']
    search_fields = ['name', 'supplier']
    list_editable = ['current_stock', 'is_active']


@admin.register(InventoryMovement)
class InventoryMovementAdmin(admin.ModelAdmin):
    list_display = ['ingredient', 'movement_type', 'quantity', 'previous_stock', 'new_stock', 'created_by', 'created_at']
    list_filter = ['movement_type', 'created_at']
    search_fields = ['ingredient__name', 'reason']
    readonly_fields = ['created_at']
