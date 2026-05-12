from django.urls import path
from . import views

urlpatterns = [
    path('', views.ingredient_list, name='ingredient_list'),
    path('nuevo/', views.ingredient_create, name='ingredient_create'),
    path('<int:pk>/', views.ingredient_detail, name='ingredient_detail'),
    path('<int:pk>/editar/', views.ingredient_edit, name='ingredient_edit'),
    path('<int:pk>/ajustar/', views.adjust_stock, name='adjust_stock'),
    # Quick add + onboarding features
    path('<int:pk>/quick-adjust/', views.quick_stock_adjust, name='inventory_quick_adjust'),
    path('quick-add/', views.quick_add_view, name='inventory_quick_add'),
    path('autocomplete/', views.autocomplete_view, name='inventory_autocomplete'),
    path('importar/', views.bulk_import_view, name='inventory_bulk_import'),
    path('plantillas/', views.load_template_view, name='inventory_load_template'),
]
