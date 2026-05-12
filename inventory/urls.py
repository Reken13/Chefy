from django.urls import path
from . import views

urlpatterns = [
    path('', views.ingredient_list, name='ingredient_list'),
    path('nuevo/', views.ingredient_create, name='ingredient_create'),
    path('<int:pk>/', views.ingredient_detail, name='ingredient_detail'),
    path('<int:pk>/editar/', views.ingredient_edit, name='ingredient_edit'),
    path('<int:pk>/ajustar/', views.adjust_stock, name='adjust_stock'),
]
