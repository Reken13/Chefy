from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import ProductionTask
from .forms import ProductionTaskForm


@login_required
def production_list(request):
    date_str = request.GET.get('date', '')
    if date_str:
        try:
            from datetime import date
            selected_date = date.fromisoformat(date_str)
        except ValueError:
            selected_date = timezone.now().date()
    else:
        selected_date = timezone.now().date()

    tasks = ProductionTask.objects.filter(
        scheduled_date=selected_date
    ).select_related('recipe', 'assigned_to').order_by('status', '-recipe__name')

    context = {
        'tasks': tasks,
        'pending': tasks.filter(status='pendiente'),
        'in_progress': tasks.filter(status='en_proceso'),
        'done': tasks.filter(status='terminado'),
        'selected_date': selected_date,
        'today': timezone.now().date(),
    }
    return render(request, 'production/task_list.html', context)


@login_required
def production_create(request):
    form = ProductionTaskForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        task = form.save(commit=False)
        task.created_by = request.user
        task.save()
        messages.success(request, f'Producción de "{task.recipe.name}" programada.')
        return redirect('production_list')
    return render(request, 'production/task_form.html', {'form': form, 'title': 'Nueva Tarea de Producción'})


@login_required
def production_complete(request, pk):
    task = get_object_or_404(ProductionTask, pk=pk)
    if request.method == 'POST':
        task.mark_done()
        if task.deduct_inventory and not task.inventory_deducted:
            _deduct_recipe_inventory(task, request.user)
        messages.success(request, f'"{task.recipe.name}" marcado como terminado.')
    return redirect('production_list')


def _deduct_recipe_inventory(task, user):
    from inventory.models import InventoryMovement
    scale = float(task.quantity) / float(task.recipe.yield_quantity) if task.recipe.yield_quantity > 0 else 1
    for ri in task.recipe.recipe_ingredients.select_related('ingredient').all():
        ingredient = ri.ingredient
        needed = ri.quantity * scale
        previous = ingredient.current_stock
        ingredient.current_stock = max(0, float(ingredient.current_stock) - needed)
        ingredient.save(update_fields=['current_stock'])
        InventoryMovement.objects.create(
            ingredient=ingredient,
            movement_type=InventoryMovement.MovementType.PRODUCTION,
            quantity=needed,
            previous_stock=previous,
            new_stock=ingredient.current_stock,
            cost_per_unit=ingredient.cost_per_unit,
            reason=f'Producción: {task.recipe.name}',
            created_by=user,
        )
    task.inventory_deducted = True
    task.save(update_fields=['inventory_deducted'])
