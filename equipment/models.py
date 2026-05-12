from django.db import models
from django.conf import settings
from django.utils import timezone


class Equipment(models.Model):
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200, blank=True)
    brand = models.CharField(max_length=100, blank=True)
    model = models.CharField(max_length=100, blank=True)
    serial_number = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Equipo'
        verbose_name_plural = 'Equipos'
        ordering = ['name']

    def __str__(self):
        return self.name


class EquipmentIssue(models.Model):
    class Priority(models.TextChoices):
        LOW = 'baja', 'Baja'
        MEDIUM = 'media', 'Media'
        HIGH = 'alta', 'Alta'
        CRITICAL = 'critica', 'Crítica - Fuera de servicio'

    class Status(models.TextChoices):
        PENDING = 'pendiente', 'Pendiente'
        IN_REPAIR = 'en_reparacion', 'En Reparación'
        RESOLVED = 'resuelto', 'Resuelto'

    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='issues', null=True, blank=True)
    equipment_name = models.CharField(max_length=200, help_text='Nombre si el equipo no está registrado')
    description = models.TextField()
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.MEDIUM)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    location = models.CharField(max_length=200, blank=True)
    image = models.ImageField(upload_to='equipment/', null=True, blank=True)
    reported_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='reported_issues')
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_equipment_issues')
    reported_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Problema de equipo'
        verbose_name_plural = 'Problemas de equipos'
        ordering = ['-reported_at']

    def __str__(self):
        name = self.equipment.name if self.equipment else self.equipment_name
        return f"{name} - {self.get_status_display()}"

    @property
    def display_name(self):
        return self.equipment.name if self.equipment else self.equipment_name

    def resolve(self, notes=''):
        self.status = self.Status.RESOLVED
        self.resolved_at = timezone.now()
        if notes:
            self.resolution_notes = notes
        self.save(update_fields=['status', 'resolved_at', 'resolution_notes'])
