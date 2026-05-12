from django.urls import path
from core.dashboard_views import dashboard_view

urlpatterns = [
    path('', dashboard_view, name='dashboard'),
]
