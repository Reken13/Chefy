from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Sum, Count, Q
from datetime import timedelta


@login_required
def dashboard_view(request):
    from inventory.models import Ingredient
    from mise_en_place.models import MiseEnPlaceTask
    from equipment.models import EquipmentIssue
    from production.models import ProductionTask
    from waste.models import WasteLog
    from purchasing.models import PurchaseList

    today = timezone.now().date()
    week_start = today - timedelta(days=7)

    low_stock_items = [i for i in Ingredient.objects.filter(is_active=True) if i.is_low_stock]
    expiring_items = [i for i in Ingredient.objects.filter(is_active=True) if i.is_expiring_soon]
    expired_items = [i for i in Ingredient.objects.filter(is_active=True) if i.is_expired]

    pending_mise = MiseEnPlaceTask.objects.filter(
        date=today, status__in=['pendiente', 'en_proceso']
    ).order_by('-priority', 'deadline')

    in_progress_mise = MiseEnPlaceTask.objects.filter(
        date=today, status='en_proceso'
    )

    done_mise = MiseEnPlaceTask.objects.filter(date=today, status='terminado')

    active_equipment_issues = EquipmentIssue.objects.filter(
        status__in=['pendiente', 'en_reparacion']
    ).order_by('-priority')

    pending_production = ProductionTask.objects.filter(
        scheduled_date=today, status__in=['pendiente', 'en_proceso']
    ).select_related('recipe', 'assigned_to')

    today_waste = WasteLog.objects.filter(date=today).aggregate(
        total_cost=Sum('cost'), count=Count('id')
    )
    weekly_waste = WasteLog.objects.filter(date__gte=week_start).aggregate(
        total_cost=Sum('cost'), count=Count('id')
    )

    total_inventory_value = sum(
        float(i.total_value) for i in Ingredient.objects.filter(is_active=True)
    )

    recent_purchase_lists = PurchaseList.objects.filter(
        status__in=['borrador', 'pendiente']
    ).order_by('-created_at')[:3]

    overdue_tasks = [t for t in MiseEnPlaceTask.objects.filter(
        status__in=['pendiente', 'en_proceso']
    ) if t.is_overdue]

    context = {
        'low_stock_items': low_stock_items[:8],
        'low_stock_count': len(low_stock_items),
        'expiring_items': expiring_items[:5],
        'expiring_count': len(expiring_items),
        'expired_items': expired_items[:5],
        'expired_count': len(expired_items),
        'pending_mise': pending_mise,
        'in_progress_mise': in_progress_mise,
        'done_mise': done_mise,
        'mise_total': pending_mise.count() + in_progress_mise.count() + done_mise.count(),
        'active_equipment_issues': active_equipment_issues[:5],
        'equipment_issues_count': active_equipment_issues.count(),
        'pending_production': pending_production,
        'today_waste_cost': today_waste['total_cost'] or 0,
        'today_waste_count': today_waste['count'] or 0,
        'weekly_waste_cost': weekly_waste['total_cost'] or 0,
        'total_inventory_value': total_inventory_value,
        'recent_purchase_lists': recent_purchase_lists,
        'overdue_tasks': overdue_tasks,
        'today': today,
    }
    return render(request, 'core/dashboard.html', context)
