from django.urls import path
from django.utils import timezone
from django.db.models import Sum, Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings


class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from inventory.models import Ingredient
        from mise_en_place.models import MiseEnPlaceTask
        from production.models import ProductionTask
        from equipment.models import EquipmentIssue
        from waste.models import WasteLog

        today = timezone.now().date()
        week_start = today - timezone.timedelta(days=7)
        expiry_threshold = today + timezone.timedelta(
            days=getattr(settings, 'EXPIRY_ALERT_DAYS', 3)
        )

        active_ingredients = Ingredient.objects.filter(is_active=True)

        low_stock_count = _count_low_stock(active_ingredients)

        expiring_count = active_ingredients.filter(
            expiry_date__isnull=False,
            expiry_date__lte=expiry_threshold,
            expiry_date__gte=today,
        ).count()

        pending_mise_count = MiseEnPlaceTask.objects.filter(
            status__in=[MiseEnPlaceTask.Status.PENDING, MiseEnPlaceTask.Status.IN_PROGRESS]
        ).count()

        pending_production_count = ProductionTask.objects.filter(
            status__in=[ProductionTask.Status.PENDING, ProductionTask.Status.IN_PROGRESS]
        ).count()

        equipment_issues_count = EquipmentIssue.objects.exclude(
            status=EquipmentIssue.Status.RESOLVED
        ).count()

        today_waste_cost = WasteLog.objects.filter(date=today).aggregate(
            total=Sum('cost')
        )['total'] or 0

        weekly_waste_cost = WasteLog.objects.filter(date__gte=week_start).aggregate(
            total=Sum('cost')
        )['total'] or 0

        total_inventory_value = sum(
            float(i.total_value) for i in active_ingredients.only(
                'current_stock', 'cost_per_unit'
            )
        )

        critical_alerts = _build_critical_alerts(
            active_ingredients, expiry_threshold, today,
            equipment_issues_count,
        )

        return Response({
            'low_stock_count': low_stock_count,
            'expiring_count': expiring_count,
            'pending_mise_count': pending_mise_count,
            'pending_production_count': pending_production_count,
            'equipment_issues_count': equipment_issues_count,
            'today_waste_cost': float(today_waste_cost),
            'weekly_waste_cost': float(weekly_waste_cost),
            'total_inventory_value': round(total_inventory_value, 2),
            'critical_alerts': critical_alerts,
        })


def _count_low_stock(active_ingredients):
    count = 0
    for ing in active_ingredients.only('current_stock', 'minimum_stock'):
        if ing.minimum_stock > 0 and ing.current_stock <= ing.minimum_stock:
            count += 1
    return count


def _build_critical_alerts(active_ingredients, expiry_threshold, today, equipment_issues_count):
    alerts = []

    low_stock_items = [
        i for i in active_ingredients.only('id', 'name', 'current_stock', 'minimum_stock')
        if i.minimum_stock > 0 and i.current_stock <= i.minimum_stock
    ]
    for ing in low_stock_items[:5]:
        alerts.append({
            'type': 'low_stock',
            'message': f'{ing.name} tiene stock bajo ({ing.current_stock} disponible)',
            'url': f'/inventario/{ing.id}/',
        })

    expiring_items = active_ingredients.filter(
        expiry_date__isnull=False,
        expiry_date__lte=expiry_threshold,
        expiry_date__gte=today,
    ).only('id', 'name', 'expiry_date')[:5]
    for ing in expiring_items:
        days = (ing.expiry_date - today).days
        alerts.append({
            'type': 'expiring',
            'message': f'{ing.name} vence en {days} día(s)',
            'url': f'/inventario/{ing.id}/',
        })

    expired_items = active_ingredients.filter(
        expiry_date__isnull=False,
        expiry_date__lt=today,
    ).only('id', 'name', 'expiry_date')[:5]
    for ing in expired_items:
        alerts.append({
            'type': 'expired',
            'message': f'{ing.name} está vencido',
            'url': f'/inventario/{ing.id}/',
        })

    if equipment_issues_count > 0:
        alerts.append({
            'type': 'equipment',
            'message': f'{equipment_issues_count} problema(s) de equipo pendiente(s)',
            'url': '/equipos/',
        })

    return alerts


class GlobalSearchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from inventory.models import Ingredient
        from recipes.models import Recipe

        q = request.query_params.get('q', '').strip()
        if not q:
            return Response({'ingredients': [], 'recipes': []})

        ingredients = Ingredient.objects.filter(
            Q(name__icontains=q) | Q(supplier__icontains=q),
            is_active=True,
        ).values('id', 'name', 'unit', 'current_stock', 'category__name')[:10]

        recipes = Recipe.objects.filter(
            Q(name__icontains=q) | Q(description__icontains=q),
            is_active=True,
        ).values('id', 'name', 'category', 'sale_price')[:10]

        return Response({
            'ingredients': list(ingredients),
            'recipes': list(recipes),
        })


urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='api-dashboard'),
    path('search/', GlobalSearchView.as_view(), name='api-search'),
]
