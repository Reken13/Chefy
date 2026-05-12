from django.urls import path
from . import views

urlpatterns = [
    path('', views.recipe_list, name='recipe_list'),
    path('nueva/', views.recipe_create, name='recipe_create'),
    path('<int:pk>/', views.recipe_detail, name='recipe_detail'),
    path('<int:pk>/editar/', views.recipe_edit, name='recipe_edit'),
]
