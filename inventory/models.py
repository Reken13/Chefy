from django.db import models
from django.conf import settings
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default='#6366f1')
    icon = models.CharField(max_length=50, default='box')

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['name']

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    class Unit(models.TextChoices):
        KG = 'kg', 'Kilogramos'
        GRAMS = 'g', 'Gramos'
        LITERS = 'l', 'Litros'
        ML = 'ml', 'Mililitros'
        UNITS = 'und', 'Unidades'
        BOXES = 'caja', 'Cajas'
        PORTIONS = 'por', 'Porciones'

    class Location(models.TextChoices):
        FRIDGE = 'nevera', 'Nevera'
        FREEZER = 'freezer', 'Freezer'
        DRY_STORAGE = 'almacen', 'Almacén Seco'
        BAR = 'bar', 'Bar'
        OTHER = 'otro', 'Otro'

    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='ingredients')
    unit = models.CharField(max_length=10, choices=Unit.choices, default=Unit.UNITS)
    current_stock = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    minimum_stock = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    cost_per_unit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    expiry_date = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=20, choices=Location.choices, default=Location.DRY_STORAGE)
    supplier = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)
    image = models.ImageField(upload_to='ingredients/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Ingrediente'
        verbose_name_plural = 'Ingredientes'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.current_stock} {self.unit})"

    @property
    def is_low_stock(self):
        if self.minimum_stock <= 0:
            return False
        return self.current_stock <= self.minimum_stock

    @property
    def is_expiring_soon(self):
        if not self.expiry_date:
            return False
        days_until_expiry = (self.expiry_date - timezone.now().date()).days
        return 0 <= days_until_expiry <= getattr(settings, 'EXPIRY_ALERT_DAYS', 3)

    @property
    def is_expired(self):
        if not self.expiry_date:
            return False
        return self.expiry_date < timezone.now().date()

    @property
    def stock_percentage(self):
        if self.minimum_stock <= 0:
            return 100
        return min(int((float(self.current_stock) / float(self.minimum_stock)) * 100), 100)

    @property
    def total_value(self):
        return self.current_stock * self.cost_per_unit


class InventoryMovement(models.Model):
    class MovementType(models.TextChoices):
        ENTRY = 'entrada', 'Entrada'
        EXIT = 'salida', 'Salida'
        ADJUSTMENT = 'ajuste', 'Ajuste'
        WASTE = 'desperdicio', 'Desperdicio'
        PRODUCTION = 'produccion', 'Producción'

    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name='movements')
    movement_type = models.CharField(max_length=15, choices=MovementType.choices)
    quantity = models.DecimalField(max_digits=10, decimal_places=3)
    previous_stock = models.DecimalField(max_digits=10, decimal_places=3)
    new_stock = models.DecimalField(max_digits=10, decimal_places=3)
    cost_per_unit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    reason = models.CharField(max_length=300, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Movimiento de inventario'
        verbose_name_plural = 'Movimientos de inventario'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_movement_type_display()} - {self.ingredient.name}: {self.quantity}"
