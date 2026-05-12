from django.contrib import admin
from .models import ProductionTask


@admin.register(ProductionTask)
class ProductionTaskAdmin(admin.ModelAdmin):
    list_display = ['recipe', 'quantity', 'unit', 'status', 'assigned_to', 'scheduled_date', 'estimated_time']
    list_filter = ['status', 'scheduled_date']
    search_fields = ['recipe__name', 'notes']
    list_editable = ['status']
    raw_id_fields = ['recipe', 'assigned_to']
