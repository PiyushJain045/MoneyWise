import bentoml
import pickle

# Load the existing model and encoders
with open("D:\\MY WORKSPACE\\Project Competition\\save_N_spend\\app\\artifacts\\anomaly_detection_model.pkl", 'rb') as f:
    saved_data = pickle.load(f)

# Save the model
saved_model = bentoml.sklearn.save_model(
    "anomaly_detector", 
    saved_data['model'],
    labels={"owner": "your-team"}
)

# Save label encoders (corrected approach)
bentoml.picklable_model.save(
    "label_encoders",
    saved_data['label_encoders'],
    labels={"owner": "your-team"}
)

print(f"Model saved: {saved_model}")