from django.shortcuts import render, redirect, HttpResponse
from django.http import JsonResponse
from django.views import View
from .models import Transaction, Profile, UserAccount, MonthlyBudget, RecurringPayment, AnomalousTransaction, Portfolio
from django.contrib import messages
from django.conf import settings

#Misslaneous
import os
from datetime import datetime
import datetime
import base64
import json
import csv
import numpy as np
import pandas as pd
from collections import defaultdict
from decimal import Decimal

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
from .utils.anamoly import detect_anomaly

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
        user_name = request.user
        print(user_name)
        return render(request, "home.html",{"username":user_name})

    def post(self, request):
        pass


class Dashboard(View):
    def get(self, request):
        print("Inside GET dashboard")

        ### Current balance
        latest_transaction = Transaction.objects.order_by("-id").first()
        current_balance = latest_transaction.balance_amount if latest_transaction else 0

        ### ACCOUNT DATA
        user_account = UserAccount.objects.filter(user=request.user).first()

        if user_account:
            account_name = user_account.account_name
            account_type = user_account.account_type
            # current_balance = user_account.current_balance
        else:
            account_name = "No Account Found"
            account_type = "N/A"
            # current_balance = "N/A"

        ### ESTIMATE SECTION
        estimate_data = estimate_section()

        ### MONTHLY BUDGET SECTION ###
        try:
            budget = MonthlyBudget.objects.get(user=request.user)
            monthly_budget_target = budget.monthly_budget # This will later come from the database
            print("monthly_budget_target", monthly_budget_target)
        except MonthlyBudget.DoesNotExist:
            monthly_budget_target = 0  # Default value if no budget is found
            print("No budget found for the user. Setting default to ₹0.")


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
            "account_name": account_name,
            "account_type": account_type,
            "balance": current_balance
        })

    def post(self, request):

        ### Current balance
        latest_transaction = Transaction.objects.order_by("-id").first()
        current_balance = latest_transaction.balance_amount if latest_transaction else 0

        ### ACCOUNT DATA
        user_account = UserAccount.objects.filter(user=request.user).first()

        if user_account:
            account_name = user_account.account_name
            account_type = user_account.account_type
        else:
            account_name = "No Account Found"
            account_type = "N/A"

        print("Account Name:", account_name)
        print("Account Type:", account_type)

        ### ESTIMATE SECTION
        estimate_data = estimate_section()

        ### MONTHLY BUDGET SECTION ###
        try:
            budget = MonthlyBudget.objects.get(user=request.user)
            monthly_budget_target = budget.monthly_budget # This will later come from the database
            print("monthly_budget_target", monthly_budget_target)
        except MonthlyBudget.DoesNotExist:
            monthly_budget_target = 0  # Default value if no budget is found
            print("No budget found for the user. Setting default to ₹0.")
        
        budget_data = monthly_budget_visualization(monthly_budget_target)

        # Generate the trend line graph 
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
             "account_name": account_name,
            "account_type": account_type,
            "balance": current_balance
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
            with open(updated_csv_path, mode='r') as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    # Create a Transaction object for each row
                    Transaction.objects.create(
                        date=row['Date'],
                        balance_amount=row['Balance Amount'],
                        transaction_amount=row['Transaction_Amount'],
                        type=row['Type'],
                        recipient=row['Recipient'],
                        category=row['Category']
                    )
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
          print(date, transaction_amount, transaction_type, recipient, category)

          latest_transaction = Transaction.objects.order_by("-id").first()
          current_balance = latest_transaction.balance_amount if latest_transaction else 0

          # numpy array
          print("BEFORE")
          data = {
                "balance_amount": float(current_balance),
                "date": date,
                "transaction_amount": transaction_amount,
                "transaction_type": transaction_type,
                "recipient": recipient,
                "category": category,
            }
          
          print("/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////")
          result = detect_anomaly(data)
          print("Anomaly Detection Result:")
          print(f"Is Anomaly: {result['is_anomaly']}")
          print(f"Anomaly Score: {result['anomaly_score']:.4f}")

          if result['is_anomaly']:
            # Store in AnomalousTransaction model
            print("INSIDE IF")
            AnomalousTransaction.objects.create(
                balance_amount=data['balance_amount'],
                date=data['date'],
                transaction_amount=data['transaction_amount'],
                transaction_type=data['transaction_type'],
                recipient=data['recipient'],
                category=data['category'],
                anomaly_score=result['anomaly_score']
            )

          # Convert date string to DateField format
          date = datetime.strptime(date, "%Y-%m-%d").date()

          # Convert transaction_amount to float
          transaction_amount = float(transaction_amount)

          # Get latest balance (from the last transaction)

          last_transaction = Transaction.objects.order_by("-id").first()
          last_balance = last_transaction.balance_amount if last_transaction else 0

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

        user = request.user 
        report = generate_financial_report(user)
        # print(report)  # Debugging: Print report to check content

        prompt = f'''   
                    You are a financial advisor in a personal finance app. Analyze the user's financial report below and provide concise, actionable advice.  

                    **User Report:**  
                    {report}  

                    **Guidelines:**  
                    1. Consider age, country, and profession for tailored advice.   
                    3. Skip markdown—use plain text with a line break after each point.  
                    4. If savings exist, suggest investment options based on the saved amount.  
                    5. Recommend the app’s *Stock Tracking* feature if relevant.  
                    6. Keep advice strictly based on the report—no assumptions. 
                    7. Also include few emojis '''  

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
        # Split advice by newlines and convert to HTML list
        advice_points = [point.strip() for point in advice.split('\n') if point.strip()]
        formatted_advice = "<ul>" + "".join(f"<li>{point}</li>" for point in advice_points) + "</ul>"

        return render(request, "financialReport.html", {"report": formatted_report, "advice": formatted_advice})

    def post(self, request):
        print("INSIDE AI POST")

        report = generate_financial_report(request.user)

        user_message = request.POST.get('user_message', '')
        print(user_message)

        prompt = f'''**Context:**
                    You are a friendly financial assistant in a Finance Management web app. The user has just received their financial report and initial advice, but may still have questions or need clarification.

                    **User's Financial Report:**
                    {report}

                    **Your Role:**
                    1. Maintain a conversational, friendly tone - act as a helpful financial friend
                    2. Keep responses concise (5-6 sentences maximum unless complex questions require more)
                    3. Remember previous chat history for context
                    4. Focus on being practical and actionable
                    5. When appropriate, reference specific parts of their report

                    **Current User Message:**
                    "{user_message}"

                    **Response Guidelines:**
                    - Acknowledge their question/concern
                    - Provide clear, specific advice
                    - Use simple financial terms (explain if needed)
                    - Offer encouragement when appropriate
                    - Suggest next steps if relevant

                    **Example Good Response:**
                    "I see you're concerned about your savings. Based on your report, you're doing well with expenses but could boost savings by 15%. Let's look at three easy 
                    ways to do this..."'''
    
        response = model.generate_content(prompt)
        print("RESPONSE:", response)

        ai_response = response.candidates[0].content.parts[0].text
        print("Extracted Text:", ai_response)
        
        # Return the response as HTML that HTMX will insert
        return HttpResponse(f'<div class="message bot-message">{ai_response}</div>')


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
    

class ProfileSection(View):
    def get(self, request):

        print("INSIDE PROFILE GET")

        # Fetch Profile Data
        profile = Profile.objects.filter(user=request.user).first()
        user_profile = {
            "name": profile.name if profile else "N/A",
            "age": profile.age if profile else "N/A",
            "email": profile.user.email if profile else "N/A",
            "phone": profile.phone if profile else "N/A",
            "profession": profile.profession if profile else "N/A",
            "profile_photo": profile.profile_photo.url if profile and profile.profile_photo else None,
        }

        # Fetch UserAccount Data
        user_account = UserAccount.objects.filter(user=request.user).first()
        account_data = {
            "account_name": user_account.account_name if user_account else "N/A",
            "account_type": user_account.account_type if user_account else "N/A",
            "current_balance": user_account.current_balance if user_account else 0.00,
        }

        # Fetch Monthly Budget Data
        monthly_budget = MonthlyBudget.objects.filter(user=request.user).first()
        budget_data = {
            "monthly_budget": monthly_budget.monthly_budget if monthly_budget else 0.00,
        }

        # Combine data into context
        context = {
            "user_profile": user_profile,
            "account_data": account_data,
            "budget_data": budget_data,
        }

        return render(request, "profile.html", context)
    
    def post(self, request):
        print("INSIDE PROFILE POST")

        # Parse incoming JSON data
        try:
            user_profile = Profile.objects.get(user=request.user)
            account_data = UserAccount.objects.get(user=request.user)
            budget_data = MonthlyBudget.objects.get(user=request.user)


            # ✅ Prepare context for the partial
            context = {
                "user_profile": user_profile,
                "account_data": account_data,
                "budget_data": budget_data,
            }
           
            
            print("Received Data:", context)
            return render(request, "partials\edit_profile_partial.html",context)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)


def OnBoarding(request):
    if request.method == "GET":
        return render(request, "onBoarding.html")
    
    if request.method == "POST":
        print("INSIDE ONBOARDING POST")
        print("Form Data:", request.POST)

        name = request.POST.get("name")
        age = int(request.POST.get("age"))
        print("Age:", age)
        phone = request.POST.get("phone")
        profession = request.POST.get("profession")
        account_name = request.POST.get("account_name")
        account_type = request.POST.get("account_type")
        current_balance = request.POST.get("current_balance")
        monthly_budget = request.POST.get("monthly_budget")
        profile_photo = request.FILES.get("profile_photo")  # ✅ Handle Image Upload

        # ✅ Step 2: Save Profile Data
        profile, created = Profile.objects.get_or_create(user=request.user)
        profile.name = name
        profile.age = age
        profile.phone = phone
        profile.profession = profession
        if profile_photo:
            profile.profile_photo = profile_photo
        profile.save()

        # ✅ Step 3: Save or Update UserAccount Data
        account, created = UserAccount.objects.get_or_create(user=request.user)
        account.account_name = account_name
        account.account_type = account_type
        account.current_balance = current_balance
        account.save()

        # ✅ Step 4 : Save or Update Monthly Budget
        budget, created = MonthlyBudget.objects.get_or_create(user=request.user)
        budget.monthly_budget = monthly_budget
        budget.save()

        print("Data stored successfully")
        messages.success(request, "Onboarding completed successfully!")
        return redirect('home')
    

class RecurringPayments(View):
    def get(self, request):
        print("INSIDE RECURRING GET")
        user = request.user  # Get the logged-in user
        recurring_payments = RecurringPayment.objects.filter(user=user)  # Fetch user's recurring payments

        if not recurring_payments.exists():
            message = "No recurring payments"
            return render(request, "recurrning.html", {"message": message})

        return render(request, "recurrning.html", {"recurring_payments": recurring_payments})

    def post(self, request):
        print("INSIDE RECURRING POST")
        name = request.POST.get("name")
        amount = request.POST.get("amount")
        category = request.POST.get("category")
        payment_type = request.POST.get("type")  # DR (Debit) or CR (Credit)
        date = request.POST.get("date")

        print(name, amount, category, payment_type, date)

        RecurringPayment.objects.create(
            user=request.user,  # Associate with logged-in user
            name=name,
            amount=amount,
            category=category,
            type=payment_type,
            date=date
        )

        print("Recurring payment saved successfully!")

        return redirect('recurring')
    

class Security(View):
    def get(self, request):
        anomalies = AnomalousTransaction.objects.filter(reviewed=False).order_by('-date')
        context = {'anomalies': anomalies}
        return render(request, 'security.html', context)

    def post(self, request):
        print("INSIDE ANOMALY POST")
        transaction_id = request.POST.get('transaction_id')
        action = request.POST.get('action')

        if action == 'confirm':
            try:
                anomaly = AnomalousTransaction.objects.get(id=transaction_id)
                anomaly.reviewed = True
                anomaly.save()
                return redirect('security')
            except Exception as e:
                return redirect('security')

        if action == 'reject':
            anomalies = AnomalousTransaction.objects.filter(reviewed=False).order_by('-date')
            return render(
                request,
                'security.html',
                {
                    "anomalies": anomalies,
                    "warning": "Report Anomaly immediately to your Branch or Call on Toll-Free No. 1800 103 1906"
                }
            )        
       

class Investments(View):
    def get(self, request):

        color_map = {
            "Stocks": "#1E90FF",         # Blue
            "Real Estate": "#FFA500",    # Orange
            "Bonds": "#8A2BE2",          # Purple
            "Crypto": "#FF69B4",         # Pink
            "Mutual Funds": "green",   # Turquoise
            "Gold": "#FFD700",           # Gold
            "Other": "#A9A9A9"           # Default Gray
        }


        user = request.user
        print("USER:", user)
        portfolios = Portfolio.objects.filter(user=user)
        total_value = Portfolio.get_total_portfolio_value(user)

        # Group values by investment type
        allocation_data = defaultdict(float)
        for item in portfolios:
            allocation_data[item.investment_type] += float(item.amount)  # corrected from current_value

        # Prepare chart data
        labels = []
        values = []
        formatted_data = []

        for inv_type, value in allocation_data.items():
            percent = round((float(value) / float(total_value)) * 100, 1) if total_value else 0

            labels.append(inv_type)
            values.append(value)
            formatted_data.append({
                'label': inv_type,
                'value': value,
                'percent': percent,
                'formatted_value': f"₹{value:,.0f}"
            })
            print("************", formatted_data)

        colors = [color_map.get(label, "#CCCCCC") for label in labels]

        context = {
            'total_value': total_value,
            'labels': labels,
            'values': values,
            'formatted_data': formatted_data,
            'has_data': bool(formatted_data),
            "colors": json.dumps(colors),
        }
        print("Context", context)

        return render(request, 'investments.html', context)
    
    def post(self, request):
        print("INSIDE POST")

        if request.FILES.get("statement_file"):
            print("INSIDE FILES")
            statement_type = request.POST.get("statement_type")
            broker = request.POST.get("broker")
            file = request.FILES["statement_file"]
            user = request.user

            print("FILE:", file)

            df = pd.read_excel(file, header=None)

            print(df.head())

            # Extract data based on statement type
            invested_value = 0
            unrealised_pnl = 0

            try:
                if statement_type == "Stocks":
                    for index, row in df.iterrows():
                        if pd.notna(row[0]):  # Check if cell is not empty
                            if 'Invested Value' in str(row[0]):
                                invested_value = Decimal(str(row[1]))
                                print(invested_value)
                            elif 'Unrealised P&L' in str(row[0]):
                                unrealised_pnl = Decimal(str(row[1]))
                                print(unrealised_pnl)

                elif statement_type == "Mutual Funds":
                    for index, row in df.iterrows():
                        if pd.notna(row[0]):
                             if 'Total Investments' in str(row[0]) and 'Current Portfolio Value' in str(row[1]):
                                 
                                 # The values are in the next row
                                values_row = df.iloc[index + 1]
                                invested_value = Decimal(str(values_row[0]))  # Total Investments column
                                print(invested_value)
                                current_value = Decimal(str(values_row[1]))  # Current Portfolio Value column
                                unrealised_pnl = Decimal(str(values_row[2]))  # Profit/Loss column
                                break
                    
                # Add more elifs as needed for other statement types

            except Exception as e:
                print("Error parsing Excel:", e)
                return redirect("investment")
            
            Portfolio.objects.create(
                user=user,
                investment_type=statement_type,
                amount=invested_value,
                date= datetime.date.today() # You can make this optional in your model or add logic to extract from file
            )

# ****************************
        else:
            type = request.POST.get("investment_type")
            amount= request.POST.get("amount")
            date = request.POST.get("date")

            Portfolio.objects.create(
                user = request.user,
                investment_type = type,
                amount = amount,
                date = date
            )

        
        return redirect("investment")


class Learn(View):
    def get(self, request):
        return render(request, "learn.html")

