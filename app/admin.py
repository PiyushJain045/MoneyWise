# Register your models here.
from django.contrib import admin
from .models import Transaction

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

# Register the Transaction model with the custom admin class
admin.site.register(Transaction, TransactionAdmin)