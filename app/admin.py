# Register your models here.
from django.contrib import admin
from .models import Transaction, Profile, UserAccount, MonthlyBudget

class TransactionAdmin(admin.ModelAdmin):
    # Fields to display in the list view
    list_display = ('date', 'recipient', 'transaction_amount', 'type', 'category', 'balance_amount')
    
    # Fields to filter by in the right sidebar
    list_filter = ('date', 'type', 'category')
    
    # Fields to search by in the search bar
    search_fields = ('recipient', 'category')
    
    # Enable date hierarchy for easy navigation by date
    date_hierarchy = 'date'
    
    # Fields to allow editing directly from the list view
    list_editable = ('transaction_amount', 'type', 'category')
    
    # Number of items to display per page in the list view
    list_per_page = 20


### 📌 Admin for Profile Model
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'age', 'phone', 'profession', 'email')
    search_fields = ('name', 'phone', 'email')
    list_filter = ('profession',)
    list_per_page = 20

### 📌 Admin for UserAccount Model
class UserAccountAdmin(admin.ModelAdmin):
    list_display = ('user', 'account_name', 'account_type', 'current_balance')
    search_fields = ('account_name',)
    list_filter = ('account_type',)
    list_editable = ('current_balance',)
    list_per_page = 20

### 📌 Admin for MonthlyBudget Model
class MonthlyBudgetAdmin(admin.ModelAdmin):
    list_display = ('user', 'monthly_budget')
    search_fields = ('user__username',)
    list_editable = ('monthly_budget',)
    list_per_page = 20


# Register the Transaction model with the custom admin class
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(UserAccount, UserAccountAdmin)
admin.site.register(MonthlyBudget, MonthlyBudgetAdmin)