from django.urls import path
from . import views

urlpatterns = [
    path('', views.kanban_view, name='mise_en_place_kanban'),
    path('nueva/', views.task_create, name='mise_en_place_create'),
    path('<int:pk>/editar/', views.task_edit, name='mise_en_place_edit'),
    path('<int:pk>/estado/', views.task_update_status, name='mise_en_place_status'),
    path('<int:pk>/eliminar/', views.task_delete, name='mise_en_place_delete'),
]
