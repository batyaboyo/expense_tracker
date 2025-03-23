# transactions/templatetags/expense_extras.py
from django import template
register = template.Library()

@register.filter
def float_divide(value, arg):
    try:
        return float(value) / float(arg) * 100
    except (ValueError, ZeroDivisionError):
        return 0
