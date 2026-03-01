# PaylabsxAlibaba — Paylabs Payment Integration + AI Insight System

This repository contains the backend payment integration with **PayLabs Indonesia API** and a frontend dashboard system for merchant transaction analytics. It includes integration modules for creating and querying payments across multiple payment methods and a structured frontend SRS for the merchant intelligence dashboard. :contentReference[oaicite:1]{index=1}

---

## 📁 Repository Structure

```
paylabsxalibaba/
├── create/                # Payment creation module
├── query/                 # Payment status query module
├── CONTEXT.md             # Project context & integration details
├── Paylabs_Merchant_Health_Dashboard_Frontend_SRS.md   # Frontend specification
├── .gitignore
```
:contentReference[oaicite:2]{index=2}

---

## 🔧 Supported Payment Methods

The backend supports creation of payment transactions via PayLabs API for these payment types: :contentReference[oaicite:3]{index=3}

- QRIS (Quick Response Indonesian Standard)  
- Virtual Accounts (Bank VAs)  
- Credit Cards  
- E-Wallets (e.g., GoPay, OVO, DANA, LINKAJA)  
- Installment / Direct Debit (e.g., Kredivo, Indodana, Atome)  

All integrations use RSA-SHA256 signed requests according to PayLabs API spec. :contentReference[oaicite:4]{index=4}

---

## 📌 Core Backend Modules

### 1. Payment Creation (`create/`)
- `main.py`: Entrypoint for running payment generation flows  
- `signature.py`: RSA-SHA256 request signing utility  
- `timestamp.py`: ISO-8601 timestamp generator with timezone offset  
- Payment creation files by type:
  - `qris.py`
  - `va.py` (Virtual Accounts)
  - `cc.py` (Credit Card)
  - `emoney.py` (E-Wallet)
  - `ec.py` (Installment / Direct Debit, partial)  
- `seeding.py`: Bulk transaction generator for testing  
:contentReference[oaicite:5]{index=5}

### 2. Payment Query (`query/`)
- `main.py`: Entrypoint for querying payment status  
- Re-uses `signature.py` and `timestamp.py` for request signing  
:contentReference[oaicite:6]{index=6}

---

## 📡 API Integration Basics

All PayLabs API calls are signed using RSA-SHA256. Required headers include: :contentReference[oaicite:7]{index=7}

- `X-TIMESTAMP` — ISO-8601 timestamp  
- `X-SIGNATURE` — Base64 encoded RSA signature  
- `X-PARTNER-ID` — Merchant ID  
- `X-REQUEST-ID` — UUID unique request identifier  

Signature string format:

```
{HTTP_METHOD}:{API_ENDPOINT}:{SHA256_BODY}:{TIMESTAMP}
```

---

## 📋 Frontend (Merchant Dashboard Spec)

The frontend system is defined in `Paylabs_Merchant_Health_Dashboard_Frontend_SRS.md` and includes: :contentReference[oaicite:8]{index=8}

### Tech Stack
- Next.js (React 18+)
- TypeScript
- React Query (TanStack)
- Native CSS Modules
- ECharts / Recharts for charts
- Deployed on Alibaba Cloud ECS

### Core Pages
- `/dashboard/overview`
- `/dashboard/revenue`
- `/dashboard/cashflow`
- `/dashboard/peer`
- `/dashboard/recommendation`
- `/dashboard/simulation`
:contentReference[oaicite:9]{index=9}

### API Contract for Dashboard
```
GET /merchant/:id/overview
GET /merchant/:id/performance
GET /merchant/:id/peer
GET /merchant/:id/risk
GET /merchant/:id/recommendation
POST /merchant/:id/simulate
```
Responses return JSON with KPIs, trend series, and timestamps. :contentReference[oaicite:10]{index=10}

---

## 🧠 AI Recommendation Module (Specification)

The dashboard SRS outlines an AI-driven recommendation module with:
- Root cause analysis section  
- Immediate action plan (30 days)  
- Strategic actions (90 days)  
- Expected KPI impact simulation  
:contentReference[oaicite:11]{index=11}

This module should be powered by the backend analytics + an AI model (e.g., Qwen) to generate insight summaries.

---

## 🛠 Backend Environment Variables

```
MID=                 # Merchant ID
PRIVATE_KEY_PATH=    # Path to RSA private key
PUBLIC_KEY_PATH=     # Path to RSA public key
PRODUCT_PATH=        # Path to sample product CSV
```
:contentReference[oaicite:12]{index=12}

---

## 📦 Dependencies

The Python backend uses libraries including:

- `cryptography` — RSA signatures  
- `requests` — HTTP client  
- `python-dotenv` — Environment variables  
- `pandas` — Data processing (product data)  
:contentReference[oaicite:13]{index=13}

---

## ⚠ Notes

- `ec.py` (Direct Debit) is considered incomplete or non-functional.
- Some API endpoints have typo inconsistencies in their documentation.
- Private keys are excluded from the repository for security.

---

## 🧪 Testing

- `seeding.py` can generate hundreds of synthetic test transactions.  

---
