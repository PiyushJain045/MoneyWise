from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.views import View
from .models import Transaction 


#Misslaneous
import csv
import os
from django.conf import settings

#Graphs and visualization
from django.utils import timezone


#Utils functions
from .utils.data_processing import clean_bank_statements  # Import CSV processing
from .utils.visualization import (
    trend_line_graph, expense_category_pie_chart,
    income_vs_expense_bar_chart, top_5_expenses_donut_chart, 
    monthly_budget_visualization, estimate_section
)  

# Imports for Environment Variable
import os
from dotenv import load_dotenv
load_dotenv() 


# Create your views here.

class Home(View):
    def get(self, request):
        return render(request, "home.html")

    def post(self, request):
        pass


class Dashboard(View):
    def get(self, request):
        print("Inside GET dashboard")


        ### ESTIMATE SECTION
        estimate_data = estimate_section()

        ### MONTHLY BUDGET SECTION ###
        monthly_budget_target = 16000  # This will later come from the database
        budget_data = monthly_budget_visualization(monthly_budget_target)


        # Generate the trend line graph default for GET request
        n = 30
        time_unit = 'days'

        # Check if we have at least 30 days of data
        today = timezone.now().date()
        earliest_transaction = Transaction.objects.order_by("date").first()

        if earliest_transaction:
            days_of_data = (today - earliest_transaction.date).days
            if days_of_data < 30:
                return render(request, "dashboard.html", {"error": "Not enough data available (Requires at least 30 days of transactions)."})

        
        ### GRAPHS SECTION ###
        #graph 1: trend line graph
        trend_graph = trend_line_graph(n, time_unit)
        # Graph 2: Expense by Category (Pie Chart)
        pie_chart = expense_category_pie_chart(n, time_unit)
        # Graph 3: Income vs Expense Bar Chart
        income_expense_chart = income_vs_expense_bar_chart(n, time_unit)
        # Graph 4: Top 5 Expenses Donut Chart
        top_expenses_chart = top_5_expenses_donut_chart(n, time_unit)

        
        ### RECENT TRANSACTION SECTION ###
        # Fetch recent 7 transactions (ordered by date descending)
        recent_transactions = Transaction.objects.order_by("-date")[:7]

        return render(request, "dashboard.html", {
            "estimate_data": estimate_data,
            "trend_graph": trend_graph,
            "pie_chart": pie_chart,
            "income_expense_chart": income_expense_chart,
            "top_expenses_chart": top_expenses_chart,
            "recent_transactions": recent_transactions,
            "budget_data": budget_data,
            "monthly_budget": monthly_budget_target,
        })

    def post(self, request):

        ### ESTIMATE SECTION
        estimate_data = estimate_section()

        ### MONTHLY BUDGET SECTION ###
        monthly_budget_target = 16000  # This will later come from the database
        budget_data = monthly_budget_visualization(monthly_budget_target)

        n = int(request.POST.get("n", 30))  # 30 days default
        time_unit = request.POST.get("unit", "days")  # 30 days default

        print(f"{n} {time_unit}")

        # Graph 1: Trend Line Graph
        trend_graph = trend_line_graph(n, time_unit)

        # Graph 2: Expense by Category (Pie Chart)
        pie_chart = expense_category_pie_chart(n, time_unit)

        # Graph 3: Income vs Expense Bar Chart
        income_expense_chart = income_vs_expense_bar_chart(n, time_unit)

        # Graph 4: Top 5 Expenses Donut Chart
        top_expenses_chart = top_5_expenses_donut_chart(n, time_unit)

        # Recent 7 transactions
        recent_transactions = Transaction.objects.order_by("-date")[:7]

        return render(request, "dashboard.html", {
            "estimate_data": estimate_data,
            "trend_graph": trend_graph,
            "pie_chart": pie_chart,
            "income_expense_chart": income_expense_chart,
            "top_expenses_chart": top_expenses_chart,
             "recent_transactions": recent_transactions,
             "budget_data": budget_data,
             "monthly_budget": monthly_budget_target,
        })


class addStatements(View):
    def get(self, request):
        print("test")
        return render(request, "addStatements.html")

    def post(self, request):
        print("test2")

        if 'csvFile' not in request.FILES:
            return render(request, "addStatements.html", {"error": "No file uploaded"})
        
        # Get .csv file
        csv_file = request.FILES['csvFile']
        print(csv_file.name)  # Print filename
        print(csv_file.content_type)  # Check MIME type


        csv_file.seek(0)
        # Process the user uploaded bank statement 
        clean_bank_statements(csv_file)

        # Path to the updated CSV file in the artifact folder
        updated_csv_path = os.path.join(settings.BASE_DIR,'app','artifacts','updated_transaction.csv')

        # Read the updated CSV file and store data in the database
        try:
            # with open(updated_csv_path, mode='r') as file:
            #     csv_reader = csv.DictReader(file)
            #     for row in csv_reader:
            #         # Create a Transaction object for each row
            #         Transaction.objects.create(
            #             date=row['Date'],
            #             balance_amount=row['Balance Amount'],
            #             transaction_amount=row['Transaction_Amount'],
            #             type=row['Type'],
            #             recipient=row['Recipient'],
            #             category=row['Category']
            #         )
                    # Success message
            return redirect("dashboard")
        
        except Exception as e:
            # Handle errors (e.g., invalid CSV format or file not found)
            return render(request, "addStatements.html", {"error": f"Error processing CSV file: {str(e)}"})
        

class AddTransaction(View):
    def get(self, request):
        return render(request, "addTransaction.html")
    
    def post(self, request):
        return redirect("dashboard")

