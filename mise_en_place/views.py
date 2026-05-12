from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from .models import MiseEnPlaceTask
from .forms import MiseEnPlaceTaskForm


@login_required
def kanban_view(request):
    date_str = request.GET.get('date', '')
    if date_str:
        try:
            from datetime import date
            selected_date = date.fromisoformat(date_str)
        except ValueError:
            selected_date = timezone.now().date()
    else:
        selected_date = timezone.now().date()

    base_qs = MiseEnPlaceTask.objects.filter(date=selected_date).select_related('assigned_to', 'recipe')

    pending = base_qs.filter(status='pendiente').order_by('-priority', 'deadline')
    in_progress = base_qs.filter(status='en_proceso').order_by('-priority', 'deadline')
    done = base_qs.filter(status='terminado')

    context = {
        'pending': pending,
        'in_progress': in_progress,
        'done': done,
        'selected_date': selected_date,
        'today': timezone.now().date(),
    }
    return render(request, 'mise_en_place/kanban.html', context)


@login_required
def task_create(request):
    form = MiseEnPlaceTaskForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        task = form.save(commit=False)
        task.created_by = request.user
        task.save()
        messages.success(request, f'Tarea "{task.title}" creada.')
        return redirect('mise_en_place_kanban')
    return render(request, 'mise_en_place/task_form.html', {'form': form, 'title': 'Nueva Tarea'})


@login_required
def task_edit(request, pk):
    task = get_object_or_404(MiseEnPlaceTask, pk=pk)
    form = MiseEnPlaceTaskForm(request.POST or None, instance=task)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Tarea actualizada.')
        return redirect('mise_en_place_kanban')
    return render(request, 'mise_en_place/task_form.html', {'form': form, 'task': task, 'title': 'Editar Tarea'})


@login_required
def task_update_status(request, pk):
    if request.method == 'POST':
        task = get_object_or_404(MiseEnPlaceTask, pk=pk)
        new_status = request.POST.get('status')
        if new_status in ['pendiente', 'en_proceso', 'terminado']:
            task.status = new_status
            if new_status == 'terminado':
                task.completed_at = timezone.now()
            else:
                task.completed_at = None
            task.save(update_fields=['status', 'completed_at'])
            if request.htmx:
                next_status_map = {'pendiente': 'en_proceso', 'en_proceso': 'terminado'}
                next_status = next_status_map.get(new_status, '')
                next_label_map = {'en_proceso': 'Terminar', 'pendiente': 'Retomar'}
                next_icon_map = {'en_proceso': 'fa-check', 'pendiente': 'fa-undo'}
                return render(request, 'mise_en_place/_task_card.html', {
                    'task': task,
                    'next_status': next_status,
                    'next_label': next_label_map.get(next_status, ''),
                    'next_icon': next_icon_map.get(next_status, ''),
                })
            messages.success(request, 'Estado actualizado.')
    return redirect('mise_en_place_kanban')


@login_required
def task_delete(request, pk):
    task = get_object_or_404(MiseEnPlaceTask, pk=pk)
    if request.method == 'POST':
        task.delete()
        messages.success(request, 'Tarea eliminada.')
    return redirect('mise_en_place_kanban')
