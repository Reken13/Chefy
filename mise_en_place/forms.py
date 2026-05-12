from django import forms
from .models import MiseEnPlaceTask


class MiseEnPlaceTaskForm(forms.ModelForm):
    class Meta:
        model = MiseEnPlaceTask
        fields = ['title', 'description', 'recipe', 'assigned_to', 'priority', 'status',
                  'deadline', 'quantity', 'notes', 'date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Nombre de la tarea'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 2}),
            'recipe': forms.Select(attrs={'class': 'form-select'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'deadline': forms.DateTimeInput(attrs={'class': 'form-input', 'type': 'datetime-local'}),
            'quantity': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ej: 5kg, 20 porciones'}),
            'notes': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 2}),
            'date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
        }
