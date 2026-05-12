from django import forms
from .models import WasteLog


class WasteLogForm(forms.ModelForm):
    class Meta:
        model = WasteLog
        fields = ['ingredient', 'quantity', 'reason', 'description', 'date']
        widgets = {
            'ingredient': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.001'}),
            'reason': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 2, 'placeholder': 'Detalles adicionales...'}),
            'date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
        }
