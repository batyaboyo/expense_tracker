from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import JsonResponse
from .models import Expense, Category
from .forms import ExpenseForm, CategoryForm
import json
from datetime import datetime, timedelta

@login_required
def expense_list(request):
    expenses = Expense.objects.filter(user=request.user)
    total = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    
    return render(request, 'expenses/expense_list.html', {
        'expenses': expenses,
        'total': total,
    })

@login_required
def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            return redirect('expense_list')
    else:
        form = ExpenseForm()
    
    return render(request, 'expenses/expense_form.html', {
        'form': form,
        'title': 'Add Expense'
    })

@login_required
def edit_expense(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            return redirect('expense_list')
    else:
        form = ExpenseForm(instance=expense)
    
    return render(request, 'expenses/expense_form.html', {
        'form': form,
        'title': 'Edit Expense'
    })

@login_required
def delete_expense(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    
    if request.method == 'POST':
        expense.delete()
        return redirect('expense_list')
    
    return render(request, 'expenses/expense_confirm_delete.html', {
        'expense': expense
    })

@login_required
def category_list(request):
    categories = Category.objects.filter(user=request.user)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            return redirect('category_list')
    else:
        form = CategoryForm()
    
    return render(request, 'expenses/category_list.html', {
        'categories': categories,
        'form': form
    })

@login_required
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk, user=request.user)
    
    if request.method == 'POST':
        category.delete()
        return redirect('category_list')
    
    return render(request, 'expenses/category_confirm_delete.html', {
        'category': category
    })

@login_required
def expense_summary(request):
    # Get date range from request or use default (last 30 days)
    end_date = datetime.now().date()
    start_date = request.GET.get('start_date')
    end_date_param = request.GET.get('end_date')
    
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    else:
        start_date = end_date - timedelta(days=30)
        
    if end_date_param:
        end_date = datetime.strptime(end_date_param, '%Y-%m-%d').date()
    
    # Filter expenses by date range
    expenses = Expense.objects.filter(
        user=request.user,
        date__gte=start_date,
        date__lte=end_date
    )
    
    # Calculate summary data for charts
    category_data = list(expenses.values('category__name').annotate(total=Sum('amount')).order_by('-total'))
    
    # Daily spending
    daily_data = list(expenses.values('date').annotate(total=Sum('amount')).order_by('date'))
    dates = [item['date'].strftime('%Y-%m-%d') for item in daily_data]
    amounts = [float(item['total']) for item in daily_data]
    
    # Categories for filtering
    categories = Category.objects.filter(user=request.user)
    
    return render(request, 'expenses/expense_summary.html', {
        'category_data': json.dumps(category_data),
        'dates': json.dumps(dates),
        'amounts': json.dumps(amounts),
        'categories': categories,
        'start_date': start_date,
        'end_date': end_date,
    })

@login_required
def get_expense_data(request):
    """API endpoint to get expense data for AJAX charts"""
    
    # Get filter parameters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    category_id = request.GET.get('category_id')
    
    # Apply filters
    expenses = Expense.objects.filter(user=request.user)
    
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        expenses = expenses.filter(date__gte=start_date)
        
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        expenses = expenses.filter(date__lte=end_date)
    
    if category_id and category_id != '0':  # 0 means all categories
        expenses = expenses.filter(category_id=category_id)
    
    # Calculate data for charts
    category_data = list(expenses.values('category__name').annotate(total=Sum('amount')).order_by('-total'))
    daily_data = list(expenses.values('date').annotate(total=Sum('amount')).order_by('date'))
    
    # Format data for response
    response_data = {
        'category_data': category_data,
        'daily_data': [
            {
                'date': item['date'].strftime('%Y-%m-%d'),
                'total': float(item['total'])
            } for item in daily_data
        ]
    }
    
    return JsonResponse(response_data)
