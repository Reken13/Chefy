from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from .models import PurchaseList, PurchaseItem
from .forms import PurchaseListForm, PurchaseItemFormSet
from inventory.models import Ingredient


@login_required
def purchase_list_index(request):
    lists = PurchaseList.objects.all().order_by('-created_at')
    return render(request, 'purchasing/list_index.html', {'lists': lists})


@login_required
def purchase_list_detail(request, pk):
    purchase_list = get_object_or_404(PurchaseList, pk=pk)
    items_by_supplier = {}
    for item in purchase_list.items.select_related('ingredient').order_by('supplier', 'ingredient__name'):
        supplier = item.supplier or item.ingredient.supplier or 'Sin proveedor'
        items_by_supplier.setdefault(supplier, []).append(item)
    return render(request, 'purchasing/list_detail.html', {
        'purchase_list': purchase_list,
        'items_by_supplier': items_by_supplier,
    })


@login_required
def purchase_list_create(request):
    if request.method == 'POST':
        form = PurchaseListForm(request.POST)
        if form.is_valid():
            pl = form.save(commit=False)
            pl.created_by = request.user
            pl.save()
            messages.success(request, 'Lista de compras creada.')
            return redirect('purchase_list_detail', pk=pl.pk)
    else:
        form = PurchaseListForm()
    return render(request, 'purchasing/list_form.html', {'form': form, 'title': 'Nueva Lista de Compras'})


@login_required
def purchase_list_generate(request):
    low_stock_items = [i for i in Ingredient.objects.filter(is_active=True) if i.is_low_stock]
    if request.method == 'POST':
        pl = PurchaseList.objects.create(
            name=f"Compras automáticas - {request.POST.get('date', 'hoy')}",
            created_by=request.user,
        )
        for ingredient in low_stock_items:
            needed = max(0, float(ingredient.minimum_stock) - float(ingredient.current_stock))
            if needed > 0:
                PurchaseItem.objects.create(
                    purchase_list=pl,
                    ingredient=ingredient,
                    quantity_needed=needed,
                    supplier=ingredient.supplier,
                )
        messages.success(request, f'Lista generada con {pl.items.count()} artículos.')
        return redirect('purchase_list_detail', pk=pl.pk)
    return render(request, 'purchasing/list_generate.html', {'low_stock_items': low_stock_items})


@login_required
def mark_item_purchased(request, pk):
    item = get_object_or_404(PurchaseItem, pk=pk)
    if request.method == 'POST':
        item.mark_purchased()
        messages.success(request, f'"{item.ingredient.name}" marcado como comprado.')
    return redirect('purchase_list_detail', pk=item.purchase_list.pk)
