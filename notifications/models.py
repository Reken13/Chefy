from django.db import models
from django.conf import settings


class Notification(models.Model):
    class NotificationType(models.TextChoices):
        LOW_STOCK = 'stock_bajo', 'Stock Bajo'
        EXPIRING = 'por_vencer', 'Próximo a Vencer'
        EXPIRED = 'vencido', 'Vencido'
        TASK_OVERDUE = 'tarea_atrasada', 'Tarea Atrasada'
        EQUIPMENT_ISSUE = 'equipo_dañado', 'Equipo Dañado'
        PURCHASE_URGENT = 'compra_urgente', 'Compra Urgente'
        GENERAL = 'general', 'General'

    class Priority(models.TextChoices):
        INFO = 'info', 'Información'
        WARNING = 'advertencia', 'Advertencia'
        CRITICAL = 'critica', 'Crítica'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NotificationType.choices, default=NotificationType.GENERAL)
    priority = models.CharField(max_length=15, choices=Priority.choices, default=Priority.INFO)
    title = models.CharField(max_length=200)
    message = models.TextField()
    url = models.CharField(max_length=300, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_notification_type_display()} - {self.title}"

    def mark_read(self):
        self.is_read = True
        self.save(update_fields=['is_read'])
