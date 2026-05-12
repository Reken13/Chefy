from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from .models import WasteLog
from .forms import WasteLogForm


@login_required
def waste_list(request):
    period = request.GET.get('period', '7')
    reason = request.GET.get('reason', '')

    days = int(period) if period.isdigit() else 7
    start_date = timezone.now().date() - timedelta(days=days)

    logs = WasteLog.objects.filter(date__gte=start_date).select_related('ingredient', 'reported_by').order_by('-date', '-created_at')
    if reason:
        logs = logs.filter(reason=reason)

    stats = logs.aggregate(total_cost=Sum('cost'), total_count=Count('id'))

    top_wasted = WasteLog.objects.filter(date__gte=start_date).values(
        'ingredient__name', 'ingredient__unit'
    ).annotate(
        total_qty=Sum('quantity'),
        total_cost=Sum('cost'),
        count=Count('id')
    ).order_by('-total_cost')[:10]

    context = {
        'logs': logs,
        'stats': stats,
        'top_wasted': top_wasted,
        'period': period,
        'reasons': WasteLog.Reason.choices,
        'selected_reason': reason,
    }
    return render(request, 'waste/waste_list.html', context)


@login_required
def waste_create(request):
    form = WasteLogForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        waste = form.save(commit=False)
        waste.reported_by = request.user
        waste.save()
        # Deduct from inventory
        ingredient = waste.ingredient
        from inventory.models import InventoryMovement
        previous = ingredient.current_stock
        ingredient.current_stock = max(0, float(ingredient.current_stock) - float(waste.quantity))
        ingredient.save(update_fields=['current_stock'])
        InventoryMovement.objects.create(
            ingredient=ingredient,
            movement_type=InventoryMovement.MovementType.WASTE,
            quantity=waste.quantity,
            previous_stock=previous,
            new_stock=ingredient.current_stock,
            cost_per_unit=ingredient.cost_per_unit,
            reason=f'Desperdicio: {waste.get_reason_display()}',
            created_by=request.user,
        )
        messages.success(request, 'Desperdicio registrado.')
        return redirect('waste_list')
    return render(request, 'waste/waste_form.html', {'form': form, 'title': 'Registrar Desperdicio'})
