from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, Count, Q
from .models import User
from .forms import LoginForm, UserProfileForm, RegisterForm


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        return redirect(request.GET.get('next', 'dashboard'))
    return render(request, 'core/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def profile_view(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Perfil actualizado correctamente.')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'core/profile.html', {'form': form})


@login_required
def toggle_dark_mode(request):
    if request.method == 'POST':
        request.user.dark_mode = not request.user.dark_mode
        request.user.save(update_fields=['dark_mode'])
    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))
