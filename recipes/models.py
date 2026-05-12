from django.db import models
from django.conf import settings
from decimal import Decimal


class Recipe(models.Model):
    class Category(models.TextChoices):
        APPETIZER = 'entrada', 'Entrada'
        MAIN = 'principal', 'Plato Principal'
        DESSERT = 'postre', 'Postre'
        SAUCE = 'salsa', 'Salsa'
        BASE = 'base', 'Preparación Base'
        BREAD = 'pan', 'Pan / Panadería'
        BEVERAGE = 'bebida', 'Bebida'
        OTHER = 'otro', 'Otro'

    name = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.MAIN)
    description = models.TextField(blank=True)
    yield_quantity = models.DecimalField(max_digits=10, decimal_places=3, default=1)
    yield_unit = models.CharField(max_length=50, default='porciones')
    prep_time = models.PositiveIntegerField(default=0, help_text='Minutos')
    cook_time = models.PositiveIntegerField(default=0, help_text='Minutos')
    steps = models.TextField(blank=True, help_text='Pasos separados por líneas')
    notes = models.TextField(blank=True)
    image = models.ImageField(upload_to='recipes/', null=True, blank=True)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    version = models.PositiveIntegerField(default=1)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_recipes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Receta'
        verbose_name_plural = 'Recetas'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} (v{self.version})"

    @property
    def total_cost(self):
        return sum(
            ri.total_cost for ri in self.recipe_ingredients.all()
        )

    @property
    def cost_per_portion(self):
        if self.yield_quantity <= 0:
            return Decimal('0')
        return self.total_cost / self.yield_quantity

    @property
    def food_cost_percentage(self):
        if self.sale_price <= 0:
            return 0
        return round(float(self.cost_per_portion) / float(self.sale_price) * 100, 1)

    @property
    def margin(self):
        return self.sale_price - self.cost_per_portion

    @property
    def total_time(self):
        return self.prep_time + self.cook_time

    def get_steps_list(self):
        return [s.strip() for s in self.steps.split('\n') if s.strip()]


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='recipe_ingredients')
    ingredient = models.ForeignKey('inventory.Ingredient', on_delete=models.CASCADE, related_name='used_in_recipes')
    quantity = models.DecimalField(max_digits=10, decimal_places=3)
    notes = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = 'Ingrediente de receta'
        verbose_name_plural = 'Ingredientes de receta'

    def __str__(self):
        return f"{self.recipe.name} - {self.ingredient.name}: {self.quantity}{self.ingredient.unit}"

    @property
    def total_cost(self):
        return self.quantity * self.ingredient.cost_per_unit
