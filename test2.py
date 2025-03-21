import numpy as np
from scipy.stats import zscore
from datetime import datetime
from django.db.models import Count
from app.models import Transaction  # Update 'yourapp' with your actual app name


np_array = [['2025-03-15' '1000' 'DR' 'RELIANCE SMART BAZAAR' 'Food & Dining']]

def anamoly_detection(np_array):
    # Extract data from numpy array
    date_str, transaction_amount, trans_type, recipient, category = np_array[0]
    transaction_amount = float(transaction_amount)  # Ensure it's a float
    
    # Convert string date to datetime object
    transaction_date = datetime.strptime(date_str, "%Y-%m-%d").date()

    # Extract Day_of_Week, Day_of_Month, Month
    day_of_week = transaction_date.weekday()
    day_of_month = transaction_date.day
    month = transaction_date.month

    # Fetch previous transactions from the database for the same day
    transactions_on_day = Transaction.objects.filter(date=transaction_date)
    transaction_count_per_day = transactions_on_day.count()

    # Fetch balance amount of the last transaction (assumption: ordered by date)
    last_transaction = Transaction.objects.filter(date__lte=transaction_date).order_by('-date').first()
    balance_amount = float(last_transaction.balance_amount) if last_transaction else 0.0

    # Fetch past transaction amounts for Z-score calculation
    past_transactions = list(
        Transaction.objects.filter(date=transaction_date).values_list('transaction_amount', flat=True)
    )

    # Convert to float array for numerical calculations
    past_transactions = np.array(past_transactions, dtype=np.float64)  

    # Compute Z-score if there are multiple transactions, else default to 0
    if len(past_transactions) > 1:
        transaction_z_scores = zscore(past_transactions)
        z_score_transaction = float(transaction_z_scores[-1])  # Latest transaction's Z-score
    else:
        z_score_transaction = 0.0

    # Create final numpy array ensuring numerical values are stored correctly
    final_array = np.array([
        [balance_amount, transaction_amount, trans_type, recipient, category,
         day_of_week, day_of_month, month, transaction_count_per_day, z_score_transaction]
    ], dtype=object)

    print("Final array:", final_array)
    return final_array
