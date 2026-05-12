from django import forms
from .models import ProductionTask


class ProductionTaskForm(forms.ModelForm):
    class Meta:
        model = ProductionTask
        fields = ['recipe', 'quantity', 'unit', 'assigned_to', 'scheduled_date', 'estimated_time', 'notes', 'deduct_inventory']
        widgets = {
            'recipe': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
            'unit': forms.TextInput(attrs={'class': 'form-input'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
            'scheduled_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'estimated_time': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'minutos'}),
            'notes': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 2}),
            'deduct_inventory': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }
