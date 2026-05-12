from django.db import models
from django.conf import settings
from django.utils import timezone


class PurchaseList(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'borrador', 'Borrador'
        PENDING = 'pendiente', 'Pendiente'
        ORDERED = 'pedido', 'Pedido Realizado'
        RECEIVED = 'recibido', 'Recibido'

    name = models.CharField(max_length=200)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.DRAFT)
    notes = models.TextField(blank=True)
    expected_delivery = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Lista de compras'
        verbose_name_plural = 'Listas de compras'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"

    @property
    def total_estimated_cost(self):
        return sum(item.estimated_cost for item in self.items.all())

    @property
    def items_count(self):
        return self.items.count()

    @property
    def pending_items(self):
        return self.items.filter(is_purchased=False).count()


class PurchaseItem(models.Model):
    purchase_list = models.ForeignKey(PurchaseList, on_delete=models.CASCADE, related_name='items')
    ingredient = models.ForeignKey('inventory.Ingredient', on_delete=models.CASCADE)
    quantity_needed = models.DecimalField(max_digits=10, decimal_places=3)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    supplier = models.CharField(max_length=200, blank=True)
    notes = models.CharField(max_length=300, blank=True)
    is_purchased = models.BooleanField(default=False)
    purchased_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Ítem de compra'
        verbose_name_plural = 'Ítems de compra'

    def __str__(self):
        return f"{self.ingredient.name}: {self.quantity_needed} {self.ingredient.unit}"

    @property
    def estimated_cost(self):
        price = self.unit_price or self.ingredient.cost_per_unit
        return self.quantity_needed * price

    def mark_purchased(self):
        self.is_purchased = True
        self.purchased_at = timezone.now()
        self.save(update_fields=['is_purchased', 'purchased_at'])
