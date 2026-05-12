from django.urls import path
from . import views

urlpatterns = [
    path('', views.purchase_list_index, name='purchase_list_index'),
    path('nueva/', views.purchase_list_create, name='purchase_list_create'),
    path('generar/', views.purchase_list_generate, name='purchase_list_generate'),
    path('<int:pk>/', views.purchase_list_detail, name='purchase_list_detail'),
    path('item/<int:pk>/comprado/', views.mark_item_purchased, name='mark_item_purchased'),
    path('<int:pk>/todos-comprados/', views.mark_all_purchased, name='mark_all_purchased'),
]
