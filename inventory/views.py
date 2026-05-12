from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum
from django.http import JsonResponse
from .models import Ingredient, Category, InventoryMovement
from .forms import IngredientForm, InventoryMovementForm


@login_required
def ingredient_list(request):
    q = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    location = request.GET.get('location', '')
    status = request.GET.get('status', '')

    ingredients = Ingredient.objects.filter(is_active=True).select_related('category')

    if q:
        ingredients = ingredients.filter(Q(name__icontains=q) | Q(supplier__icontains=q))
    if category_id:
        ingredients = ingredients.filter(category_id=category_id)
    if location:
        ingredients = ingredients.filter(location=location)
    if status == 'bajo':
        all_ing = list(ingredients)
        ingredients = [i for i in all_ing if i.is_low_stock]
    elif status == 'venciendo':
        all_ing = list(ingredients)
        ingredients = [i for i in all_ing if i.is_expiring_soon]
    elif status == 'vencido':
        all_ing = list(ingredients)
        ingredients = [i for i in all_ing if i.is_expired]

    categories = Category.objects.all()
    total_value = sum(float(i.total_value) for i in Ingredient.objects.filter(is_active=True))

    context = {
        'ingredients': ingredients if isinstance(ingredients, list) else list(ingredients),
        'categories': categories,
        'locations': Ingredient.Location.choices,
        'total_value': total_value,
        'q': q,
        'selected_category': category_id,
        'selected_location': location,
        'selected_status': status,
    }
    return render(request, 'inventory/ingredient_list.html', context)


@login_required
def ingredient_create(request):
    form = IngredientForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        ingredient = form.save()
        messages.success(request, f'Ingrediente "{ingredient.name}" creado correctamente.')
        return redirect('ingredient_list')
    return render(request, 'inventory/ingredient_form.html', {'form': form, 'title': 'Nuevo Ingrediente'})


@login_required
def ingredient_edit(request, pk):
    ingredient = get_object_or_404(Ingredient, pk=pk)
    form = IngredientForm(request.POST or None, request.FILES or None, instance=ingredient)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Ingrediente actualizado.')
        return redirect('ingredient_list')
    return render(request, 'inventory/ingredient_form.html', {'form': form, 'ingredient': ingredient, 'title': 'Editar Ingrediente'})


@login_required
def ingredient_detail(request, pk):
    ingredient = get_object_or_404(Ingredient, pk=pk)
    movements = ingredient.movements.select_related('created_by').order_by('-created_at')[:20]
    return render(request, 'inventory/ingredient_detail.html', {'ingredient': ingredient, 'movements': movements})


@login_required
def adjust_stock(request, pk):
    ingredient = get_object_or_404(Ingredient, pk=pk)
    if request.method == 'POST':
        form = InventoryMovementForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            movement_type = form.cleaned_data['movement_type']
            reason = form.cleaned_data.get('reason', '')

            previous_stock = ingredient.current_stock
            if movement_type == InventoryMovement.MovementType.ENTRY:
                ingredient.current_stock += quantity
            elif movement_type in [InventoryMovement.MovementType.EXIT,
                                    InventoryMovement.MovementType.WASTE,
                                    InventoryMovement.MovementType.PRODUCTION]:
                ingredient.current_stock = max(0, ingredient.current_stock - quantity)
            else:
                ingredient.current_stock = quantity

            InventoryMovement.objects.create(
                ingredient=ingredient,
                movement_type=movement_type,
                quantity=quantity,
                previous_stock=previous_stock,
                new_stock=ingredient.current_stock,
                cost_per_unit=ingredient.cost_per_unit,
                reason=reason,
                created_by=request.user,
            )
            ingredient.save(update_fields=['current_stock'])
            messages.success(request, f'Stock de "{ingredient.name}" actualizado.')
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'new_stock': float(ingredient.current_stock)})
            return redirect('ingredient_list')
    else:
        form = InventoryMovementForm()
    return render(request, 'inventory/adjust_stock.html', {'form': form, 'ingredient': ingredient})
