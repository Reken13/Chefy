from django.db import models
from django.conf import settings
from django.utils import timezone


class ProductionTask(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pendiente', 'Pendiente'
        IN_PROGRESS = 'en_proceso', 'En Proceso'
        DONE = 'terminado', 'Terminado'
        CANCELLED = 'cancelado', 'Cancelado'

    recipe = models.ForeignKey('recipes.Recipe', on_delete=models.CASCADE, related_name='production_tasks')
    quantity = models.DecimalField(max_digits=10, decimal_places=3)
    unit = models.CharField(max_length=50, default='porciones')
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='production_tasks')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_production_tasks')
    scheduled_date = models.DateField(default=timezone.now)
    estimated_time = models.PositiveIntegerField(default=0, help_text='Minutos')
    notes = models.TextField(blank=True)
    deduct_inventory = models.BooleanField(default=True)
    inventory_deducted = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Tarea de producción'
        verbose_name_plural = 'Tareas de producción'
        ordering = ['-scheduled_date', 'status']

    def __str__(self):
        return f"{self.recipe.name} x{self.quantity} - {self.get_status_display()}"

    @property
    def estimated_cost(self):
        return self.recipe.cost_per_portion * self.quantity

    def mark_done(self):
        self.status = self.Status.DONE
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'completed_at'])
