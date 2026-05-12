from django.db import models
from django.conf import settings
from django.utils import timezone


class MiseEnPlaceTask(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pendiente', 'Pendiente'
        IN_PROGRESS = 'en_proceso', 'En Proceso'
        DONE = 'terminado', 'Terminado'

    class Priority(models.TextChoices):
        LOW = 'baja', 'Baja'
        MEDIUM = 'media', 'Media'
        HIGH = 'alta', 'Alta'
        CRITICAL = 'critica', 'Crítica'

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    recipe = models.ForeignKey('recipes.Recipe', on_delete=models.SET_NULL, null=True, blank=True, related_name='mise_en_place_tasks')
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_tasks')
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.MEDIUM)
    deadline = models.DateTimeField(null=True, blank=True)
    quantity = models.CharField(max_length=100, blank=True, help_text='Ej: 5kg, 20 porciones')
    notes = models.TextField(blank=True)
    date = models.DateField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Tarea de Mise en Place'
        verbose_name_plural = 'Tareas de Mise en Place'
        ordering = ['-priority', 'deadline']

    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"

    @property
    def is_overdue(self):
        if not self.deadline or self.status == self.Status.DONE:
            return False
        return timezone.now() > self.deadline

    def mark_done(self):
        self.status = self.Status.DONE
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'completed_at'])
