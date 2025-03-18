from app.models import Transaction, Profile# UserProfile
import pandas as pd
from datetime import datetime

# def generate_financial_report(user):
from app.models import Transaction
import pandas as pd
from datetime import datetime

def generate_financial_report(user):
    """
    Generates a text-based financial report without requiring user authentication.

    :return: String financial report
    """
    try:
        # Hardcoded user details (later can be fetched dynamically)
        profile = Profile.objects.get(user=user)
        age = profile.age
        profession = profile.profession
        country = "India"

        user_details = f"User Profile:\n- Age: {age}\n- Profession: {profession}\n- Country: {country}\n"

        # Get latest balance from the most recent transaction
        latest_transaction = Transaction.objects.order_by("-date").first()
        current_balance = latest_transaction.balance_amount if latest_transaction else 0

        # Fetch all transactions (for all users, since user filtering is not needed yet)
        transactions = Transaction.objects.all()

        if not transactions.exists():
            return f"{user_details}\nNo financial data available for analysis."

        # Convert transactions to DataFrame
        df = pd.DataFrame(list(transactions.values("date", "transaction_amount", "type")))

        # Convert date column to datetime
        df["date"] = pd.to_datetime(df["date"])
        df["year_month"] = df["date"].dt.to_period("M")

        # ✅ Convert transaction_amount to numeric to avoid dtype errors
        df["transaction_amount"] = pd.to_numeric(df["transaction_amount"], errors="coerce")

        # Calculate Monthly Income (Credit)
        income_df = df[df["type"] == "CR"].groupby("year_month")["transaction_amount"].sum()
        avg_monthly_income = income_df.mean() if not income_df.empty else 0

        # Calculate Monthly Expenses (Debit)
        expense_df = df[df["type"] == "DR"].groupby("year_month")["transaction_amount"].sum()
        avg_monthly_expense = expense_df.mean() if not expense_df.empty else 0

        # Budget & Savings Insights
        savings_potential = avg_monthly_income - avg_monthly_expense
        savings_status = "✔️ Healthy" if savings_potential > 0 else "⚠️ Needs Improvement"

            # ✅ Fix: Convert `transaction_amount` before using `nlargest()`
        df["transaction_amount"] = pd.to_numeric(df["transaction_amount"], errors="coerce")

        # Spending Pattern Analysis
        biggest_expense = df[df["type"] == "DR"].nlargest(1, "transaction_amount")
        top_expense_category = biggest_expense["transaction_amount"].values[0] if not biggest_expense.empty else "No data"

        # Generate Report
        report = f"""
        📊 Financial Health Report - {datetime.today().strftime('%Y-%m-%d')}
        
        {user_details}
        
        💰 Current Balance: ₹{current_balance:.2f}
        💵 Average Monthly Income: ₹{avg_monthly_income:.2f}
        📉 Average Monthly Expenses: ₹{avg_monthly_expense:.2f}
        💡 Savings Potential: ₹{savings_potential:.2f} ({savings_status})
        🛒 Biggest Expense Last Month: ₹{top_expense_category}
        🏆 Overall Financial Status: {'✅ Stable' if savings_potential > 0 else '❗ At Risk'}

        """

        return report

    except Exception as e:
        return f"❌ Error generating financial report: {e}"

