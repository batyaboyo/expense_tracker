from django.urls import path
from . import views

urlpatterns = [
    path('', views.expense_list, name='expense_list'),
    path('expense/add/', views.add_expense, name='add_expense'),
    path('expense/<int:pk>/edit/', views.edit_expense, name='edit_expense'),
    path('expense/<int:pk>/delete/', views.delete_expense, name='delete_expense'),
    path('categories/', views.category_list, name='category_list'),
    path('category/<int:pk>/delete/', views.delete_category, name='delete_category'),
    path('summary/', views.expense_summary, name='expense_summary'),
    path('api/expense-data/', views.get_expense_data, name='get_expense_data'),
]
