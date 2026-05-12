from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from .models import Ingredient, Category, InventoryMovement
from .forms import IngredientForm, InventoryMovementForm
from .parsers import parse_quick_add, parse_bulk_text
from .kitchen_templates import KITCHEN_TEMPLATES, RESTAURANT_TYPES


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

@login_required
@require_POST
def quick_stock_adjust(request, pk):
    """HTMX quick +/- stock adjustment — returns refreshed ingredient card."""
    ingredient = get_object_or_404(Ingredient, pk=pk)
    try:
        delta = float(request.POST.get('delta', 0))
    except (ValueError, TypeError):
        delta = 0

    if delta != 0:
        previous = ingredient.current_stock
        movement_type = (InventoryMovement.MovementType.ENTRY if delta > 0
                         else InventoryMovement.MovementType.EXIT)
        ingredient.current_stock = max(0, float(ingredient.current_stock) + delta)
        ingredient.save(update_fields=['current_stock'])
        InventoryMovement.objects.create(
            ingredient=ingredient,
            movement_type=movement_type,
            quantity=abs(delta),
            previous_stock=previous,
            new_stock=ingredient.current_stock,
            cost_per_unit=ingredient.cost_per_unit,
            reason='Ajuste rápido',
            created_by=request.user,
        )

    return render(request, 'inventory/_ingredient_card.html', {'item': ingredient})


@login_required
def quick_add_view(request):
    """Parse natural language input and create ingredient."""
    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        parsed = parse_quick_add(text)

        if parsed['valid'] and parsed['name']:
            # Find or create category
            category = None
            cat_name = parsed.get('suggested_category', '')
            if cat_name:
                category, _ = Category.objects.get_or_create(name=cat_name, defaults={'color': '#6366f1'})

            ingredient, created = Ingredient.objects.get_or_create(
                name__iexact=parsed['name'],
                defaults={
                    'name': parsed['name'],
                    'unit': parsed['unit'],
                    'current_stock': parsed['quantity'],
                    'location': parsed.get('suggested_location', 'almacen'),
                    'category': category,
                }
            )
            if not created:
                ingredient.current_stock += parsed['quantity']
                ingredient.save(update_fields=['current_stock'])
                action = 'actualizado'
            else:
                action = 'creado'

            if request.htmx:
                return render(request, 'inventory/_quick_add_result.html', {
                    'ingredient': ingredient,
                    'created': created,
                    'action': action,
                    'parsed': parsed,
                })
            messages.success(request, f'"{ingredient.name}" {action} ({ingredient.current_stock} {ingredient.unit})')
            return redirect('ingredient_list')

        if request.htmx:
            return render(request, 'inventory/_quick_add_result.html', {
                'error': 'No pude entender la entrada. Intenta: "Tomate 5kg"',
                'raw': text,
            })
        messages.error(request, 'No pude entender la entrada. Intenta: "Tomate 5kg"')
        return redirect('ingredient_list')

    return render(request, 'inventory/quick_add.html')


@login_required
def autocomplete_view(request):
    """Return ingredient name suggestions for autocomplete."""
    q = request.GET.get('q', '').strip()
    results = []
    if len(q) >= 1:
        matches = Ingredient.objects.filter(name__icontains=q, is_active=True).values('name', 'unit')[:8]
        results = list(matches)
    if request.htmx:
        return render(request, 'inventory/_autocomplete.html', {'results': results, 'q': q})
    return JsonResponse({'results': results})


@login_required
def bulk_import_view(request):
    """Import multiple ingredients from CSV text or file."""
    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        parsed_items = parse_bulk_text(text)

        if not parsed_items:
            messages.error(request, 'No se encontraron ingredientes válidos.')
            return render(request, 'inventory/bulk_import.html', {'items': [], 'text': text})

        # Preview mode
        if request.POST.get('action') == 'preview':
            return render(request, 'inventory/bulk_import.html', {
                'items': parsed_items,
                'text': text,
                'preview': True,
            })

        # Import mode
        created_count = 0
        updated_count = 0
        for item in parsed_items:
            if not item.get('valid') or not item.get('name'):
                continue
            category = None
            cat_name = item.get('suggested_category', '')
            if cat_name:
                category, _ = Category.objects.get_or_create(name=cat_name, defaults={'color': '#6366f1'})

            ingredient, created = Ingredient.objects.get_or_create(
                name__iexact=item['name'],
                defaults={
                    'name': item['name'],
                    'unit': item['unit'],
                    'current_stock': item['quantity'],
                    'location': item.get('suggested_location', 'almacen'),
                    'category': category,
                }
            )
            if created:
                created_count += 1
            else:
                if item['quantity'] > 0:
                    ingredient.current_stock += item['quantity']
                    ingredient.save(update_fields=['current_stock'])
                updated_count += 1

        messages.success(request, f'Importación completa: {created_count} creados, {updated_count} actualizados.')
        return redirect('ingredient_list')

    return render(request, 'inventory/bulk_import.html')


@login_required
def load_template_view(request):
    """Load a kitchen template (categories + ingredients)."""
    if request.method == 'POST':
        template_key = request.POST.get('template')
        template = KITCHEN_TEMPLATES.get(template_key)
        if not template:
            messages.error(request, 'Template no encontrado.')
            return redirect('ingredient_list')

        # Create categories
        cat_map = {}
        for cat_data in template.get('categories', []):
            cat, _ = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'color': cat_data['color'], 'icon': cat_data.get('icon', 'box')}
            )
            cat_map[cat_data['name']] = cat

        # Create ingredients
        created = 0
        for ing_data in template.get('ingredients', []):
            cat = cat_map.get(ing_data.get('category', ''))
            _, was_created = Ingredient.objects.get_or_create(
                name__iexact=ing_data['name'],
                defaults={
                    'name': ing_data['name'],
                    'unit': ing_data['unit'],
                    'location': ing_data.get('location', 'almacen'),
                    'minimum_stock': ing_data.get('min_stock', 0),
                    'category': cat,
                }
            )
            if was_created:
                created += 1

        messages.success(request, f'Template "{template["label"]}" cargado: {created} ingredientes creados.')
        return redirect('ingredient_list')

    # GET: show template picker
    templates_list = [
        {'key': k, 'label': v['label'], 'count': len(v['ingredients'])}
        for k, v in KITCHEN_TEMPLATES.items()
    ]
    return render(request, 'inventory/template_picker.html', {'templates': templates_list, 'restaurant_types': RESTAURANT_TYPES})
