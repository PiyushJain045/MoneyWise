# bentoml serve service.py:scv --reload
import pandas as pd
import bentoml
from bentoml.io import JSON
from datetime import datetime
import pickle
from typing import Dict, Any

# Load components
model_ref = bentoml.sklearn.get("anomaly_detector:latest")
model_runner = model_ref.to_runner()

# Load label encoders
with open("D:\\MY WORKSPACE\\Project Competition\\save_N_spend\\app\\artifacts\\anomaly_detection_model.pkl", 'rb') as f:
    label_encoders = pickle.load(f)['label_encoders']

# Create service
svc = bentoml.Service("anomaly_detection_service", runners=[model_runner])

@svc.api(input=JSON(), output=JSON())
def detect_anomaly(input_series: Dict[str, Any]) -> Dict[str, Any]:
    """Detect transaction anomalies (synchronous version)"""
    
    # Prepare features
    transaction_date = datetime.strptime(input_series['date'], '%Y-%m-%d')
    
    features = {
        'Balance Amount': float(input_series['balance_amount']),
        'Transaction_Amount': float(input_series['transaction_amount']),
        'Type': input_series['transaction_type'],
        'day_of_week': transaction_date.weekday(),
        'day_of_month': transaction_date.day,
        'month': transaction_date.month,
        'Recipient': input_series['recipient'],
        'Category': input_series['category']
    }
    
    # Encode categorical features
    for col in ['Type', 'Recipient', 'Category']:
        le = label_encoders[col]
        try:
            features[col] = le.transform([features[col]])[0]
        except ValueError:
            features[col] = le.transform(['unknown'])[0]
    
    # Predict
    features_df = pd.DataFrame([features])
    anomaly_score = model_runner.predict.run(features_df)[0]
    
    return {
        'is_anomaly': bool(anomaly_score == -1),
        'anomaly_score': float(anomaly_score)
    }