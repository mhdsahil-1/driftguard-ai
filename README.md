# DriftGuard AI

**PayPal Sandbox Checkout & Experimental Transaction Risk Intelligence**

DriftGuard AI is a prototype exploring how experimental AI-based transaction risk analysis and temporal drift monitoring could complement a PayPal-powered checkout workflow.

> **Disclaimer:** This is an independent experimental project. It is not affiliated with or endorsed by PayPal. Its risk scores are not official PayPal fraud assessments, and the model has not been trained on PayPal transaction data.

## Problem

Transaction patterns can change over time, potentially reducing the reliability of fraud-detection models. This project explores transaction risk scoring, model evaluation on time-separated data, and a payment workflow using PayPal Sandbox.

## Planned and Implemented Features

- FastAPI backend
- PayPal Sandbox authentication
- Sandbox order creation
- Experimental rule-based risk-scoring endpoint
- Random Forest baseline trained on the synthetic PaySim dataset
- Checkout interface and temporal drift monitoring — planned

Feature status will be updated as implementation and testing are completed.

## Technology Stack

- Python 3.12
- FastAPI and Uvicorn
- scikit-learn, pandas, NumPy and joblib
- HTTPX and python-dotenv
- PayPal Developer Sandbox
- HTML, CSS and JavaScript for the checkout interface

## Dataset

The experimental baseline uses the PaySim synthetic mobile-money transaction dataset.

Dataset source: https://www.kaggle.com/datasets/ealaxi/paysim1

The dataset is not PayPal transaction data. Model results should not be interpreted as validated performance on real PayPal payments.

Download the dataset separately and place the CSV in `data/`. Do not commit the dataset or generated model files to this repository.

## Local Setup

### 1. Clone the repository

```bash
git clone <YOUR_PUBLIC_REPOSITORY_URL>
cd driftguard-ai
```

### 2. Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install fastapi "uvicorn[standard]" httpx python-dotenv pydantic pandas numpy scikit-learn joblib
```

### 4. Configure PayPal Sandbox

Create a `.env` file in the project root:

```dotenv
PAYPAL_CLIENT_ID=your_sandbox_client_id
PAYPAL_CLIENT_SECRET=your_sandbox_client_secret
PAYPAL_API_BASE=https://api-m.sandbox.paypal.com
```

Use Sandbox credentials only. Never commit `.env` or publish secrets.

### 5. Run the backend

```powershell
python -m uvicorn main:app --reload
```

Open the interactive API documentation at:

http://127.0.0.1:8000/docs

## API Endpoints

| Endpoint | Purpose |
|---|---|
| `GET /` | Project status |
| `GET /health` | Health check |
| `POST /risk/score` | Experimental rule-based risk score |
| `POST /paypal/create-order` | Create a PayPal Sandbox order |
| `POST /paypal/capture-order` | Capture an order after buyer approval |

Payment endpoints must be tested using valid Sandbox workflows. Do not submit real payments or use Live credentials.

## AI Evaluation and Limitations

The Random Forest baseline is trained on synthetic PaySim data. Its input features and labels are dataset-specific. A successful PayPal Sandbox order does not establish whether a transaction is legitimate.

Temporal robustness and drift monitoring must be evaluated separately and documented with reproducible metrics before being described as completed features.

## Tools Used

- PayPal Developer Sandbox
- Python and FastAPI
- scikit-learn and pandas
- Visual Studio Code
- Git and GitHub

## License

See [LICENSE](LICENSE).

## Demo

Demo URL: To be added after deployment and end-to-end testing.

Video demonstration: To be added after recording a public YouTube demo under three minutes.