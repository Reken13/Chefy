from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        EXECUTIVE_CHEF = 'executive_chef', 'Chef Ejecutivo'
        SOUS_CHEF = 'sous_chef', 'Sous Chef'
        COOK = 'cook', 'Cocinero'
        INVENTORY = 'inventory', 'Inventario'

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.COOK)
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    dark_mode = models.BooleanField(default=False)
    restaurant_name = models.CharField(max_length=100, default='Mi Restaurante')

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    @property
    def is_executive_chef(self):
        return self.role == self.Role.EXECUTIVE_CHEF

    @property
    def is_sous_chef(self):
        return self.role == self.Role.SOUS_CHEF

    @property
    def can_manage(self):
        return self.role in [self.Role.EXECUTIVE_CHEF, self.Role.SOUS_CHEF]
