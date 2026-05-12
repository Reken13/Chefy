from django import forms
from .models import Ingredient, Category, InventoryMovement


class IngredientForm(forms.ModelForm):
    class Meta:
        model = Ingredient
        fields = ['name', 'category', 'unit', 'current_stock', 'minimum_stock',
                  'cost_per_unit', 'expiry_date', 'location', 'supplier', 'notes', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Nombre del ingrediente'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'unit': forms.Select(attrs={'class': 'form-select'}),
            'current_stock': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.001'}),
            'minimum_stock': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.001'}),
            'cost_per_unit': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
            'expiry_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'location': forms.Select(attrs={'class': 'form-select'}),
            'supplier': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Proveedor'}),
            'notes': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3}),
        }


class InventoryMovementForm(forms.Form):
    quantity = forms.DecimalField(
        max_digits=10, decimal_places=3, min_value=0.001,
        widget=forms.NumberInput(attrs={'class': 'form-input', 'step': '0.001', 'placeholder': 'Cantidad'})
    )
    movement_type = forms.ChoiceField(
        choices=InventoryMovement.MovementType.choices,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    reason = forms.CharField(
        required=False, max_length=300,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Motivo (opcional)'})
    )
