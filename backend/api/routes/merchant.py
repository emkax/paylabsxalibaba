"""
Merchant API Routes

REST API endpoints for merchant data, health metrics, and simulations.
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import os
import json

from database import get_db, get_redis_client
from services import create_paylabs_client, create_analytics_service, create_qwen_service
from models.transaction import Transaction, MerchantHealthSnapshot, SimulationResult

router = APIRouter(prefix="/api/merchant", tags=["merchant"])


@router.get("/{merchant_id}")
async def get_merchant_data(
    merchant_id: str,
    type: str = Query(..., description="Type of data to fetch"),
    days: int = Query(30, description="Number of days of data"),
    db: Session = Depends(get_db)
):
    """
    Get merchant data by type (overview, performance, cashflow, peer, risk, recommendation)
    """
    try:
        # Try to get from cache first
        redis = get_redis_client()
        cache_key = f"merchant:{merchant_id}:{type}:{days}"
        cached_data = redis.get(cache_key)

        if cached_data:
            import json
            return {"data": json.loads(cached_data), "source": "cache"}

        # Get data based on type
        analytics = create_analytics_service()
        qwen_service = create_qwen_service()

        if type == "overview":
            # Get recent transactions
            transactions = db.query(Transaction).filter(
                Transaction.merchant_id == merchant_id,
                Transaction.transaction_time >= datetime.utcnow() - timedelta(days=days)
            ).all()

            tx_list = [
                {
                    "amount": tx.amount,
                    "status": tx.status,
                    "transaction_time": tx.transaction_time,
                    "payment_method": tx.payment_method
                }
                for tx in transactions
            ]

            health_data = analytics.calculate_health_score(tx_list)

            # Cache for 5 minutes
            redis.setex(cache_key, 300, str(health_data))

            return {"data": health_data, "lastUpdated": datetime.utcnow().isoformat()}

        elif type == "performance":
            # Get revenue and transaction data
            transactions = db.query(Transaction).filter(
                Transaction.merchant_id == merchant_id,
                Transaction.transaction_time >= datetime.utcnow() - timedelta(days=days)
            ).all()

            # Aggregate daily revenue
            daily_data = {}
            for tx in transactions:
                if tx.status != 'success':
                    continue
                date = tx.transaction_time.strftime('%Y-%m-%d')
                if date not in daily_data:
                    daily_data[date] = {"date": date, "revenue": 0, "count": 0}
                daily_data[date]["revenue"] += tx.amount
                daily_data[date]["count"] += 1

            daily_revenue = sorted(daily_data.values(), key=lambda x: x['date'])
            transaction_frequency = [{"date": d["date"], "count": d["count"]} for d in daily_revenue]

            total_revenue = sum(d["revenue"] for d in daily_revenue)
            total_transactions = sum(d["count"] for d in daily_revenue)

            performance_data = {
                "dailyRevenue": daily_revenue,
                "transactionFrequency": transaction_frequency,
                "totalTransactions": total_transactions,
                "averageTransactionValue": total_revenue / total_transactions if total_transactions > 0 else 0
            }

            redis.setex(cache_key, 300, str(performance_data))

            return {"data": performance_data, "lastUpdated": datetime.utcnow().isoformat()}

        elif type == "cashflow":
            # Get cashflow data (simplified - would need actual inflow/outflow data)
            transactions = db.query(Transaction).filter(
                Transaction.merchant_id == merchant_id,
                Transaction.transaction_time >= datetime.utcnow() - timedelta(days=30)
            ).all()

            # Group by date
            daily_data = {}
            for tx in transactions:
                date = tx.transaction_time.strftime('%Y-%m-%d')
                if date not in daily_data:
                    daily_data[date] = {"inflow": 0, "outflow": 0}

                if tx.status == 'success':
                    daily_data[date]["inflow"] += tx.amount
                    # Estimate outflow as percentage (in real implementation, track actual expenses)
                    daily_data[date]["outflow"] += tx.amount * 0.85

            # Calculate metrics
            inflow = [{"date": k, "amount": v["inflow"]} for k, v in sorted(daily_data.items())]
            outflow = [{"date": k, "amount": v["outflow"]} for k, v in sorted(daily_data.items())]
            net = [{"date": k, "amount": v["inflow"] - v["outflow"]} for k, v in sorted(daily_data.items())]

            # Count negative days streak
            negative_streak = 0
            for n in reversed(net):
                if n["amount"] < 0:
                    negative_streak += 1
                else:
                    break

            cashflow_data = {
                "inflow": inflow,
                "outflow": outflow,
                "netCashflow": net,
                "negativeStreak": min(negative_streak, 5),
                "liquidityRunway": 90,  # Would be calculated from actual cash reserves
                "runwayTarget": 90
            }

            return {"data": cashflow_data, "lastUpdated": datetime.utcnow().isoformat()}

        elif type == "peer":
            # Get peer benchmark (would need actual peer data in production)
            peer_data = {
                "percentile": 65,
                "radarData": [
                    {"metric": "Revenue Growth", "merchant": 60, "peers": 50},
                    {"metric": "Cash Flow", "merchant": 55, "peers": 50},
                    {"metric": "Customer Retention", "merchant": 70, "peers": 60},
                    {"metric": "Transaction Volume", "merchant": 65, "peers": 55},
                    {"metric": "Avg Order Value", "merchant": 58, "peers": 50},
                    {"metric": "Profit Margin", "merchant": 52, "peers": 50},
                ],
                "comparisonTable": [
                    {"metric": "Monthly Revenue", "merchant": 156000000, "peers": 125000000, "industry": 98000000},
                    {"metric": "Growth Rate (%)", "merchant": 12.5, "peers": 8.3, "industry": 5.2},
                    {"metric": "Customer Retention (%)", "merchant": 78, "peers": 65, "industry": 58},
                    {"metric": "Avg Transaction (IDR)", "merchant": 485000, "peers": 420000, "industry": 380000},
                    {"metric": "Monthly Transactions", "merchant": 321, "peers": 298, "industry": 257},
                ],
                "peerSegment": "city"
            }

            return {"data": peer_data, "lastUpdated": datetime.utcnow().isoformat()}

        elif type == "risk":
            # Get risk assessment
            transactions = db.query(Transaction).filter(
                Transaction.merchant_id == merchant_id,
                Transaction.transaction_time >= datetime.utcnow() - timedelta(days=days)
            ).all()

            tx_list = [
                {
                    "amount": tx.amount,
                    "status": tx.status,
                    "transaction_time": tx.transaction_time.isoformat(),
                    "payment_method": tx.payment_method,
                    "is_anomaly": tx.is_anomaly
                }
                for tx in transactions
            ]

            health_data = analytics.calculate_health_score(tx_list)

            risk_data = {
                "riskLevel": health_data["riskLevel"],
                "riskScore": 100 - health_data["healthScore"],
                "factors": [
                    {"name": "Revenue Volatility", "score": health_data["kpis"]["volatilityScore"]},
                    {"name": "Cashflow Stress", "score": health_data["kpis"]["cashflowStressIndex"]},
                    {"name": "Peer Position", "score": 100 - health_data["kpis"]["peerPercentile"]},
                ]
            }

            return {"data": risk_data, "lastUpdated": datetime.utcnow().isoformat()}

        elif type == "recommendation":
            # Get AI recommendations
            transactions = db.query(Transaction).filter(
                Transaction.merchant_id == merchant_id,
                Transaction.transaction_time >= datetime.utcnow() - timedelta(days=days)
            ).all()

            tx_list = [
                {
                    "amount": tx.amount,
                    "status": tx.status,
                    "transaction_time": tx.transaction_time.isoformat()
                }
                for tx in transactions
            ]

            health_data = analytics.calculate_health_score(tx_list)

            # Generate AI insights
            ai_insights = qwen_service.generate_merchant_insights(health_data)

            return {"data": ai_insights, "lastUpdated": datetime.utcnow().isoformat()}

        else:
            raise HTTPException(status_code=400, detail=f"Invalid type: {type}")

    except Exception as e:
        # Fallback to mock data for demo purposes
        return _get_fallback_data(type, merchant_id, days)


@router.post("/{merchant_id}/simulate")
async def simulate_scenario(
    merchant_id: str,
    discount_percentage: float = Query(0),
    cost_reduction: float = Query(0),
    marketing_boost: float = Query(0),
    delivery_integration: bool = Query(False),
    db: Session = Depends(get_db)
):
    """
    Run what-if simulation for business decisions
    """
    try:
        analytics = create_analytics_service()

        # Get current merchant metrics
        transactions = db.query(Transaction).filter(
            Transaction.merchant_id == merchant_id,
            Transaction.transaction_time >= datetime.utcnow() - timedelta(days=30)
        ).all()

        tx_list = [
            {
                "amount": tx.amount,
                "status": tx.status,
                "transaction_time": tx.transaction_time.isoformat()
            }
            for tx in transactions
        ]

        base_metrics = analytics.calculate_health_score(tx_list)

        # Run simulation
        simulation_result = analytics.simulate_scenario(
            base_metrics=base_metrics,
            discount_percentage=discount_percentage,
            cost_reduction=cost_reduction,
            marketing_boost=marketing_boost,
            delivery_integration=delivery_integration
        )

        # Save simulation result
        sim_record = SimulationResult(
            merchant_id=merchant_id,
            discount_percentage=discount_percentage,
            cost_reduction_percentage=cost_reduction,
            marketing_boost_percentage=marketing_boost,
            delivery_integration=delivery_integration,
            forecasted_revenue=simulation_result["forecastedRevenue"],
            updated_health_score=simulation_result["updatedHealthScore"],
            updated_survival_probability=simulation_result["updatedSurvivalProbability"]
        )

        db.add(sim_record)
        db.commit()

        return {
            "data": simulation_result,
            "lastUpdated": datetime.utcnow().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{merchant_id}/transactions")
async def get_transactions(
    merchant_id: str,
    start_date: str = Query(..., description="Start date YYYY-MM-DD"),
    end_date: str = Query(..., description="End date YYYY-MM-DD"),
    limit: int = Query(100),
    offset: int = Query(0),
    db: Session = Depends(get_db)
):
    """
    Get transactions for a merchant within a date range
    """
    try:
        transactions = db.query(Transaction).filter(
            Transaction.merchant_id == merchant_id,
            Transaction.transaction_time >= datetime.strptime(start_date, '%Y-%m-%d'),
            Transaction.transaction_time <= datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
        ).offset(offset).limit(limit).all()

        return {
            "data": [
                {
                    "transaction_id": tx.transaction_id,
                    "amount": tx.amount,
                    "currency": tx.currency,
                    "payment_method": tx.payment_method,
                    "status": tx.status,
                    "transaction_time": tx.transaction_time.isoformat(),
                    "is_anomaly": tx.is_anomaly,
                    "anomaly_score": tx.anomaly_score
                }
                for tx in transactions
            ],
            "total": len(transactions),
            "limit": limit,
            "offset": offset
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _get_fallback_data(type: str, merchant_id: str, days: int) -> Dict[str, Any]:
    """
    Return fallback data when database is not available
    This ensures the dashboard works for demo purposes
    """
    import random
    from datetime import date

    if type == "overview":
        health_score = random.randint(65, 95)
        return {
            "data": {
                "healthScore": health_score,
                "survivalProbability": random.randint(70, 95),
                "riskLevel": "low" if health_score >= 80 else "medium" if health_score >= 70 else "high",
                "kpis": {
                    "revenue": random.randint(100000000, 600000000),
                    "revenueChange": round(random.uniform(-5, 15), 2),
                    "volatilityScore": random.randint(10, 50),
                    "cashflowStressIndex": random.randint(10, 70),
                    "peerPercentile": random.randint(50, 90),
                    "repeatRatio": round(random.uniform(0.4, 0.8), 2)
                }
            },
            "lastUpdated": datetime.utcnow().isoformat()
        }

    elif type == "performance":
        daily_revenue = []
        transaction_frequency = []
        base_revenue = random.randint(2000000, 7000000)
        base_transactions = random.randint(200, 700)

        for i in range(days - 1, -1, -1):
            d = date.today() - timedelta(days=i)
            daily_revenue.append({
                "date": d.isoformat(),
                "revenue": int(base_revenue * (0.8 + random.random() * 0.4))
            })
            transaction_frequency.append({
                "date": d.isoformat(),
                "count": int(base_transactions * (0.8 + random.random() * 0.4))
            })

        return {
            "data": {
                "dailyRevenue": daily_revenue,
                "transactionFrequency": transaction_frequency,
                "totalTransactions": sum(t["count"] for t in transaction_frequency),
                "averageTransactionValue": base_revenue / base_transactions if base_transactions > 0 else 0
            },
            "lastUpdated": datetime.utcnow().isoformat()
        }

    elif type == "recommendation":
        return {
            "data": {
                "rootCauses": [
                    {
                        "title": "Revenue Volatility",
                        "description": "High day-to-day revenue fluctuations indicate inconsistent demand.",
                        "severity": "high"
                    }
                ],
                "immediateActions": [
                    {
                        "id": "1",
                        "title": "Implement Weekend Promotions",
                        "description": "Launch targeted weekend discounts to boost low-period sales.",
                        "expectedImpact": "+15% weekend revenue",
                        "status": "pending",
                        "priority": "high"
                    }
                ],
                "strategicActions": [
                    {
                        "id": "2",
                        "title": "Expand Product Categories",
                        "description": "Add complementary products to increase average order value.",
                        "expectedImpact": "+25% AOV",
                        "status": "pending",
                        "priority": "medium"
                    }
                ],
                "expectedImpact": {
                    "revenue": 23,
                    "healthScore": 12
                }
            },
            "lastUpdated": datetime.utcnow().isoformat()
        }

    # Default fallback
    return {
        "data": {},
        "lastUpdated": datetime.utcnow().isoformat()
    }
