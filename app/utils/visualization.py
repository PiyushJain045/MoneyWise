import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from io import BytesIO
import base64
from app.models import Transaction  # Import your model

# Graph 1: line chart
def trend_line_graph(n, time_unit="days"):
    """
    Generates a trend line chart for the last N days or months showing transaction trends.
    
    :param n: Time filter (7, 30, 90, 180 for days OR 1, 3, 6 for months)
    :param time_unit: "days" or "months"
    :return: Base64-encoded image for embedding in Django templates
    """
    try:
        # Fetch transactions using class methods
        if time_unit == "days":
            transactions = Transaction.get_last_n_days_transactions(n)
            title = f"Spending Trend Over the Last {n} Days"
        elif time_unit == "months":
            transactions = Transaction.get_last_n_months_transactions(n)
            title = f"Spending Trend Over the Last {n} Months"
        else:
            raise ValueError("Invalid time_unit. Choose 'days' or 'months'.")

        # Convert QuerySet to DataFrame
        df = pd.DataFrame(list(transactions.values("date", "transaction_amount")))

        if df.empty:
            print("No transactions found for the selected period.")
            return None

        # Convert Date column to datetime format
        df["date"] = pd.to_datetime(df["date"])

        # Aggregate total spending per day
        df = df.groupby("date")["transaction_amount"].sum().reset_index()

        # Sort values by date
        df = df.sort_values("date")

        # Plot the trend line
        plt.figure(figsize=(10, 5))
        sns.lineplot(data=df, x="date", y="transaction_amount", marker="o", linestyle="-", color="blue")
        plt.xlabel("Date")
        plt.ylabel("Total Transaction Amount (₹)")
        plt.title(title)
        plt.xticks(rotation=45)
        plt.grid(True)

        # Convert plot to Base64 image
        buffer = BytesIO()
        plt.savefig(buffer, format="png")
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        plt.close()

        return image_base64

    except Exception as e:
        print(f"Error generating trend line graph: {e}")
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
        print("DF")
        print(category_totals.head())

        if category_totals.empty:
            print("Inside IF")
            return None  # No expenses in this period

        # Plot the Pie Chart
        plt.figure(figsize=(8, 6))
        category_totals.plot.pie(autopct='%1.1f%%', startangle=90, cmap="tab10")
        plt.title(title)
        plt.ylabel("")  # Hide the default y-axis label

        # Convert plot to Base64 image
        buffer = BytesIO()
        plt.savefig(buffer, format="png")
        buffer.seek(0)

        # Check if buffer contains data
        print("Buffer size:", buffer.getbuffer().nbytes)

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
        plt.figure(figsize=(8, 6))
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
        plt.figure(figsize=(8, 6))
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
