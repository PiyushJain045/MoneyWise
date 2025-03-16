from django.db import models
from django.utils import timezone
from datetime import timedelta

class Transaction(models.Model):
    date = models.DateField()
    balance_amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_amount = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(max_length=2, choices=[('DR', 'Debit'), ('CR', 'Credit')])
    recipient = models.CharField(max_length=255)
    category = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.date} - {self.recipient} - {self.transaction_amount}"

    @classmethod
    def get_last_n_days_transactions(cls, days):
        """
        Returns transactions for the last N days.
        """
        start_date = timezone.now().date() - timedelta(days=days)
        return cls.objects.filter(date__gte=start_date)

    @classmethod
    def get_last_n_months_transactions(cls, months):
        """
        Returns transactions for the last N months.
        """
        start_date = timezone.now().date() - timedelta(days=30 * months)
        return cls.objects.filter(date__gte=start_date)

    @classmethod
    def get_last_7_days_transactions(cls):
        """
        Returns transactions for the last 7 days.
        """
        return cls.get_last_n_days_transactions(7)

    @classmethod
    def get_last_30_days_transactions(cls):
        """
        Returns transactions for the last 30 days.
        """
        return cls.get_last_n_days_transactions(30)

    @classmethod
    def get_last_3_months_transactions(cls):
        """
        Returns transactions for the last 3 months.
        """
        return cls.get_last_n_months_transactions(3)

    @classmethod
    def get_last_6_months_transactions(cls):
        """
        Returns transactions for the last 6 months.
        """
        return cls.get_last_n_months_transactions(6)

    @classmethod
    def filter_by_category(cls, category):
        """
        Filters transactions by category.
        """
        return cls.objects.filter(category=category)

    @classmethod
    def filter_by_type(cls, transaction_type):
        """
        Filters transactions by type (DR or CR).
        """
        return cls.objects.filter(type=transaction_type)

    @classmethod
    def filter_by_recipient(cls, recipient):
        """
        Filters transactions by recipient.
        """
        return cls.objects.filter(recipient__icontains=recipient)