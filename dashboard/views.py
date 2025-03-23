# dashboard/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from django.utils import timezone
from transactions.models import Transaction, Category, Budget
from datetime import timedelta
import json

@login_required
def dashboard(request):
    # Get the current month and year
    today = timezone.now().date()
    current_month_start = today.replace(day=1)
    next_month_start = (today.replace(day=28) + timedelta(days=4)).replace(day=1)
    
    # Date ranges
    last_30_days_start = today - timedelta(days=30)
    last_6_months_start = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
    last_6_months_start = last_6_months_start.replace(month=((last_6_months_start.month - 6) % 12 or 12))
    if last_6_months_start.month > today.month:
        last_6_months_start = last_6_months_start.replace(year=today.year - 1)
    
    # Current month stats
    current_month_income = Transaction.objects.filter(
        user=request.user,
        transaction_type='income',
        date__gte=current_month_start,
        date__lt=next_month_start
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    current_month_expense = Transaction.objects.filter(
        user=request.user,
        transaction_type='expense',
        date__gte=current_month_start,
        date__lt=next_month_start
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Last 30 days stats
    last_30_days_income = Transaction.objects.filter(
        user=request.user,
        transaction_type='income',
        date__gte=last_30_days_start
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    last_30_days_expense = Transaction.objects.filter(
        user=request.user,
        transaction_type='expense',
        date__gte=last_30_days_start
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Get budget insights for the current month
    budget_insights = []
    budgets = Budget.objects.filter(
        user=request.user,
        month__year=today.year,
        month__month=today.month
    )
    
    for budget in budgets:
        spending = Transaction.objects.filter(
            user=request.user,
            category=budget.category,
            transaction_type='expense',
            date__gte=current_month_start,
            date__lt=next_month_start
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        percentage = (spending / budget.amount) * 100 if budget.amount else 0
        status = 'danger' if percentage >= 90 else 'warning' if percentage >= 70 else 'good'
        
        budget_insights.append({
            'category': budget.category.name,
            'budget': budget.amount,
            'spent': spending,
            'remaining': budget.amount - spending,
            'percentage': int(percentage),
            'status': status
        })
    
    # Sort insights by percentage spent (highest first)
    budget_insights.sort(key=lambda x: x['percentage'], reverse=True)
    
    # Monthly spending trend (last 6 months)
    monthly_spending = []
    for i in range(6):
        month_date = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
        month_date = month_date.replace(month=((month_date.month - i) % 12 or 12))
        if month_date.month > today.month:
            month_date = month_date.replace(year=today.year - 1)
            
        next_month = (month_date.replace(day=28) + timedelta(days=4)).replace(day=1)
        
        monthly_total = Transaction.objects.filter(
            user=request.user,
            transaction_type='expense',
            date__gte=month_date,
            date__lt=next_month
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        monthly_spending.append({
            'month': month_date.strftime('%b %Y'),
            'total': float(monthly_total)
        })
    
    # Reverse to show chronological order
    monthly_spending.reverse()
    
    # Top spending categories (last 30 days)
    top_expense_categories = Transaction.objects.filter(
        user=request.user,
        transaction_type='expense',
        date__gte=last_30_days_start
    ).values('category__name').annotate(total=Sum('amount')).order_by('-total')[:5]
    
    # Prepare chart data
    expense_categories = [item['category__name'] for item in top_expense_categories]
    expense_values = [float(item['total']) for item in top_expense_categories]
    
    monthly_labels = [item['month'] for item in monthly_spending]
    monthly_values = [item['total'] for item in monthly_spending]
    
    # Recent transactions
    recent_transactions = Transaction.objects.filter(
        user=request.user
    ).order_by('-date')[:5]
    
    context = {
        'current_month': today.strftime('%B %Y'),
        'current_month_income': current_month_income,
        'current_month_expense': current_month_expense,
        'current_month_savings': current_month_income - current_month_expense,
        'last_30_days_income': last_30_days_income,
        'last_30_days_expense': last_30_days_expense,
        'last_30_days_savings': last_30_days_income - last_30_days_expense,
        'budget_insights': budget_insights,
        'monthly_labels_json': json.dumps(monthly_labels),
        'monthly_values_json': json.dumps(monthly_values),
        'expense_categories_json': json.dumps(expense_categories),
        'expense_values_json': json.dumps(expense_values),
        'recent_transactions': recent_transactions,
    }
    
    return render(request, 'dashboard/dashboard.html', context)

@login_required
def reports(request):
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=90)  # Default to last 90 days
    
    # Handle date filter
    if request.method == 'GET' and 'start_date' in request.GET and 'end_date' in request.GET:
        try:
            start_date = datetime.strptime(request.GET['start_date'], '%Y-%m-%d').date()
            end_date = datetime.strptime(request.GET['end_date'], '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, 'Invalid date format. Using default date range.')
    
    # Get all transactions for the period
    transactions = Transaction.objects.filter(
        user=request.user,
        date__gte=start_date,
        date__lte=end_date
    ).order_by('-date')
    
    # Summary statistics
    total_income = transactions.filter(transaction_type='income').aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = transactions.filter(transaction_type='expense').aggregate(Sum('amount'))['amount__sum'] or 0
    net_savings = total_income - total_expense
    saving_rate = (net_savings / total_income * 100) if total_income > 0 else 0
    
    # Expenses by category
    expenses_by_category = transactions.filter(
        transaction_type='expense'
    ).values('category__name').annotate(total=Sum('amount')).order_by('-total')
    
    # Income by category
    income_by_category = transactions.filter(
        transaction_type='income'
    ).values('category__name').annotate(total=Sum('amount')).order_by('-total')
    
    # Monthly breakdown
    monthly_data = {}
    for transaction in transactions:
        month_key = transaction.date.strftime('%Y-%m')
        month_name = transaction.date.strftime('%b %Y')
        
        if month_key not in monthly_data:
            monthly_data[month_key] = {
                'month': month_name,
                'income': 0,
                'expense': 0,
                'net': 0
            }
        
        if transaction.transaction_type == 'income':
            monthly_data[month_key]['income'] += float(transaction.amount)
        else:
            monthly_data[month_key]['expense'] += float(transaction.amount)
            
        monthly_data[month_key]['net'] = monthly_data[month_key]['income'] - monthly_data[month_key]['expense']
    
    # Sort monthly data by date
    monthly_breakdown = [monthly_data[key] for key in sorted(monthly_data.keys())]
    
    # Prepare chart data
    expense_categories = [item['category__name'] for item in expenses_by_category]
    expense_values = [float(item['total']) for item in expenses_by_category]
    
    monthly_labels = [item['month'] for item in monthly_breakdown]
    monthly_income = [item['income'] for item in monthly_breakdown]
    monthly_expense = [item['expense'] for item in monthly_breakdown]
    monthly_net = [item['net'] for item in monthly_breakdown]
    
    context = {
        'start_date': start_date,
        'end_date': end_date,
        'total_income': total_income,
        'total_expense': total_expense,
        'net_savings': net_savings,
        'saving_rate': round(saving_rate, 1),
        'transactions': transactions,
        'expenses_by_category': expenses_by_category,
        'income_by_category': income_by_category,
        'monthly_breakdown': monthly_breakdown,
        'expense_categories_json': json.dumps(expense_categories),
        'expense_values_json': json.dumps(expense_values),
        'monthly_labels_json': json.dumps(monthly_labels),
        'monthly_income_json': json.dumps(monthly_income),
        'monthly_expense_json': json.dumps(monthly_expense),
        'monthly_net_json': json.dumps(monthly_net),
    }
    
    return render(request, 'dashboard/reports.html', context)
