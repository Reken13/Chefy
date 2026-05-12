from django.urls import path
from . import views

urlpatterns = [
    path('', views.production_list, name='production_list'),
    path('nueva/', views.production_create, name='production_create'),
    path('<int:pk>/completar/', views.production_complete, name='production_complete'),
]
