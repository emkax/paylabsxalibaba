# Paylabs AI Merchant Health & Survival Intelligence (MHSI)

AI-powered merchant analytics engine using **Qwen (Alibaba DashScope)** to analyze Paylabs transaction data and generate structured financial risk intelligence.

---

# 🧠 Architecture Overview

```
Excel (Sandbox Merchant Data)
        ↓
calculate_performance_metrics()
        ↓
Structured Metrics JSON
        ↓
Qwen (DashScope API - qwen-plus)
        ↓
Structured Risk Analysis (OVERVIEW / ACTION)
```

---

# 📦 Project Structure

```
.
├── analyze.py
├── extract_performance_metric.py
├── .env
├── case1.json (optional JSON mode)
├── sandbox_merchant.xlsx   <-- place Excel file here
└── session_memory.json     <-- auto-generated
```

---

# ⚙️ Requirements

- Python 3.9+
- Alibaba DashScope API Key
- pip

Install dependencies:

```bash
pip install openai python-dotenv pandas openpyxl
```

---

# 🔑 Environment Setup

Create `.env` file:

```
DASHSCOPE_API_KEY=your_dashscope_key_here
```

The system uses:

```
model="qwen-plus"
base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
```

---

# 📊 Using Excel Sandbox Merchant Data

## 1️⃣ Prepare Excel File

Place merchant transaction Excel file inside project root:

```
sandbox_merchant.xlsx
```

Expected columns (minimum):

- transaction_date
- amount
- customer_id
- status (optional)
- payment_method (optional)

---

## 2️⃣ Compute Performance Metrics

`extract_performance_metric.py` must expose:

```python
calculate_performance_metrics(excel_path: str) -> dict
```

Example returned structure:

```python
{
    "analysis_start": "2025-01-01",
    "analysis_end": "2025-01-31",
    "total_revenue": 720000000,
    "revenue_change_30d_percent": 21.6,
    "revenue_volatility_score": 0.41,
    "cashflow_stress_index": 0.19,
    "avg_ticket_size": 82000,
    "ticket_size_change_percent": 7.8,
    "transaction_frequency_change_percent": 12.4,
    "negative_cashflow_streak_days": 2,
    "customer_repeat_ratio": 0.46,
    "peak_hour_distribution": {
        "08:00-12:00": 0.32,
        "12:00-18:00": 0.48,
        "18:00-23:00": 0.20
    }
}
```

---

## 3️⃣ Inject Metrics into Session

Modify `analyze.py` entry logic to compute directly from Excel:

```python
from extract_performance_metric import calculate_performance_metrics

metrics = calculate_performance_metrics("sandbox_merchant.xlsx")

profile = None  # optional merchant profile

session.initialize(
    merchant_profile=profile,
    metrics_data={
        "performance_metrics": metrics,
        "peer_comparison": {}  # optional
    }
)
```

---

# 🚀 Running the System

## Interactive Mode

```bash
python analyze.py case1.json
```

OR if using Excel-based metrics (recommended):

```bash
python analyze.py
```

Commands available:

```
ACTION
OVERVIEW
reset
quit
```

---

# 📌 Command Modes

## OVERVIEW

Returns strict JSON:

```json
{
  "overview": {
    "health_score": 78,
    "survival_probability_60d": 84,
    "survival_trend": "Improving",
    "key_metrics": { ... },
    "peer_comparison": { ... },
    "top_risks": [ ... ]
  }
}
```

---

## ACTION

Returns structured 0–7d, 30d, 90d execution plan:

```json
{
  "action_plan": {
    "immediate": { ... },
    "strategic_30_days": { ... },
    "strategic_90_days": { ... }
  }
}
```

---

# 🧮 Metrics Explained

| Metric | Purpose |
|--------|----------|
| revenue_change_30d_percent | Growth or decline indicator |
| revenue_volatility_score | Revenue instability index |
| cashflow_stress_index | Liquidity risk indicator |
| avg_ticket_size | Monetization quality |
| ticket_size_change_percent | Pricing power trend |
| transaction_frequency_change_percent | Demand velocity |
| negative_cashflow_streak_days | Consecutive liquidity pressure |
| customer_repeat_ratio | Retention quality |
| peak_hour_distribution | Operational concentration risk |

---

# 🧠 AI Behavior Control

The system prompt enforces:

- No hallucination
- No fabricated metrics
- Data-cited reasoning only
- Strict JSON mode for ACTION & OVERVIEW
- Session memory persistence

Temperature: `0.2`  
Max Tokens: `2500`

---

# 💾 Session Memory

Automatically saved to:

```
session_memory.json
```

Includes:

- merchant_profile
- metrics_data
- conversation_history

Reset conversation:

```
reset
```

---

# 🔍 What This System Can Do

✔ Compute financial health indicators  
✔ Detect revenue volatility patterns  
✔ Detect liquidity stress risk  
✔ Detect declining demand signals  
✔ Measure customer retention quality  
✔ Generate structured survival probability  
✔ Compare merchant vs peer metrics  
✔ Generate prioritized execution plan  
✔ Maintain multi-turn AI memory session  

---

# 🛑 What It Does NOT Do

- Does not fabricate missing data
- Does not predict without metric basis
- Does not access external databases
- Does not modify merchant data

---

# 🧩 Extending the System

You can extend:

- Add anomaly detection layer
- Add peer auto-clustering
- Add seasonal adjustment modeling
- Add LTV prediction model
- Add churn classification model
- Add risk scoring regression model

---

# 📌 Production Notes

For production deployment:

- Wrap CLI with FastAPI
- Add authentication layer
- Add structured logging
- Add rate limiting
- Move session storage to Redis or database
- Add async processing queue

---

# 🏁 Summary

This system converts raw Paylabs merchant transaction data into:

- Financial health score
- Survival probability
- Risk detection
- Data-grounded execution roadmap

Powered by:

- Python
- Pandas
- Qwen (Alibaba DashScope)
- Structured Anti-Hallucination Prompting