# import pandas as pd
# import numpy as np
# from sklearn.ensemble import IsolationForest
# from sklearn.preprocessing import LabelEncoder
# import pickle
# from datetime import datetime

# def detect_anomaly(data):
#     """
#     Detect if a transaction is anomalous based on the trained model.
    
#     Args:
#         data: Dictionary containing transaction details
        
#     Returns:
#         dict: Contains anomaly flag and anomaly score
#     """

#     print("DAAAAAAAAAT", data)
#     # Load the model and encoders
#     with open("D:\\MY WORKSPACE\\Project Competition\\save_N_spend\\app\\artifacts\\anomaly_detection_model.pkl", 'rb') as f:
#         saved_data = pickle.load(f)
#         model = saved_data['model']
#         label_encoders = saved_data['label_encoders']
    
#     # Create a DataFrame from the input data
#     transaction_date = datetime.strptime(data['date'], '%Y-%m-%d')
    
#     # Prepare features
#     features_dict = {
#         'Balance Amount': data['balance_amount'],
#         'Transaction_Amount': data['transaction_amount'],
#         'Type': data['transaction_type'],
#         'day_of_week': transaction_date.weekday(),
#         'day_of_month': transaction_date.day,
#         'month': transaction_date.month,
#         'Recipient': data['recipient'],
#         'Category': data['category']
#     }
    
#     # Encode categorical features
#     for col in ['Type', 'Recipient', 'Category']:
#         le = label_encoders[col]
#         try:
#             features_dict[col] = le.transform([features_dict[col]])[0]
#         except ValueError:
#             # If category is unseen, treat as unknown
#             features_dict[col] = le.transform(['unknown'])[0]
    
#     # Convert to DataFrame
#     features_df = pd.DataFrame([features_dict])
    
#     # Predict anomaly
#     anomaly_score = model.decision_function(features_df)[0]
#     is_anomaly = model.predict(features_df)[0] == -1
    
#     return {
#         'is_anomaly': bool(is_anomaly),
#         'anomaly_score': float(anomaly_score)
#     }


### Using Bento ML
import requests
import json
from datetime import datetime


def detect_anomaly(data):
    print("INSIDE BENTO")
    """
    Detect if a transaction is anomalous by calling BentoML API
    
    Args:
        data: Dictionary containing transaction details
        
    Returns:
        dict: Contains anomaly flag and anomaly score
    """
    # Prepare the request data in the format your BentoML API expects
    api_data = {
        "balance_amount": float(data['balance_amount']),
        "date": data['date'],
        "transaction_amount": float(data['transaction_amount']),
        "transaction_type": data['transaction_type'],
        "recipient": data['recipient'],
        "category": data['category']
    }

    try:
        # Make request to BentoML API
        response = requests.post(
            "http://localhost:3000/detect_anomaly",
            headers={"Content-Type": "application/json"},
            data=json.dumps(api_data)
        )
        
        # Check for successful response
        response.raise_for_status()
        print(response.json())
        api_result = response.json()
        return {
            'is_anomaly': bool(api_result.get('is_anomaly', False)),
            'anomaly_score': float(api_result.get('anomaly_score', 0.0))
        }
        
    except requests.exceptions.RequestException as e:
        # Handle API call errors
        print(f"Error calling anomaly detection API: {e}")
        return {
            'is_anomaly': False,
            'anomaly_score': 0.0,
            'error': str(e)
        }
    


