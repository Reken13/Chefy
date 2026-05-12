from django import forms
from django.forms import inlineformset_factory
from .models import Recipe, RecipeIngredient


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['name', 'category', 'description', 'yield_quantity', 'yield_unit',
                  'prep_time', 'cook_time', 'steps', 'notes', 'image', 'sale_price']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Nombre de la receta'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 2}),
            'yield_quantity': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
            'yield_unit': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'porciones'}),
            'prep_time': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'minutos'}),
            'cook_time': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'minutos'}),
            'steps': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 8, 'placeholder': 'Un paso por línea...'}),
            'notes': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3}),
            'sale_price': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
        }


class RecipeIngredientForm(forms.ModelForm):
    class Meta:
        model = RecipeIngredient
        fields = ['ingredient', 'quantity', 'notes']
        widgets = {
            'ingredient': forms.Select(attrs={'class': 'form-select ingredient-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.001'}),
            'notes': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Preparación (ej: brunoise)'}),
        }


RecipeIngredientFormSet = inlineformset_factory(
    Recipe, RecipeIngredient,
    form=RecipeIngredientForm,
    extra=5,
    can_delete=True,
)
