from django.contrib import admin
from .models import WasteLog


@admin.register(WasteLog)
class WasteLogAdmin(admin.ModelAdmin):
    list_display = ['ingredient', 'quantity', 'reason', 'cost', 'reported_by', 'date']
    list_filter = ['reason', 'date']
    search_fields = ['ingredient__name', 'description']
    readonly_fields = ['created_at']
