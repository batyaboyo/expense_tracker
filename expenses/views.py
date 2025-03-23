from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Sum
from django.http import JsonResponse
from .models import Expense, Category
from .forms import ExpenseForm, CategoryForm
import json
from datetime import datetime, timedelta
from collections import defaultdict

class ExpenseListView(LoginRequiredMixin, ListView):
    model = Expense
    template_name = 'expenses/expense_list.html'
    context_object_name = 'expenses'
    paginate_by = 10
    
    def get_queryset(self):
        return Expense.objects.filter(user=self.request.user)

class ExpenseDetailView(LoginRequiredMixin, DetailView):
    model = Expense
    template_name = 'expenses/expense_detail.html'
    
    def get_queryset(self):
        return Expense.objects.filter(user=self.request.user)

class ExpenseCreateView(LoginRequiredMixin, CreateView):
    model = Expense
    form_class = ExpenseForm
    template_name = 'expenses/expense_form.html'
    success_url = reverse_lazy('expense-list')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['category'].queryset = Category.objects.filter(user=self.request.user)
        return form

class ExpenseUpdateView(LoginRequiredMixin, UpdateView):
    model = Expense
    form_class = ExpenseForm
    template_name = 'expenses/expense_form.html'
    success_url = reverse_lazy('expense-list')
    
    def get_queryset(self):
        return Expense.objects.filter(user=self.request.user)
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['category'].queryset = Category.objects.filter(user=self.request.user)
        return form

class ExpenseDeleteView(LoginRequiredMixin, DeleteView):
    model = Expense
    template_name = 'expenses/expense_confirm_delete.html'
    success_url = reverse_lazy('expense-list')
    
    def get_queryset(self):
        return Expense.objects.filter(user=self.request.user)

@login_required
def dashboard(request):
    # Get date ranges
    today = datetime.now().date()
    start_of_month = today.replace(day=1)
    last_month_end = start_of_month - timedelta(days=1)
    last_month_start = last_month_end.replace(day=1)
    
    # Current month expenses
    current_month_expenses = Expense.objects.filter(
        user=request.user, 
        date__gte=start_of_month,
        date__lte=today
    )
    
    # Last month expenses
    last_month_expenses = Expense.objects.filter(
        user=request.user, 
        date__gte=last_month_start,
        date__lte=last_month_end
    )
    
    # Total expenses
    total_expenses = current_month_expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    last_month_total = last_month_expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Category breakdown
    category_expenses = {}
    categories = Category.objects.filter(user=request.user)
    for category in categories:
        amount = current_month_expenses.filter(category=category).aggregate(Sum('amount'))['amount__sum'] or 0
        category_expenses[category.name] = float(amount)
    
    # Daily expenses for the current month
    daily_expenses = defaultdict(float)
    for expense in current_month_expenses:
        date_str = expense.date.strftime('%Y-%m-%d')
        daily_expenses[date_str] += float(expense.amount)
    
    # Convert to lists for Chart.js
    dates = list(daily_expenses.keys())
    amounts = list(daily_expenses.values())
    
    context = {
        'total_expenses': total_expenses,
        'last_month_total': last_month_total,
        'category_expenses': json.dumps(category_expenses),
        'dates': json.dumps(dates),
        'amounts': json.dumps(amounts),
        'recent_expenses': current_month_expenses.order_by('-date')[:5]
    }
    
    return render(request, 'expenses/dashboard.html', context)

@login_required
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            return redirect('expense-create')
    else:
        form = CategoryForm()
    
    return render(request, 'expenses/category_form.html', {'form': form})

@login_required
def expense_by_category_data(request):
    # For AJAX call to get category data
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    expenses = Expense.objects.filter(
        user=request.user,
        date__month=current_month,
        date__year=current_year
    )
    
    category_data = {}
    for expense in expenses:
        category_name = expense.category.name if expense.category else 'Uncategorized'
        if category_name in category_data:
            category_data[category_name] += float(expense.amount)
        else:
            category_data[category_name] = float(expense.amount)
    
    return JsonResponse(category_data)
