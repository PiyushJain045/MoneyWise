# [Money Wise](https://moneywise-ndld.onrender.com/)

## Overview  
A Django-based personal finance management system with comprehensive tracking, reporting, and AI-powered features.

## Features  

### 📊 Dashboard  
- Real-time balance & account overview  
- Interactive visualizations:  
  - Transaction trends  
  - Expense categorization  
  - Income vs. expense analysis  
  - Top expense tracking  

### 💳 Transaction Management  
- CSV bank statement imports  
- Manual transaction entry  
- AI receipt scanning (Gemini API)  
- Anomaly detection system  

### 📈 Financial Reporting  
- Automated report generation  
- AI financial advisor chat  
- Personalized recommendations  

### 👤 User Profile  
- Personal & account management  
- Monthly budget configuration  
- Profile photo upload  

### 🔄 Recurring Payments  
- Scheduled transaction tracking  
- Payment calendar view  

### 🛡️ Security Center  
- Anomaly review dashboard  
- Fraud reporting interface  

### 📈 Investment Tracking  
- Portfolio valuation  
- Asset allocation visualization  
- Broker statement imports  

### 🎓 Learning Resources  
- Financial education materials  

## Tech Stack  
| Component          | Technology           |
|--------------------|----------------------|
| Backend            | Django               |
| Database           | SQLite (configurable)|
| AI Integration     | Gemini API           |
| Visualization      | Custom JS/CSS        |
| Anomaly Detection  | Custom algorithm     |

## Installation  

```bash
# Clone repository
git clone https://github.com/PiyushJain045/MoneyWise.git

# Setup virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
echo "GEMINI_API_KEY=Add your gemini-1.5-flash API key here" > .env

# Initialize database
python manage.py migrate
python manage.py createsuperuser

# Launch development server
python manage.py runserver
