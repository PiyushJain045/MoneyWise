import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")  # Prevents GUI issues
import pandas as pd
import seaborn as sns
import matplotlib.dates as mdates

from datetime import datetime, timedelta

from io import BytesIO
import base64
from app.models import Transaction  # Import your model

# Graph 1: line chart
# def trend_line_graph(n, time_unit="days"):
#     """
#     Generates a trend line chart for the last N days or months showing transaction trends.
    
#     :param n: Time filter (7, 30, 90, 180 for days OR 1, 3, 6 for months)
#     :param time_unit: "days" or "months"
#     :return: Base64-encoded image for embedding in Django templates
#     """
#     try:
#         # Fetch transactions using class methods
#         if time_unit == "days":
#             transactions = Transaction.get_last_n_days_transactions(n)
#             title = f"Spending Trend Over the Last {n} Days"
#         elif time_unit == "months":
#             transactions = Transaction.get_last_n_months_transactions(n)
#             title = f"Spending Trend Over the Last {n} Months"
#         else:
#             raise ValueError("Invalid time_unit. Choose 'days' or 'months'.")

#         # Convert QuerySet to DataFrame
#         df = pd.DataFrame(list(transactions.values("date", "transaction_amount")))

#         if df.empty:
#             print("No transactions found for the selected period.")
#             return None

#         # Convert Date column to datetime format
#         df["date"] = pd.to_datetime(df["date"])

#         # Aggregate total spending per day
#         df = df.groupby("date")["transaction_amount"].sum().reset_index()

#         # Sort values by date
#         df = df.sort_values("date")

#         # Plot the trend line
#         plt.figure(figsize=(12, 6))
#         sns.lineplot(data=df, x="date", y="transaction_amount", marker="o", linestyle="-", color="blue")
#         plt.xlabel("Date")
#         plt.ylabel("Total Transaction Amount (₹)")
#         plt.title(title)
#         plt.xticks(rotation=45, ha='right')
#         plt.tight_layout()
#         plt.grid(True)

#         # Convert plot to Base64 image
#         buffer = BytesIO()
#         plt.savefig(buffer, format="png", bbox_inches="tight")
#         buffer.seek(0)
#         image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
#         plt.close()

#         return image_base64

#     except Exception as e:
#         print(f"Error generating trend line graph: {e}")
#         return None
    
def trend_line_graph(n, time_unit="days"):
    """
    Generates a trend line chart for the last N days or months showing transaction trends.
    
    :param n: Time filter (7, 30, 90, 180 for days OR 1, 3, 6 for months)
    :param time_unit: "days" or "months"
    :return: Base64-encoded image for embedding in Django templates
    """
    try:
        # Clear any existing plots
        plt.close('all')
        
        # Fetch transactions using class methods
        if time_unit == "days":
            transactions = Transaction.get_last_n_days_transactions(n)
            title = f"Spending Trend Over the Last {n} Days"
            date_format = '%b %d'
        elif time_unit == "months":
            transactions = Transaction.get_last_n_months_transactions(n)
            title = f"Spending Trend Over the Last {n} Months"
            date_format = '%b %Y'
        else:
            raise ValueError("Invalid time_unit. Choose 'days' or 'months'.")

        # Convert QuerySet to DataFrame
        df = pd.DataFrame(list(transactions.values("date", "transaction_amount")))

        if df.empty:
            print("No transactions found for the selected period.")
            return None

        # Data validation and cleaning
        df["date"] = pd.to_datetime(df["date"])
        df = df.dropna()
        df["transaction_amount"] = pd.to_numeric(df["transaction_amount"], errors='coerce')
        df = df.dropna(subset=["transaction_amount"])

        # Aggregate and sort
        df = df.groupby("date")["transaction_amount"].sum().reset_index()
        df = df.sort_values("date")

        # Create figure with modern style
        plt.figure(figsize=(10, 5.5), dpi=100)
        sns.set_style("whitegrid", {'grid.linestyle': '--', 'grid.alpha': 0.4})
        
        # Create the plot
        ax = sns.lineplot(
            data=df, 
            x="date", 
            y="transaction_amount", 
            marker="o", 
            markersize=8,
            linewidth=2.5,
            color="#4C72B0",
            markerfacecolor="#DD8452",
            markeredgecolor="#DD8452"
        )
        
        # Add value annotations
        y_offset = df["transaction_amount"].max() * 0.03
        for _, row in df.iterrows():
            ax.text(
                row['date'], 
                row['transaction_amount'] + y_offset, 
                f"₹{int(row['transaction_amount'])}", 
                ha='center',
                va='bottom',
                fontsize=9,
                color="#555555"
            )
        
        # Style the plot
        plt.xlabel("Date", fontsize=11, labelpad=10, color="#333333")
        plt.ylabel("Amount (₹)", fontsize=11, labelpad=10, color="#333333")
        plt.title(title, fontsize=14, pad=20, color="#222222", fontweight='bold')
        ax.xaxis.set_major_formatter(mdates.DateFormatter(date_format))
        plt.xticks(rotation=45, ha='right', fontsize=9, color="#555555")
        plt.yticks(fontsize=9, color="#555555")
        sns.despine(left=True, bottom=True)
        ax.set_facecolor('#F8F9FA')
        
        # Add watermark
        ax.text(
            0.5, 0.5, 
            'Personal Finance', 
            transform=ax.transAxes,
            fontsize=40, 
            color='gray',
            alpha=0.1,
            ha='center', 
            va='center',
            rotation=30
        )

        # Save to buffer
        buffer = BytesIO()
        plt.savefig(buffer, format="png", bbox_inches="tight", dpi=120, pad_inches=0.5)
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        plt.close('all')
        
        return image_base64

    except Exception as e:
        print(f"Error generating trend line graph: {e}")
        plt.close('all')
        return None
    
# Graph 2: Pie Chart
def expense_category_pie_chart(n, time_unit="days"):
    """
    Generates a pie chart for expenses categorized by spending type.
    
    :param n: Time filter (7, 30, 90, 180 for days OR 1, 3, 6 for months)
    :param time_unit: "days" or "months"
    :return: Base64-encoded image for embedding in Django templates
    """
    try:
        # Fetch transactions using class methods
        if time_unit == "days":
            transactions = Transaction.get_last_n_days_transactions(n)
            title = f"Expense Breakdown Over the Last {n} Days"
        elif time_unit == "months":
            transactions = Transaction.get_last_n_months_transactions(n)
            title = f"Expense Breakdown Over the Last {n} Months"
        else:
            raise ValueError("Invalid time_unit. Choose 'days' or 'months'.")

        # Convert QuerySet to DataFrame
        df = pd.DataFrame(list(transactions.values("category", "transaction_amount", "type")))

        if df.empty:
            print("No transactions found for the selected period.")
            return None
        
        # Convert transaction_amount to numeric type
        df["transaction_amount"] = pd.to_numeric(df["transaction_amount"], errors="coerce")

        # Filter only expenses (Debit transactions)
        df = df[df["type"] == "DR"]

        # Aggregate total spending by category
        category_totals = df.groupby("category")["transaction_amount"].sum()
        
        print(category_totals.head())

        if category_totals.empty:
            print("Inside IF")
            return None  # No expenses in this period

        # Plot the Pie Chart
        plt.figure(figsize=(6,10))  # Increase figure size for better spacing

        # Explode smaller slices for better visibility
        explode = [0.1 if (value / category_totals.sum()) < 0.05 else 0 for value in category_totals]

        # Plot the pie chart
        wedges, texts, autotexts = plt.pie(
            category_totals,
            labels=category_totals.index,
            autopct='%1.1f%%',
            startangle=90,
            explode=explode,
            pctdistance=0.85,  # Adjust percentage label distance
            labeldistance=1.1,  # Adjust category label distance
            colors=sns.color_palette("tab10"),  # Use a better color palette
            textprops={'fontsize': 10}  # Adjust font size
        )

        # Add a legend for better readability
        plt.legend(
            wedges,
            category_totals.index,
            title="Categories",
            loc="center left",
            bbox_to_anchor=(1, 0, 0.5, 1)  # Place legend outside the pie chart
        )

        plt.title(title, pad=20)  # Add padding to the title
        plt.tight_layout()  # Automatically adjust layout to prevent overlap

        # Convert plot to Base64 image
        buffer = BytesIO()
        plt.savefig(buffer, format="png", bbox_inches="tight")  # Use bbox_inches="tight" to prevent cropping
        buffer.seek(0)

        # Check if buffer contains data
        if buffer.getbuffer().nbytes == 0:
            print("⚠️ Empty buffer! Something went wrong with the plot.")
            return None
        
        image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        plt.close()

        return image_base64

    except Exception as e:
        print(f"Error generating pie chart: {e}")
        return None
    
 
# Graph 3: Bar chart
def income_vs_expense_bar_chart(n, time_unit="days"):
    """
    Generates a bar chart comparing total income (CR) vs. total expense (DR).

    :param n: Time filter (7, 30, 90, 180 for days OR 1, 3, 6 for months)
    :param time_unit: "days" or "months"
    :return: Base64-encoded image for embedding in Django templates
    """
    try:
        # Fetch transactions using class methods
        if time_unit == "days":
            transactions = Transaction.get_last_n_days_transactions(n)
            title = f"Income vs Expense Over the Last {n} Days"
        elif time_unit == "months":
            transactions = Transaction.get_last_n_months_transactions(n)
            title = f"Income vs Expense Over the Last {n} Months"
        else:
            raise ValueError("Invalid time_unit. Choose 'days' or 'months'.")

        # Convert QuerySet to DataFrame
        df = pd.DataFrame(list(transactions.values("transaction_amount", "type")))

        if df.empty:
            print("⚠️ No transactions found for the selected period.")
            return None

        # Convert transaction_amount to numeric
        df["transaction_amount"] = pd.to_numeric(df["transaction_amount"], errors="coerce")

        # Calculate total income (CR) and total expense (DR)
        income = df[df["type"] == "CR"]["transaction_amount"].sum()
        expense = df[df["type"] == "DR"]["transaction_amount"].sum()

        if income == 0 and expense == 0:
            print("⚠️ No income or expense data available.")
            return None

        # Prepare data for plotting
        categories = ["Income", "Expense"]
        values = [income, expense]

        # Create bar chart
        plt.figure(figsize=(5, 5))
        sns.barplot(x=categories, y=values, palette=["green", "red"])

        # Add labels
        plt.xlabel("Category")
        plt.ylabel("Total Amount (₹)")
        plt.title(title)
        plt.grid(axis="y", linestyle="--", alpha=0.7)

        # Show values on top of bars
        for i, v in enumerate(values):
            plt.text(i, v + (v * 0.05), f"₹{v:,.2f}", ha="center", fontsize=12, fontweight="bold")

        # Convert plot to Base64 image
        buffer = BytesIO()
        plt.savefig(buffer, format="png", bbox_inches="tight")  # Prevent clipping
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        plt.close()

        return image_base64

    except Exception as e:
        print(f"❌ Error generating bar chart: {e}")
        return None
    
# Graph 4: Donut pie chart
def top_5_expenses_donut_chart(n, time_unit="days"):
    """
    Generates a donut chart for the top 5 individual debit (DR) transactions.

    :param n: Time filter (7, 30, 90, 180 for days OR 1, 3, 6 for months)
    :param time_unit: "days" or "months"
    :return: Base64-encoded image for embedding in Django templates
    """
    try:
        # Fetch transactions using class methods
        if time_unit == "days":
            transactions = Transaction.get_last_n_days_transactions(n)
            title = f"Top 5 Largest Transactions Over the Last {n} Days"
        elif time_unit == "months":
            transactions = Transaction.get_last_n_months_transactions(n)
            title = f"Top 5 Largest Transactions Over the Last {n} Months"
        else:
            raise ValueError("Invalid time_unit. Choose 'days' or 'months'.")

        # Convert QuerySet to DataFrame
        df = pd.DataFrame(list(transactions.values("recipient", "transaction_amount", "type")))

        if df.empty:
            print("⚠️ No transactions found for the selected period.")
            return None

        # Convert transaction_amount to numeric
        df["transaction_amount"] = pd.to_numeric(df["transaction_amount"], errors="coerce")

        # Filter only debit (DR) transactions
        df = df[df["type"] == "DR"]

        if df.empty:
            print("⚠️ No debit (DR) transactions found.")
            return None

        # Select the top 5 largest individual expenses
        top_expenses = df.nlargest(5, "transaction_amount")

        if top_expenses.empty:
            print("⚠️ No significant individual expenses found.")
            return None

        # Prepare data for plotting
        recipients = top_expenses["recipient"]
        amounts = top_expenses["transaction_amount"]

        # Create a Donut Chart (Pie Chart with a Hole)
        plt.figure(figsize=(5, 5))
        wedges, texts, autotexts = plt.pie(
            amounts, labels=recipients, autopct='%1.1f%%', startangle=140,
            wedgeprops={'linewidth': 1, 'edgecolor': 'black'},
            pctdistance=0.85, colors=sns.color_palette("Reds_r", len(recipients))
        )

        # Draw a circle in the middle to create a donut effect
        centre_circle = plt.Circle((0, 0), 0.70, fc='white')
        plt.gca().add_patch(centre_circle)

        # Title and formatting
        plt.title(title, fontsize=14)
        plt.ylabel("")  # Hide default y-axis label
        plt.tight_layout()

        # Convert plot to Base64 image
        buffer = BytesIO()
        plt.savefig(buffer, format="png", bbox_inches="tight")  # Prevent clipping
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        plt.close()

        return image_base64

    except Exception as e:
        print(f"❌ Error generating top 5 transactions donut chart: {e}")
        return None
    

# Monthly budget transaction
def monthly_budget_visualization(monthly_budget_target=10000):
    """
    Generates monthly budget statistics and a progress bar visualization.

    :param monthly_budget_target: User-defined budget goal (Default: 10,000)
    :return: Dictionary containing expense summary and a base64-encoded image
    """
    try:
        # Get the first and last day of the current month
        today = datetime.today()
        first_day = today.replace(day=1)
        last_day = (first_day.replace(month=first_day.month % 12 + 1, day=1) - timedelta(days=1)).date()

        # Fetch transactions within the current month
        transactions = Transaction.objects.filter(date__gte=first_day, date__lte=today, type="DR")

        # Convert QuerySet to DataFrame
        df = pd.DataFrame(list(transactions.values("transaction_amount")))

        # Calculate total expense so far
        total_expense = df["transaction_amount"].sum() if not df.empty else 0

        # Calculate budget used percentage
        budget_used = (total_expense / monthly_budget_target) * 100
        budget_used = min(budget_used, 100)  # Ensure it doesn't exceed 100%

        # Calculate daily spending limit to stay within budget
        remaining_budget = max(monthly_budget_target - total_expense, 0)
        remaining_days = (last_day - today.date()).days
        daily_spending_limit = remaining_budget / remaining_days if remaining_days > 0 else 0

        # Generate Progress Bar (Budget Usage)
        plt.figure(figsize=(8, 1))
        plt.barh([""], [budget_used], color="red", height=0.5, label="Used Budget")
        plt.barh([""], [100 - budget_used], left=[budget_used], color="green", height=0.5, label="Remaining Budget")
        plt.xlim(0, 100)
        plt.xticks([])
        plt.yticks([])
        plt.legend(loc="upper right")
        plt.title(f"Budget Used: {budget_used:.1f}% | Remaining: {100 - budget_used:.1f}%")

        # Convert plot to Base64 image
        buffer = BytesIO()
        plt.savefig(buffer, format="png", bbox_inches="tight")
        buffer.seek(0)
        budget_progress_image = base64.b64encode(buffer.getvalue()).decode("utf-8")
        plt.close()

        return {
            "total_expense": total_expense,
            "budget_used": budget_used,
            "daily_spending_limit": daily_spending_limit,
            "budget_progress_image": budget_progress_image,
        }

    except Exception as e:
        print(f"❌ Error generating monthly budget visualization: {e}")
        return None
    

### Esimate Section
def estimate_section():
    """
    Computes financial estimates including current balance, average monthly income, and expenses.

    :return: Dictionary containing the estimate data
    """
    try:
        # 1️⃣ Current Balance (from the most recent transaction)
        latest_transaction = Transaction.objects.order_by("-date").first()
        current_balance = latest_transaction.balance_amount if latest_transaction else 0

        # Fetch all transactions
        transactions = Transaction.objects.all()

        if not transactions.exists():
            return {
                "current_balance": current_balance,
                "avg_monthly_income": 0,
                "avg_monthly_expense": 0,
                "net_report": "No data available",
                "net_color": "black",
            }

        # Convert QuerySet to DataFrame
        df = pd.DataFrame(list(transactions.values("date", "transaction_amount", "type")))

        # Convert date column to datetime
        df["date"] = pd.to_datetime(df["date"])

        # Extract year and month for grouping
        df["year_month"] = df["date"].dt.to_period("M")

        # 2️⃣ Calculate Average Monthly Income (Credit)
        income_df = df[df["type"] == "CR"].groupby("year_month")["transaction_amount"].sum()
        avg_monthly_income = income_df.mean() if not income_df.empty else 0

        # 3️⃣ Calculate Average Monthly Expense (Debit)
        expense_df = df[df["type"] == "DR"].groupby("year_month")["transaction_amount"].sum()
        avg_monthly_expense = expense_df.mean() if not expense_df.empty else 0

        # 4️⃣ Determine Net Report
        if avg_monthly_expense > avg_monthly_income:
            net_report = f"⚠️ You are overspending by ₹{avg_monthly_expense - avg_monthly_income:.2f}"
            net_color = "red"
        else:
            net_report = f"✅ You are saving ₹{avg_monthly_income - avg_monthly_expense:.2f} per month"
            net_color = "green"

        return {
            "current_balance": current_balance,
            "avg_monthly_income": avg_monthly_income,
            "avg_monthly_expense": avg_monthly_expense,
            "net_report": net_report,
            "net_color": net_color,
        }

    except Exception as e:
        print(f"❌ Error generating estimate section: {e}")
        return None