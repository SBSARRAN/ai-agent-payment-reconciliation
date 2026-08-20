# AI Payment Reconciliation System

An AI-powered payment reconciliation system that automatically receives customer payment screenshots through WhatsApp, extracts transaction details using AI, matches them against the company's transaction statement, and displays matched payments on a Streamlit dashboard for accountant approval.

The project automates a repetitive accounting workflow while keeping the final approval with the accountant.

---

## Problem Statement

Customers often send UPI/payment screenshots through WhatsApp after making a payment.

The accountant then manually needs to:

- Check whether the image is actually a payment receipt
- Read the amount, UTR, transaction ID and payment date
- Search for the transaction in the company statement
- Verify whether the payment was received
- Record the reconciliation result

This project automates these steps using **Generative AI + LangGraph + WhatsApp automation**.

---

## System Workflow

```text
Customer
   ↓
WhatsApp
   ↓
Neonize
   ↓
Receipt Image Download
   ↓
LangGraph Workflow
   ↓
Payment Classification
   ↓
Receipt Data Extraction
   ↓
Pydantic Validation
   ↓
Transaction Statement
   ↓
Matching Engine
   ↓
MATCHED / NOT MATCHED
   ↓
Excel Reconciliation Report
   ↓
FastAPI
   ↓
Streamlit Dashboard
   ↓
Accountant Approval
```

---

## Key Features

### WhatsApp Integration

The system connects to WhatsApp using **Neonize**.

When a customer sends an image:

- The image message is automatically detected
- Non-image messages are ignored
- Duplicate events are ignored
- The image is downloaded locally
- Sender information is captured
- The image is automatically passed into the AI workflow

No manual receipt upload is required.

### AI Receipt Classification

Customers may send images other than payment receipts.

The first AI step determines whether the received image is actually related to a payment.

```text
Image
  ↓
AI Classifier
  ↓
Payment?
  ├── No  → Ignore
  └── Yes → Continue
```

This prevents unrelated WhatsApp images from entering the reconciliation process.

### AI Receipt Extraction

For valid payment receipts, the AI converts the screenshot into structured transaction data.

The system extracts fields such as:

```text
Amount
UTR
Transaction ID
Payment Date
Payment Time
Payment Status
Payer Name
Payee Name
Payment App
```

Example extracted data:

```json
{
  "amount": 1099,
  "utr": "075194213850",
  "transaction_id": "T2608201821267350770576",
  "payment_date": "2026-08-20",
  "payment_time": "18:21",
  "payment_status": "SUCCESS",
  "payee_name": "TCM TG 01",
  "payment_app": "PhonePe"
}
```

### Pydantic Validation

The AI response is validated using **Pydantic** before being used by the reconciliation system.

This converts the LLM output into a predictable structured `Receipt` object and reduces problems caused by inconsistent AI responses.

---

## LangGraph Workflow

**LangGraph** is used to orchestrate the AI workflow.

```text
START
  ↓
classify_node
  ↓
Payment?
 ├── NO → END
 │
 └── YES
       ↓
   extract_node
       ↓
load_statement_node
       ↓
    match_node
       ↓
      END
```

The nodes communicate using a shared `PaymentState`.

The state carries information such as:

```text
image_path
customer_name
phone_number
is_payment
receipt
transactions
matched_transaction
status
error
```

This makes each processing step independent and keeps the workflow modular.

---

## Statement Processing

The accountant uploads the company's transaction statement through the Streamlit dashboard.

The backend parses settled transactions and converts them into structured transaction objects.

Example:

```text
Payer          : SARAN
Transaction ID : T2608201821267350770576
Amount         : 1099
Date           : 2026-08-20
Status         : Settled
```

---

## Matching Engine

The extracted receipt is compared against transactions from the uploaded statement.

The current matching logic verifies three important fields:

```text
Transaction ID
      +
Amount
      +
Payment Date
```

Example:

```text
Receipt
Transaction ID : T2608201821267350770576
Amount         : 1099
Date           : 2026-08-20

             ↓

Statement
Transaction ID : T2608201821267350770576
Amount         : 1099
Date           : 2026-08-20

             ↓

ID MATCH     : True
AMOUNT MATCH : True
DATE MATCH   : True

             ↓

PAYMENT MATCHED ✅
```

If the transaction does not exist in the statement, the workflow returns:

```text
NOT_MATCHED
```

---

## Reconciliation Report

Successfully matched payments are written to an Excel reconciliation report.

```text
data/reports/reconciliation_report.xlsx
```

This report is then used by the backend and dashboard to display reconciled payments.

---

## FastAPI Backend

**FastAPI** provides the backend API layer.

Main operations include:

```text
GET  /health
POST /upload-statement
GET  /matches
POST /payments/{transaction_id}/confirm
```

The API connects statement processing, reconciliation results and the Streamlit frontend.

---

## Streamlit Dashboard

The **Streamlit dashboard** provides a simple interface for the accountant.

The accountant can:

- Upload the transaction statement
- View automatically matched payments
- Check customer and transaction details
- Review reconciliation status
- Approve verified payments

The receipt itself comes automatically through WhatsApp.

---

## Human-in-the-Loop Approval

The system does not automatically make the final accounting decision.

```text
AI Processing
     ↓
Payment Matched
     ↓
Streamlit Dashboard
     ↓
Accountant Reviews
     ↓
Approve Payment
     ↓
APPROVED
```

This keeps a human in control of the final financial approval.

---

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core application |
| OpenAI API | Receipt classification and extraction |
| LangGraph | AI workflow orchestration |
| Pydantic | Structured data validation |
| Neonize | WhatsApp integration |
| FastAPI | Backend API |
| Streamlit | Accountant dashboard |
| Pandas | Statement processing |
| OpenPyXL | Excel report generation |

---

## Project Structure

```text
ai-payment-reconciliation/
│
├── backend/
│   ├── api/
│   ├── graph/
│   │   ├── state.py
│   │   ├── nodes.py
│   │   └── workflow.py
│   │
│   ├── schemas/
│   ├── services/
│   │   ├── receipt_classifier.py
│   │   ├── receipt_extractor.py
│   │   ├── bank_parser.py
│   │   ├── matcher.py
│   │   └── report_exporter.py
│   │
│   ├── whatsapp/
│   │   ├── client.py
│   │   ├── listener.py
│   │   ├── downloader.py
│   │   └── session.py
│   │
│   └── main.py
│
├── frontend/
│   └── app.py
│
├── data/
│   ├── receipts/
│   ├── statements/
│   └── reports/
│
├── requirements.txt
└── README.md
```

---

## Running the Project

Activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 1. Start FastAPI

```powershell
python -m uvicorn backend.main:app --reload
```

### 2. Start Streamlit

```powershell
python -m streamlit run frontend/app.py
```

### 3. Start WhatsApp Client

```powershell
python -m backend.whatsapp.client
```

Once WhatsApp displays:

```text
WhatsApp connected successfully!
```

new customer receipt images can automatically enter the reconciliation workflow.

---

## Successful End-to-End Test

The system was tested using a PhonePe receipt:

```text
Amount         : ₹1,099
Transaction ID : T2608201821267350770576
Date           : 2026-08-20
Status         : SUCCESS
```

The corresponding transaction existed in the uploaded statement.

The matcher produced:

```text
ID MATCH: True
AMOUNT MATCH: True
DATE MATCH: True

PAYMENT MATCHED ✅
LANGGRAPH FINAL STATUS: MATCHED
REPORT UPDATED ✅
```

The system was also tested with a receipt that did not exist in the statement and correctly returned:

```text
NOT_MATCHED
```

---

## Future Improvements

- Duplicate receipt detection
- Multiple bank/UPI statement formats
- Confidence-based matching
- Improved WhatsApp contact-name resolution
- WhatsApp confirmation after approval
- Authentication for the accountant dashboard
- Database-backed reconciliation history
- ERP/accounting software integration

---

## Summary

This project demonstrates an end-to-end **AI engineering workflow** combining:

**WhatsApp Automation + Multimodal AI + Structured Extraction + Pydantic + LangGraph + Transaction Matching + FastAPI + Streamlit + Human Approval**

> This project is a prototype. Production financial systems would require additional authentication, security, audit logging and validation.
