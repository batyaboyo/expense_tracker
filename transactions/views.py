# transactions/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Transaction, Category
from .forms import TransactionForm, CategoryForm

@login_required
def transaction_list(request):
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')
    return render(request, 'transactions/transaction_list.html', {'transactions': transactions})

@login_required
def add_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            messages.success(request, 'Transaction added successfully!')
            return redirect('transaction_list')
    else:
        form = TransactionForm()
    
    user_categories = Category.objects.filter(user=request.user)
    return render(request, 'transactions/add_transaction.html', {'form': form, 'categories': user_categories})

@login_required
def edit_transaction(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=transaction)
        if form.is_valid():
            form.save()
            messages.success(request, 'Transaction updated successfully!')
            return redirect('transaction_list')
    else:
        form = TransactionForm(instance=transaction)
    
    return render(request, 'transactions/edit_transaction.html', {'form': form})

@login_required
def delete_transaction(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    if request.method == 'POST':
        transaction.delete()
        messages.success(request, 'Transaction deleted successfully!')
        return redirect('transaction_list')
    return render(request, 'transactions/delete_transaction.html', {'transaction': transaction})

@login_required
def manage_categories(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            messages.success(request, 'Category added successfully!')
            return redirect('manage_categories')
    else:
        form = CategoryForm()
    
    categories = Category.objects.filter(user=request.user)
    return render(request, 'transactions/manage_categories.html', {'form': form, 'categories': categories})


# transactions/views.py (add these functions)
@login_required
def manage_budgets(request):
    if request.method == 'POST':
        form = BudgetForm(request.POST)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.user = request.user
            
            # Check if budget for this category and month already exists
            existing_budget = Budget.objects.filter(
                user=request.user,
                category=budget.category,
                month__year=budget.month.year,
                month__month=budget.month.month
            ).first()
            
            if existing_budget:
                existing_budget.amount = budget.amount
                existing_budget.save()
                messages.success(request, 'Budget updated successfully!')
            else:
                budget.save()
                messages.success(request, 'Budget added successfully!')
                
            return redirect('manage_budgets')
    else:
        form = BudgetForm()
    
    # Get current month's budgets
    current_month = timezone.now().date().replace(day=1)
    
    budgets = Budget.objects.filter(
        user=request.user,
        month__year=current_month.year,
        month__month=current_month.month
    )
    
    # Calculate spending for each category
    budget_data = []
    for budget in budgets:
        spending = Transaction.objects.filter(
            user=request.user,
            category=budget.category,
            transaction_type='expense',
            date__year=current_month.year,
            date__month=current_month.month
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        budget_data.append({
            'budget': budget,
            'spending': spending,
            'remaining': budget.amount - spending,
            'percentage': int((spending / budget.amount) * 100) if budget.amount > 0 else 0
        })
    
    # Get user categories for the form
    expense_categories = Category.objects.filter(user=request.user, type='expense')
    
    return render(request, 'transactions/manage_budgets.html', {
        'form': form,
        'budget_data': budget_data,
        'expense_categories': expense_categories,
        'current_month': current_month
    })


# transactions/views.py (add this)
import csv
from django.http import HttpResponse

@login_required
def export_transactions(request):
    # Get date range from query parameters
    start_date = request.GET.get('start_date', None)
    end_date = request.GET.get('end_date', None)
    
    # Parse dates if provided
    if start_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        except ValueError:
            start_date = None
    
    if end_date:
        try:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            end_date = None
    
    # Filter transactions based on date range
    transactions = Transaction.objects.filter(user=request.user)
    if start_date:
        transactions = transactions.filter(date__gte=start_date)
    if end_date:
        transactions = transactions.filter(date__lte=end_date)
    
    # Sort by date
    transactions = transactions.order_by('-date')
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="transactions.csv"'
    
    # Write CSV header and data
    writer = csv.writer(response)
    writer.writerow(['Date', 'Type', 'Category', 'Description', 'Amount'])
    
    for transaction in transactions:
        writer.writerow([
            transaction.date.strftime('%Y-%m-%d'),
            transaction.transaction_type.title(),
            transaction.category.name if transaction.category else 'Uncategorized',
            transaction.description,
            transaction.amount
        ])
    
    return response
