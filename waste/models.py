from django.db import models
from django.conf import settings
from django.utils import timezone


class WasteLog(models.Model):
    class Reason(models.TextChoices):
        EXPIRED = 'vencido', 'Vencido'
        SPOILED = 'dañado', 'Dañado / Contaminado'
        OVERPRODUCTION = 'sobreproduccion', 'Sobreproducción'
        COOKING_ERROR = 'error_coccion', 'Error de Cocción'
        SPILLAGE = 'derrame', 'Derrame / Accidente'
        TRIMMING = 'merma', 'Merma de Limpieza'
        OTHER = 'otro', 'Otro'

    ingredient = models.ForeignKey('inventory.Ingredient', on_delete=models.CASCADE, related_name='waste_logs')
    quantity = models.DecimalField(max_digits=10, decimal_places=3)
    reason = models.CharField(max_length=20, choices=Reason.choices, default=Reason.OTHER)
    description = models.TextField(blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    reported_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Registro de desperdicio'
        verbose_name_plural = 'Registros de desperdicios'
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.ingredient.name}: {self.quantity} {self.ingredient.unit} ({self.get_reason_display()})"

    def save(self, *args, **kwargs):
        if not self.cost:
            self.cost = self.quantity * self.ingredient.cost_per_unit
        super().save(*args, **kwargs)
