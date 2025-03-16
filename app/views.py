from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views import View
from .models import Transaction 

#Misslaneous
import csv
import os
from django.conf import settings

#Graphs and visualization


#Utils functions
from .utils.data_processing import clean_bank_statements  # Import CSV processing
# from .utils.visualization import generate_expense_pie_chart  # Import graph function

# Imports for Environment Variable
import os
from dotenv import load_dotenv
load_dotenv() 


# Create your views here.
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
            return render(request, "dashboard.html", {"success": "File uploaded and processed successfully"})
        
        except Exception as e:
            # Handle errors (e.g., invalid CSV format or file not found)
            return render(request, "addStatements.html", {"error": f"Error processing CSV file: {str(e)}"})

