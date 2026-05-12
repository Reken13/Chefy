from django.urls import path
from . import views

urlpatterns = [
    path('', views.issue_list, name='equipment_issue_list'),
    path('nuevo/', views.issue_create, name='equipment_issue_create'),
    path('<int:pk>/editar/', views.issue_edit, name='equipment_issue_edit'),
    path('<int:pk>/resolver/', views.issue_resolve, name='equipment_issue_resolve'),
]
