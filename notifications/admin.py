from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'notification_type', 'priority', 'title', 'is_read', 'created_at']
    list_filter = ['notification_type', 'priority', 'is_read']
    search_fields = ['title', 'message', 'user__username']
    list_editable = ['is_read']
