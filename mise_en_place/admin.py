from django.contrib import admin
from .models import MiseEnPlaceTask


@admin.register(MiseEnPlaceTask)
class MiseEnPlaceTaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'priority', 'assigned_to', 'date', 'deadline', 'is_overdue']
    list_filter = ['status', 'priority', 'date']
    search_fields = ['title', 'description']
    list_editable = ['status', 'priority']
    raw_id_fields = ['assigned_to', 'created_by', 'recipe']
