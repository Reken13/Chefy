from django import forms
from .models import EquipmentIssue


class EquipmentIssueForm(forms.ModelForm):
    class Meta:
        model = EquipmentIssue
        fields = ['equipment', 'equipment_name', 'description', 'priority', 'status', 'location', 'image', 'assigned_to']
        widgets = {
            'equipment': forms.Select(attrs={'class': 'form-select'}),
            'equipment_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Nombre si no está en la lista'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3, 'placeholder': 'Describe el problema...'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'location': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ubicación del equipo'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
        }
