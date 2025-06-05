from django.db import models
from django.contrib.auth.models import User 
from django.utils import timezone
from datetime import timedelta

### 📌 Model 1: Profile (User Details)
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Links to Django's User model
    name = models.CharField(max_length=255, null=False, blank=False)
    age = models.PositiveIntegerField(null=True, blank=True)
    email = models.EmailField(unique=True)  # Automatically fetched from User model
    phone = models.CharField(max_length=15, unique=True, null=False, blank=False)
    profession = models.CharField(
        max_length=20,
        choices=[
            ("Businessman", "Businessman"),
            ("Employee", "Employee"),
            ("Student", "Student"),
            ("Housewife", "Housewife"),
            ("Other", "Other"),
        ],
        null=False,
        blank=False,
    )
    profile_photo = models.ImageField(upload_to="profile_photos/", null=True, blank=True)  # Optional

    def __str__(self):
        return self.name
    
### 📌 Model 2: UserAccount (Bank Account Info)
class UserAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Links to Django's User model
    account_name = models.CharField(max_length=255, null=False, blank=False)
    account_type = models.CharField(
        max_length=10,
        choices=[("Current", "Current"), ("Savings", "Savings")],
        null=False,
        blank=False,
    )
    current_balance = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.account_name} - {self.account_type}"
    
### 📌 Model 3: MonthlyBudget
class MonthlyBudget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Links to Django's User model
    monthly_budget = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Monthly Budget: ₹{self.monthly_budget}"

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
#######################################################

# model 5
class RecurringPayment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Links to User model
    name = models.CharField(max_length=255, null=False, blank=False)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False)
    category = models.CharField(max_length=255, null=False, blank=False)
    type = models.CharField(max_length=2, choices=[('DR', 'Debit'), ('CR', 'Credit')], null=False, blank=False)
    date = models.PositiveIntegerField(
        choices=[(i, f"Day {i}") for i in range(1, 29)],  # Limits to 1-28 to avoid issues with shorter months
        null=False,
        blank=False
    )

    def __str__(self):
        return f"{self.name} - {self.type} - ₹{self.amount} on Day {self.date}"


#6 
class AnomalousTransaction(models.Model):
    balance_amount = models.FloatField()
    date = models.DateField()
    transaction_amount = models.FloatField()
    transaction_type = models.CharField(max_length=2)  # DR/CR
    recipient = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    anomaly_score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed = models.BooleanField(default=False)  # For manual review

    class Meta:
        ordering = ['-date']


### 📌 Model 7: Portfolio (User Investments)
class Portfolio(models.Model):
    INVESTMENT_CHOICES = [
        ("Stocks", "Stocks"),
        ("Bonds", "Bonds"),
        ("Real Estate", "Real Estate"),
        ("Crypto", "Crypto"),
        ("Gold", "Gold"),
        ("Mutual Funds", "Mutual Funds"),
        ("Money Market", "Money Market"),
        ("Others", "Others"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link to Django's User model
    investment_type = models.CharField(max_length=50, choices=INVESTMENT_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()

    def __str__(self):
        return f"{self.user.username} - {self.investment_type} - ₹{self.amount}"
    
    @classmethod
    def get_total_portfolio_value(cls, user):
        """
        Returns the total portfolio value for the given user.
        """
        total = cls.objects.filter(user=user).aggregate(total_value=models.Sum('amount'))['total_value']
        return total or 0.0  # Return 0.0 if no records exist
