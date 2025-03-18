from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.views import View
from .models import Transaction 


#Misslaneous
import csv
import os
from django.conf import settings
from datetime import datetime
import base64
import json

#Graphs and visualization
from django.utils import timezone


#Utils functions
from .utils.data_processing import clean_bank_statements  # Import CSV processing
from .utils.visualization import (
    trend_line_graph, expense_category_pie_chart,
    income_vs_expense_bar_chart, top_5_expenses_donut_chart, 
    monthly_budget_visualization, estimate_section
)  
from .utils.generate_financial_report import generate_financial_report

# Imports for Environment Variable
import os
from dotenv import load_dotenv
load_dotenv() 
# Setup GEMINI API
import google.generativeai as genai
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash") 


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
         print("INSIDE GET addTran")

         return render(request, "addTransaction.html")
    
    def post(self, request):
          print("INSIDE ADDtran POST")
          date = request.POST.get('date')
          transaction_amount = request.POST.get('transaction_amount')
          transaction_type = request.POST.get('type')
          recipient = request.POST.get('recipient')
          category = request.POST.get('category')
          print(date, transaction_amount, type, recipient, category)

          # Convert date string to DateField format
          date = datetime.strptime(date, "%Y-%m-%d").date()

          # Convert transaction_amount to float
          transaction_amount = float(transaction_amount)

          # Get latest balance (from the last transaction)
          last_transaction = Transaction.objects.order_by("-date").first()
          last_balance = last_transaction.balance_amount if last_transaction else 0.0

          # Update balance based on transaction type
          if transaction_type == "CR":
                new_balance = float(last_balance) + transaction_amount
          else:  # DR (Debit)
                new_balance = float(last_balance) - transaction_amount

            # Create and save transaction
          Transaction.objects.create(
                date=date,
                balance_amount=new_balance,
                transaction_amount=transaction_amount,
                type=transaction_type,
                recipient=recipient,
                category=category
            )
          print("Transaction added successfully.")
          return redirect("dashboard")
     
    
     

class FinancialReport(View):
    def get(self, request):
        report = generate_financial_report()
        # print(report)  # Debugging: Print report to check content

        prompt = f'''You are being used in a personal finance management app. Here is the financial report of a user:  
        {report}  

        Based on this, provide financial advice in a friendly manner. Use point format and keep it minimal.  
        If the user is financially stable, mention the 'Stock Tracking' feature.'''  

        try:
            # Ask Gemini for Advice
            response = model.generate_content(prompt)
            print("RESPONSE:", response)

            advice = response.candidates[0].content.parts[0].text
            print("Extracted Text:", advice)
            
        except Exception as e:
            advice = f"Error fetching AI advice: {e}"

        # print("RESPONSE:", advice)  # Debugging: Print AI response

        # ✅ Fix: Format report with line breaks and bold styling
        formatted_report = report.replace("\n", "<br>")  # Convert newlines to HTML <br>

        # ✅ Fix: Format AI advice as bullet points
        formatted_advice = advice.replace("* ", "<li>").replace("\n", "</li>") + "</li>"

        return render(request, "financialReport.html", {"report": formatted_report, "advice": formatted_advice})

    def post(self, request):
        pass


class AiReceipt(View):
    def get(self,request):
        pass

    def post(self,request):
        print("INSIDE AI RECEIPT POST")
        try:
            # Get the uploaded file
            receipt_file = request.FILES.get("receiptImage")

            if not receipt_file:
                return JsonResponse({"error": "No file uploaded."}, status=400)
            
            # ✅ Read file content & encode as Base64
            file_content = receipt_file.read()
            encoded_image = base64.b64encode(file_content).decode("utf-8")

                        # ✅ Determine MIME Type
            file_type = receipt_file.content_type
            if file_type == "image/png":
                mime_type = "image/png"
            elif file_type == "image/jpeg":
                mime_type = "image/jpeg"
            else:
                return render(request, "addTransaction.html", {"error": "Unsupported file format. Please upload PNG or JPG."})

             # ✅ Prepare Gemini API request
            prompt = """
            You are an AI assistant in a personal finance app. 
            The user uploaded a receipt image. Extract the following details:
            - Date of transaction(YYYY-MM-DD format)
            - Transaction amount (₹)
            - Transaction type (CR/DR)
            - Recipient name
            - Category (Food & Dining, Transport, Shopping, Entertainment, Banking & Transfers, Utilities & Bills
            ,Health & Fitness, Education, Rent & Housing, Friend/Family, Other)
            
            Return only a JSON object with keys: date, transaction_amount, type, recipient, category.
            """

            # ✅ Send Image + Text Prompt to Gemini 1.5 Flash
            response = model.generate_content([prompt, {"mime_type": mime_type, "data": encoded_image}])
            bill = response.candidates[0].content.parts[0].text
            # Remove the ```json and ``` markers
            json_str = bill.strip('```json\n').strip('```')
            # Parse the JSON string into a Python dictionary
            extracted_data = json.loads(json_str)
            print("Extracted JSON Data:", extracted_data)

            return render(request, "addTransaction.html", extracted_data)
    
        except Exception as e:
            return render(request, "addTransaction.html", {"error": f"Error processing receipt: {e}"})
    



    