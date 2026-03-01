"""
AI API Routes

Endpoints for AI-powered recommendations, anomaly detection, and insights.
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import json

from database import get_db
from services import create_qwen_service, create_analytics_service
from models.transaction import Transaction, AIRecommendation

router = APIRouter(prefix="/api/ai", tags=["ai"])


@router.get("/{merchant_id}/insights")
async def get_ai_insights(
    merchant_id: str,
    days: int = Query(30, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    """
    Get AI-generated insights and recommendations for a merchant
    """
    try:
        qwen_service = create_qwen_service()
        analytics = create_analytics_service()

        # Get recent transactions
        transactions = db.query(Transaction).filter(
            Transaction.merchant_id == merchant_id,
            Transaction.transaction_time >= datetime.utcnow() - timedelta(days=days)
        ).all()

        tx_list = [
            {
                "amount": tx.amount,
                "status": tx.status,
                "transaction_time": tx.transaction_time.isoformat(),
                "payment_method": tx.payment_method
            }
            for tx in transactions
        ]

        # Calculate health metrics
        health_data = analytics.calculate_health_score(tx_list)

        # Generate AI insights
        insights = qwen_service.generate_merchant_insights(health_data)

        # Save recommendations to database
        for action in insights.get('immediateActions', []) + insights.get('strategicActions', []):
            recommendation = AIRecommendation(
                merchant_id=merchant_id,
                recommendation_type='immediate' if action in insights.get('immediateActions', []) else 'strategic',
                title=action.get('title', ''),
                description=action.get('description', ''),
                severity=action.get('priority', 'medium'),
                priority=action.get('priority', 'medium'),
                model_used='qwen-max'
            )
            db.add(recommendation)

        db.commit()

        return {
            "data": insights,
            "merchantId": merchant_id,
            "analysisDate": datetime.utcnow().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{merchant_id}/anomalies")
async def detect_anomalies(
    merchant_id: str,
    days: int = Query(30, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    """
    Detect anomalous transactions using ML
    """
    try:
        analytics = create_analytics_service()

        # Get transactions
        transactions = db.query(Transaction).filter(
            Transaction.merchant_id == merchant_id,
            Transaction.transaction_time >= datetime.utcnow() - timedelta(days=days)
        ).all()

        tx_list = [
            {
                "id": tx.id,
                "transaction_id": tx.transaction_id,
                "amount": tx.amount,
                "status": tx.status,
                "transaction_time": tx.transaction_time.isoformat(),
                "payment_method": tx.payment_method
            }
            for tx in transactions
        ]

        # Detect anomalies
        results = analytics.detect_anomalies(tx_list)

        # Update database with anomaly flags
        anomaly_count = 0
        for tx_result in results:
            if tx_result.get('is_anomaly'):
                anomaly_count += 1
                # Update transaction in database
                db.query(Transaction).filter(
                    Transaction.transaction_id == tx_result.get('transaction_id')
                ).update({
                    "is_anomaly": True,
                    "anomaly_score": tx_result.get('anomaly_score')
                })

        db.commit()

        return {
            "data": {
                "transactions": results,
                "totalAnomalies": anomaly_count,
                "anomalyRate": round(anomaly_count / len(results) * 100, 2) if results else 0
            },
            "analyzedAt": datetime.utcnow().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{merchant_id}/forecast")
async def get_revenue_forecast(
    merchant_id: str,
    periods: int = Query(7, description="Number of days to forecast"),
    db: Session = Depends(get_db)
):
    """
    Get revenue forecast using time-series analysis
    """
    try:
        analytics = create_analytics_service()

        # Get historical daily revenue
        transactions = db.query(Transaction).filter(
            Transaction.merchant_id == merchant_id,
            Transaction.transaction_time >= datetime.utcnow() - timedelta(days=60)
        ).all()

        # Aggregate by date
        daily_revenue = {}
        for tx in transactions:
            if tx.status != 'success':
                continue
            date = tx.transaction_time.strftime('%Y-%m-%d')
            if date not in daily_revenue:
                daily_revenue[date] = 0
            daily_revenue[date] += tx.amount

        daily_revenue_list = [
            {"date": k, "revenue": v}
            for k, v in sorted(daily_revenue.items())
        ]

        # Generate forecast
        forecasts = analytics.forecast_revenue(daily_revenue_list, periods)

        return {
            "data": {
                "historical": daily_revenue_list[-30:],  # Last 30 days
                "forecast": forecasts
            },
            "forecastedAt": datetime.utcnow().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{merchant_id}/analyze-transaction")
async def analyze_single_transaction(
    merchant_id: str,
    transaction_id: str,
    db: Session = Depends(get_db)
):
    """
    Analyze a single transaction for anomalies
    """
    try:
        qwen_service = create_qwen_service()
        analytics = create_analytics_service()

        # Get the transaction
        transaction = db.query(Transaction).filter(
            Transaction.transaction_id == transaction_id,
            Transaction.merchant_id == merchant_id
        ).first()

        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")

        # Get historical pattern for this merchant
        historical_transactions = db.query(Transaction).filter(
            Transaction.merchant_id == merchant_id,
            Transaction.id != transaction.id
        ).limit(100).all()

        if historical_transactions:
            amounts = [tx.amount for tx in historical_transactions if tx.status == 'success']
            avg_amount = sum(amounts) / len(amounts) if amounts else transaction.amount
            std_amount = (sum((a - avg_amount) ** 2 for a in amounts) / len(amounts)) ** 0.5 if len(amounts) > 1 else avg_amount * 0.3
        else:
            avg_amount = transaction.amount
            std_amount = transaction.amount * 0.3

        historical_pattern = {
            "avg_amount": avg_amount,
            "std_amount": std_amount,
            "typical_hours": list(range(9, 21))  # 9 AM to 8 PM
        }

        tx_data = {
            "amount": transaction.amount,
            "hour": transaction.transaction_time.hour if transaction.transaction_time else 12
        }

        # Analyze for anomaly
        anomaly_result = qwen_service.analyze_transaction_anomaly(tx_data, historical_pattern)

        return {
            "data": {
                "transaction_id": transaction_id,
                "amount": transaction.amount,
                **anomaly_result
            },
            "analyzedAt": datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recommendations/{merchant_id}")
async def get_recommendations(
    merchant_id: str,
    status: str = Query("pending", description="Filter by status"),
    limit: int = Query(10),
    db: Session = Depends(get_db)
):
    """
    Get stored AI recommendations for a merchant
    """
    try:
        query = db.query(AIRecommendation).filter(
            AIRecommendation.merchant_id == merchant_id
        )

        if status:
            query = query.filter(AIRecommendation.status == status)

        recommendations = query.order_by(
            AIRecommendation.created_at.desc()
        ).limit(limit).all()

        return {
            "data": [
                {
                    "id": rec.id,
                    "type": rec.recommendation_type,
                    "title": rec.title,
                    "description": rec.description,
                    "severity": rec.severity,
                    "priority": rec.priority,
                    "status": rec.status,
                    "expected_revenue_impact": rec.expected_revenue_impact,
                    "expected_health_impact": rec.expected_health_impact,
                    "created_at": rec.created_at.isoformat()
                }
                for rec in recommendations
            ],
            "total": len(recommendations)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recommendations/{recommendation_id}/implement")
async def mark_recommendation_implemented(
    recommendation_id: int,
    db: Session = Depends(get_db)
):
    """
    Mark a recommendation as implemented
    """
    try:
        recommendation = db.query(AIRecommendation).filter(
            AIRecommendation.id == recommendation_id
        ).first()

        if not recommendation:
            raise HTTPException(status_code=404, detail="Recommendation not found")

        recommendation.status = "implemented"
        recommendation.implemented_at = datetime.utcnow()
        db.commit()

        return {
            "success": True,
            "data": {
                "id": recommendation.id,
                "status": "implemented",
                "implemented_at": recommendation.implemented_at.isoformat()
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
