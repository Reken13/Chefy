from django import forms
from django.forms import inlineformset_factory
from .models import PurchaseList, PurchaseItem


class PurchaseListForm(forms.ModelForm):
    class Meta:
        model = PurchaseList
        fields = ['name', 'status', 'notes', 'expected_delivery']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 2}),
            'expected_delivery': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
        }


class PurchaseItemForm(forms.ModelForm):
    class Meta:
        model = PurchaseItem
        fields = ['ingredient', 'quantity_needed', 'unit_price', 'supplier', 'notes']
        widgets = {
            'ingredient': forms.Select(attrs={'class': 'form-select'}),
            'quantity_needed': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.001'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
            'supplier': forms.TextInput(attrs={'class': 'form-input'}),
            'notes': forms.TextInput(attrs={'class': 'form-input'}),
        }


PurchaseItemFormSet = inlineformset_factory(
    PurchaseList, PurchaseItem,
    form=PurchaseItemForm,
    extra=3,
    can_delete=True,
)
