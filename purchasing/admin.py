from django.contrib import admin
from .models import PurchaseList, PurchaseItem


class PurchaseItemInline(admin.TabularInline):
    model = PurchaseItem
    extra = 2
    raw_id_fields = ['ingredient']


@admin.register(PurchaseList)
class PurchaseListAdmin(admin.ModelAdmin):
    list_display = ['name', 'status', 'items_count', 'total_estimated_cost', 'created_at']
    list_filter = ['status']
    search_fields = ['name']
    inlines = [PurchaseItemInline]


@admin.register(PurchaseItem)
class PurchaseItemAdmin(admin.ModelAdmin):
    list_display = ['ingredient', 'purchase_list', 'quantity_needed', 'unit_price', 'is_purchased']
    list_filter = ['is_purchased', 'purchase_list__status']
