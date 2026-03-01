import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

import json

BASE_DIR = Path(__file__).parent

def calculate_performance_metrics(
    file_path,
    analysis_year,
    start_month,
    end_month,
    start_day=1,
    end_day=None,
    time_col="Initiation Time",
    amount_col="Amount",
    status_col="Order Status",
    success_status=None
):
    """
    Flexible performance calculation
    Based on custom start & end date
    """

    if success_status is None:
        success_status = ["SUCCESS", "PAID", "COMPLETED", "Success"]

    # ===============================
    # LOAD DATA
    # ===============================
    df = pd.read_excel(file_path)

    df[time_col] = pd.to_datetime(df[time_col])
    df = df[df[status_col].isin(success_status)].copy()

    if df.empty:
        return {"error": "No successful transactions found."}

    df = df.sort_values(time_col)
    df["date"] = df[time_col].dt.date
    df["hour"] = df[time_col].dt.hour

    # ===============================
    # DEFINE CUSTOM DATE RANGE
    # ===============================

    if end_day is None:
        # auto last day of end_month
        if end_month == 12:
            next_month = datetime(analysis_year + 1, 1, 1)
        else:
            next_month = datetime(analysis_year, end_month + 1, 1)
        end_date = next_month - timedelta(seconds=1)
    else:
        end_date = datetime(analysis_year, end_month, end_day, 23, 59, 59)

    start_date = datetime(analysis_year, start_month, start_day)

    # Rolling comparison windows
    last_30_days_start = end_date - timedelta(days=30)
    prev_30_days_start = last_30_days_start - timedelta(days=30)

    # ===============================
    # MAIN WINDOW DATA
    # ===============================

    df_main = df[
        (df[time_col] >= start_date) &
        (df[time_col] <= end_date)
    ]

    df_30d = df[
        (df[time_col] > last_30_days_start) &
        (df[time_col] <= end_date)
    ]

    df_prev_30d = df[
        (df[time_col] > prev_30_days_start) &
        (df[time_col] <= last_30_days_start)
    ]

    # ===============================
    # REVENUE METRICS
    # ===============================

    total_revenue = df_main[amount_col].sum()

    revenue_30d = df_30d[amount_col].sum()
    revenue_prev_30d = df_prev_30d[amount_col].sum()

    revenue_change_30d_percent = (
        ((revenue_30d - revenue_prev_30d) / revenue_prev_30d) * 100
        if revenue_prev_30d > 0 else 0
    )

    # ===============================
    # VOLATILITY & CASHFLOW
    # ===============================

    daily_revenue = df_30d.groupby("date")[amount_col].sum()

    revenue_volatility_score = (
        daily_revenue.std() / daily_revenue.mean()
        if daily_revenue.mean() > 0 else 0
    )

    negative_days = (daily_revenue == 0).sum()
    cashflow_stress_index = (negative_days / 30) + revenue_volatility_score * 0.5

    # Negative streak
    streak = 0
    max_streak = 0

    for val in daily_revenue.values:
        if val == 0:
            streak += 1
            max_streak = max(max_streak, streak)
        else:
            streak = 0

    # ===============================
    # TICKET SIZE
    # ===============================

    total_transactions = len(df_main)

    avg_ticket_size = (
        total_revenue / total_transactions
        if total_transactions > 0 else 0
    )

    avg_ticket_30d = df_30d[amount_col].mean()
    avg_ticket_prev_30d = df_prev_30d[amount_col].mean()

    ticket_size_change_percent = (
        ((avg_ticket_30d - avg_ticket_prev_30d) / avg_ticket_prev_30d) * 100
        if avg_ticket_prev_30d > 0 else 0
    )

    # ===============================
    # TRANSACTION FREQUENCY
    # ===============================

    transaction_frequency_change_percent = (
        ((len(df_30d) - len(df_prev_30d)) / len(df_prev_30d)) * 100
        if len(df_prev_30d) > 0 else 0
    )

    # ===============================
    # PEAK HOUR DISTRIBUTION
    # ===============================

    def categorize_hour(hour):
        if 6 <= hour <= 11:
            return "morning"
        elif 12 <= hour <= 17:
            return "afternoon"
        else:
            return "evening"

    df_main["time_category"] = df_main["hour"].apply(categorize_hour)

    peak_dist = (
        df_main["time_category"]
        .value_counts(normalize=True)
        .mul(100)
        .round(2)
        .to_dict()
    )

    for key in ["morning", "afternoon", "evening"]:
        peak_dist.setdefault(key, 0)

    # ===============================
    # CUSTOMER REPEAT RATIO
    # ===============================

    customer_repeat_ratio = None

    if "customer_id" in df_main.columns:
        customer_counts = df_main["customer_id"].value_counts()
        repeat_customers = (customer_counts > 1).sum()
        total_customers = customer_counts.count()

        customer_repeat_ratio = (
            repeat_customers / total_customers
            if total_customers > 0 else 0
        )

    # ===============================
    # FINAL OUTPUT
    # ===============================

    return {
        "analysis_start": start_date,
        "analysis_end": end_date,
        "total_revenue": round(total_revenue, 2),
        "revenue_change_30d_percent": round(revenue_change_30d_percent, 2),
        "revenue_volatility_score": round(revenue_volatility_score, 4),
        "cashflow_stress_index": round(cashflow_stress_index, 4),
        "avg_ticket_size": round(avg_ticket_size, 2),
        "ticket_size_change_percent": round(ticket_size_change_percent, 2),
        "transaction_frequency_change_percent": round(transaction_frequency_change_percent, 2),
        "negative_cashflow_streak_days": max_streak,
        "customer_repeat_ratio": round(customer_repeat_ratio, 2)
        if customer_repeat_ratio is not None else None,
        "peak_hour_distribution": peak_dist
    }

FILENAME = "Transaction_Order_Small_Case1"
metrics = calculate_performance_metrics(
    file_path=BASE_DIR / ("./"+ FILENAME + ".xlsx"),
    analysis_year=2026,
    start_month=1,
    end_month=2,
    start_day=15,
    end_day=20
)
print(metrics)


JSON_OUTPUT_PATH = BASE_DIR / ("./" + FILENAME + ".json")
print(JSON_OUTPUT_PATH)

with open(JSON_OUTPUT_PATH, "w") as f:
    json.dump(metrics, f, indent=4, default=str)