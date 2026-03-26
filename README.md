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
```

### Screenshots

<img width="1920" height="1080" alt="Screenshot 2026-03-26 194009" src="https://github.com/user-attachments/assets/9ea29c11-ecf2-4533-8051-538b01c67349" />

<img width="1920" height="1080" alt="Screenshot 2026-03-26 194313" src="https://github.com/user-attachments/assets/d2dd04c4-46df-4108-afa0-3fd23c39663c" />

<img width="1920" height="1080" alt="Screenshot 2026-03-26 194043" src="https://github.com/user-attachments/assets/774509da-adce-4c5d-9c9c-0010abaa56eb" />

<img width="1920" height="1080" alt="Screenshot 2026-03-26 194120" src="https://github.com/user-attachments/assets/ff819936-6e90-4e86-a06f-cff46f8a8ca1" />

<img width="1920" height="1080" alt="Screenshot 2026-03-26 194246" src="https://github.com/user-attachments/assets/e48c2251-ed6c-4afa-b666-aabfd67610e3" />

<img width="1920" height="1080" alt="Screenshot 2026-03-26 194603" src="https://github.com/user-attachments/assets/1435d467-fd44-4f34-847a-0368e71e10de" />

<img width="1920" height="1080" alt="Screenshot 2026-03-26 194620" src="https://github.com/user-attachments/assets/af7cd337-2092-41ea-a0c6-bd5326f10fe1" />

<img width="1920" height="1080" alt="Screenshot 2026-03-26 194636" src="https://github.com/user-attachments/assets/3af07e12-5775-477e-a945-765f9a322de4" />

<img width="1920" height="1080" alt="Screenshot 2026-03-26 194513" src="https://github.com/user-attachments/assets/97a64081-f405-4a5d-8bde-053b53f9b993" />







