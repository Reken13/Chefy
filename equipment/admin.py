from django.contrib import admin
from .models import Equipment, EquipmentIssue


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'brand', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'brand', 'location']


@admin.register(EquipmentIssue)
class EquipmentIssueAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'priority', 'status', 'reported_by', 'reported_at', 'resolved_at']
    list_filter = ['status', 'priority', 'reported_at']
    search_fields = ['equipment__name', 'equipment_name', 'description']
