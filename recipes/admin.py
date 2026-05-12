from django.contrib import admin
from .models import Recipe, RecipeIngredient


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 3
    raw_id_fields = ['ingredient']


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'yield_quantity', 'yield_unit', 'total_time', 'sale_price', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['name', 'description']
    inlines = [RecipeIngredientInline]
    readonly_fields = ['created_at', 'updated_at']
