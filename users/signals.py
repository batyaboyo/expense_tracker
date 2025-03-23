# users/signals.py
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from transactions.models import Category

@receiver(post_save, sender=User)
def create_default_categories(sender, instance, created, **kwargs):
    if created:
        # Create default expense categories
        expense_categories = [
            'Food & Dining', 'Transportation', 'Housing', 'Utilities', 
            'Entertainment', 'Shopping', 'Healthcare', 'Education',
            'Personal Care', 'Travel', 'Gifts & Donations', 'Miscellaneous'
        ]
        
        for category_name in expense_categories:
            Category.objects.create(
                name=category_name,
                type='expense',
                user=instance
            )
        
        # Create default income categories
        income_categories = [
            'Salary', 'Freelance', 'Investments', 'Gifts', 'Other Income'
        ]
        
        for category_name in income_categories:
            Category.objects.create(
                name=category_name,
                type='income',
                user=instance
            )
