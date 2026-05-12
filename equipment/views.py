from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import EquipmentIssue, Equipment
from .forms import EquipmentIssueForm


@login_required
def issue_list(request):
    status = request.GET.get('status', '')
    priority = request.GET.get('priority', '')

    issues = EquipmentIssue.objects.select_related('equipment', 'reported_by', 'assigned_to').order_by('-reported_at')
    if status:
        issues = issues.filter(status=status)
    if priority:
        issues = issues.filter(priority=priority)

    context = {
        'issues': issues,
        'statuses': EquipmentIssue.Status.choices,
        'priorities': EquipmentIssue.Priority.choices,
        'selected_status': status,
        'selected_priority': priority,
        'active_count': EquipmentIssue.objects.filter(status__in=['pendiente', 'en_reparacion']).count(),
    }
    return render(request, 'equipment/issue_list.html', context)


@login_required
def issue_create(request):
    form = EquipmentIssueForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        issue = form.save(commit=False)
        issue.reported_by = request.user
        issue.save()
        messages.success(request, 'Problema de equipo reportado.')
        return redirect('equipment_issue_list')
    return render(request, 'equipment/issue_form.html', {'form': form, 'title': 'Reportar Problema'})


@login_required
def issue_edit(request, pk):
    issue = get_object_or_404(EquipmentIssue, pk=pk)
    form = EquipmentIssueForm(request.POST or None, request.FILES or None, instance=issue)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Problema actualizado.')
        return redirect('equipment_issue_list')
    return render(request, 'equipment/issue_form.html', {'form': form, 'issue': issue, 'title': 'Editar Problema'})


@login_required
def issue_resolve(request, pk):
    issue = get_object_or_404(EquipmentIssue, pk=pk)
    if request.method == 'POST':
        notes = request.POST.get('notes', '')
        issue.resolve(notes=notes)
        messages.success(request, f'Equipo "{issue.display_name}" marcado como resuelto.')
    return redirect('equipment_issue_list')
