import requests
import json
from datetime import datetime


def detect_anomaly(data):
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
    

data = {
    "balance_amount": 6355.16,
    "date": "2025-03-25",
    "transaction_amount": 4000,
    "transaction_type": "CR",
    "recipient": "RELIANCE SMART BAZAAR",
    "category": "Food & Dining"
}

data = {'balance_amount': 8297.28, 'date': '2025-03-15', 'transaction_amount': '57.88', 'transaction_type': 'DR', 'recipient': 'Reliance Smart Bazaar', 'category': 'Food & Dining'}  
detect_anomaly(data)