from .models import Notification
from django.contrib.auth import get_user_model

User = get_user_model()


def notify_all_managers(notification_type, priority, title, message, url=''):
    managers = User.objects.filter(role__in=['executive_chef', 'sous_chef', 'inventory'], is_active=True)
    notifications = [
        Notification(
            user=u,
            notification_type=notification_type,
            priority=priority,
            title=title,
            message=message,
            url=url,
        )
        for u in managers
    ]
    Notification.objects.bulk_create(notifications, ignore_conflicts=True)


def check_and_create_stock_alerts():
    from inventory.models import Ingredient
    low_stock = [i for i in Ingredient.objects.filter(is_active=True) if i.is_low_stock]
    for ingredient in low_stock:
        title = f'Stock bajo: {ingredient.name}'
        message = f'{ingredient.name} tiene {ingredient.current_stock}{ingredient.unit} (mínimo: {ingredient.minimum_stock}{ingredient.unit})'
        notify_all_managers(
            notification_type=Notification.NotificationType.LOW_STOCK,
            priority=Notification.Priority.WARNING,
            title=title,
            message=message,
            url='/inventario/',
        )


def check_and_create_expiry_alerts():
    from inventory.models import Ingredient
    expiring = [i for i in Ingredient.objects.filter(is_active=True) if i.is_expiring_soon]
    for ingredient in expiring:
        title = f'Próximo a vencer: {ingredient.name}'
        message = f'{ingredient.name} vence el {ingredient.expiry_date}'
        notify_all_managers(
            notification_type=Notification.NotificationType.EXPIRING,
            priority=Notification.Priority.WARNING,
            title=title,
            message=message,
            url='/inventario/',
        )
