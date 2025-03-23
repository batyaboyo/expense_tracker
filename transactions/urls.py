# transactions/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.transaction_list, name='transaction_list'),
    path('add/', views.add_transaction, name='add_transaction'),
    path('edit/<int:pk>/', views.edit_transaction, name='edit_transaction'),
    path('delete/<int:pk>/', views.delete_transaction, name='delete_transaction'),
    path('categories/', views.manage_categories, name='manage_categories'),
    path('budgets/', views.manage_budgets, name='manage_budgets'),
    path('export/', views.export_transactions, name='export_transactions'),
]
