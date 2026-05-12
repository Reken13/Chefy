from django.urls import path
from . import views

urlpatterns = [
    path('', views.waste_list, name='waste_list'),
    path('nuevo/', views.waste_create, name='waste_create'),
]
