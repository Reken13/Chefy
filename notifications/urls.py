from django.urls import path
from . import views

urlpatterns = [
    path('', views.notification_list, name='notification_list'),
    path('<int:pk>/leer/', views.mark_read, name='notification_mark_read'),
    path('leer-todas/', views.mark_all_read, name='notification_mark_all_read'),
]
