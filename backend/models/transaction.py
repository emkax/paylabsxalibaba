"""
SQLAlchemy models for PayLabs transaction data
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Index, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Transaction(Base):
    """
    Transaction model for storing PayLabs payment data
    """
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String(64), unique=True, index=True, nullable=False)
    merchant_id = Column(String(32), index=True, nullable=False)

    # Transaction details
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="IDR")
    payment_method = Column(String(32))  # qris, va, cc, emoney, etc.
    transaction_type = Column(String(32))  # payment, refund, chargeback

    # Status
    status = Column(String(32), index=True)  # success, pending, failed, cancelled
    is_anomaly = Column(Boolean, default=False, index=True)
    anomaly_score = Column(Float, nullable=True)

    # Timestamps
    transaction_time = Column(DateTime, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Raw data storage
    raw_data = Column(JSON, nullable=True)

    # Indices for common queries
    __table_args__ = (
        Index('idx_merchant_time', 'merchant_id', 'transaction_time'),
        Index('idx_status_time', 'status', 'transaction_time'),
    )

    def __repr__(self):
        return f"<Transaction(id={self.transaction_id}, amount={self.amount}, status={self.status})>"


class MerchantHealthSnapshot(Base):
    """
    Daily health score snapshots for merchants
    """
    __tablename__ = "merchant_health_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(String(32), index=True, nullable=False)
    snapshot_date = Column(DateTime, index=True, nullable=False)

    # Health metrics
    health_score = Column(Float, nullable=False)
    survival_probability = Column(Float, nullable=False)
    risk_level = Column(String(16))  # low, medium, high

    # KPIs
    daily_revenue = Column(Float)
    revenue_change = Column(Float)
    volatility_score = Column(Float)
    cashflow_stress_index = Column(Float)
    peer_percentile = Column(Float)
    repeat_ratio = Column(Float)

    # AI recommendations
    ai_insights = Column(JSON, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('idx_merchant_date', 'merchant_id', 'snapshot_date'),
    )

    def __repr__(self):
        return f"<MerchantHealthSnapshot(merchant={self.merchant_id}, score={self.health_score})>"


class AIRecommendation(Base):
    """
    AI-generated recommendations for merchants
    """
    __tablename__ = "ai_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(String(32), index=True, nullable=False)

    # Recommendation content
    recommendation_type = Column(String(32))  # immediate, strategic, alert
    title = Column(String(256), nullable=False)
    description = Column(String(1024))
    severity = Column(String(16))  # high, medium, low
    priority = Column(String(16))  # high, medium, low

    # Expected impact
    expected_revenue_impact = Column(Float)  # percentage
    expected_health_impact = Column(Float)  # points

    # Status
    status = Column(String(16), default="pending")  # pending, implemented, dismissed
    implemented_at = Column(DateTime, nullable=True)

    # AI metadata
    model_used = Column(String(64))  # e.g., "qwen-max"
    confidence_score = Column(Float)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index('idx_merchant_status', 'merchant_id', 'status'),
    )

    def __repr__(self):
        return f"<AIRecommendation(merchant={self.merchant_id}, type={self.recommendation_type})>"


class SimulationResult(Base):
    """
    What-if simulation results
    """
    __tablename__ = "simulation_results"

    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(String(32), index=True, nullable=False)

    # Simulation parameters
    discount_percentage = Column(Float, default=0)
    cost_reduction_percentage = Column(Float, default=0)
    marketing_boost_percentage = Column(Float, default=0)
    delivery_integration = Column(Boolean, default=False)

    # Results
    forecasted_revenue = Column(Float)
    updated_health_score = Column(Float)
    updated_survival_probability = Column(Float)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<SimulationResult(merchant={self.merchant_id}, revenue={self.forecasted_revenue})>"
