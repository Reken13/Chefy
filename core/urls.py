from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('perfil/', views.profile_view, name='profile'),
    path('dark-mode/', views.toggle_dark_mode, name='toggle_dark_mode'),
    path('onboarding/', views.onboarding_view, name='onboarding'),
]
