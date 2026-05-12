from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'get_full_name', 'email', 'role', 'is_active']
    list_filter = ['role', 'is_active', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        ('Perfil', {'fields': ('role', 'phone', 'avatar', 'dark_mode', 'restaurant_name')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Perfil', {'fields': ('role', 'phone', 'restaurant_name')}),
    )
