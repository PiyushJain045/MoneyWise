# Stage 1 imports
import pandas as pd
import os
from django.conf import settings
from io import StringIO  # For handling file-like objects

# Stage 2 imports
import os
from dotenv import load_dotenv
load_dotenv() 
# Setup GEMINI API
import google.generativeai as genai


# Prompt that is passed to Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")


# Stage 1: RAW bank transaction csv cleaning
def clean_bank_statements(csv_file):
    print("INSIDE UTILS")

    # Decode the file content into a string
    file_content = csv_file.read().decode('utf-8')
    
    # Use StringIO to create a file-like object
    file_like_object = StringIO(file_content)

    # create a dataframe
    df = pd.read_csv(file_like_object, skiprows=7, skipfooter=1, engine='python')
    print("DATA:", df.head())
    print("Column Names:", df.columns)

    # fill credit + debit missing values because in a boi bank statement they are the only empty fileld
    df.fillna(0, inplace=True)
    

    # Combine 'Debit' + 'Credit' to create a new column 'Transaction_Amount'
    df['Transaction_Amount'] = df['Debit'] + df['Credit']

    # Create a new column 'Type' --> Credit(CR) or Debit(DR)
    df['Type'] = df.apply(lambda row: 'DR' if row['Debit'] > 0 else 'CR', axis=1)

    # drop unnecessary columns
    df.drop(columns=['Sr No', 'Debit', 'Credit'], inplace=True)

    # Create a 'Recipient' column using 'Remarks'
    df['Recipient'] = df['Remarks'].str.split('/').str[3]
    # drop 'Remarks'
    df.drop(columns=['Remarks'], inplace=True)

    # Correct the dtype of 'Date'
    df['Date'] = pd.to_datetime(df['Date'], format='%d-%m-%Y')

    # 'Recepient' might have some NULL values --> fill with Unknown
    df['Recipient'].fillna('Unknown', inplace=True)
    # 'Receipient' might also have some empty string values
    df['Recipient'] = df['Recipient'].replace('', 'Unknown')  # Convert blanks to NULL

    # Stored cleaned .csv file in artifacts folder
    artifacts_folder = os.path.join(settings.BASE_DIR, 'app', 'artifacts')
    os.makedirs(artifacts_folder, exist_ok=True)
    
    output_file_path = os.path.join(artifacts_folder, 'cleaned_transaction.csv')
    df.to_csv(output_file_path, index=False)

    print(f"Cleaned data saved to: {output_file_path}")

    # Add categories using Gemini
    updated_file_path = add_category(output_file_path, artifacts_folder)
    print(f"Updated data saved to: {updated_file_path}")

    return

#Stage 2: Gemini adds the 'category' column to Stage 1 output
def add_category(file_path, artifacts_folder):
    try:
        print("Inside add_categories")
        # Load the CSV file
        df = pd.read_csv(file_path)

        # Create a prompt for Gemini
        prompt = """
        I am using you in my ai finance management project. Based on the 'Recipient' column in the following CSV data, categorize each transaction into one of these categories:
        - Food & Dining
        - Transport
        - Shopping
        - Entertainment
        - Banking & Transfers
        - Utilities & Bills
        - Health & Fitness
        - Education
        - Rent & Housing
        - Friend/Family
        - Other

        CONCATINATE this categories with the original CSV file and return the UPDATED csv. 

        Here is the data:
        """ + df.to_csv(index=False)

        # Send the prompt to Gemini
        response = model.generate_content(prompt)
        print("****************************************************************************************************")
        print("****************************************************************************************************")
        print("RESPONSE", response)
        print("RESPONSE", response.candidates[0].content.parts[0].text)

        # Extract the response (assuming it returns a CSV with a 'Category' column)
        updated_csv = response.candidates[0].content.parts[0].text

        # Convert the response to a DataFrame
        updated_df = pd.read_csv(StringIO(updated_csv.strip().strip("```csv").strip()))
        print("****************************************************************************************************")
        print("****************************************************************************************************")
        print(updated_df.head())

        # Save the updated DataFrame to a new CSV file
        updated_file_path = os.path.join(artifacts_folder, 'updated_transaction.csv')
        updated_df.to_csv(updated_file_path, index=False)

        print(f"Updated data saved to: {updated_file_path}")
        return updated_file_path

    except Exception as e:
        message = f"{e} Error occurred with Gemini"
        print(message)
        return message

    

