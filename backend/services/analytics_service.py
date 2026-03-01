"""
Analytics Service for Merchant Health Intelligence

This module provides health score calculation, anomaly detection,
predictive analytics, and peer benchmarking.
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


class AnalyticsService:
    """
    Service for calculating merchant health metrics and detecting anomalies
    """

    def __init__(self):
        self.scaler = StandardScaler()

    def calculate_health_score(
        self,
        transactions: List[Dict[str, Any]],
        peer_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive health score for a merchant

        Args:
            transactions: List of transaction dictionaries
            peer_data: Optional peer benchmark data

        Returns:
            Dictionary containing health score, survival probability, and KPIs
        """
        if not transactions:
            return self._empty_health_result()

        df = pd.DataFrame(transactions)

        # Convert transaction_time to datetime
        if 'transaction_time' in df.columns:
            df['transaction_time'] = pd.to_datetime(df['transaction_time'])
            df = df.sort_values('transaction_time')

        # Calculate key metrics
        total_revenue = df[df['status'] == 'success']['amount'].sum()

        # Daily aggregation
        df['date'] = pd.to_datetime(df['transaction_time']).dt.date if 'transaction_time' in df.columns else pd.to_datetime(df['created_at']).dt.date
        daily_revenue = df.groupby('date')['amount'].sum()

        # Revenue metrics
        avg_daily_revenue = daily_revenue.mean() if len(daily_revenue) > 0 else 0
        revenue_std = daily_revenue.std() if len(daily_revenue) > 1 else 0
        revenue_volatility = (revenue_std / avg_daily_revenue * 100) if avg_daily_revenue > 0 else 0

        # Revenue change (last 7 days vs previous 7 days)
        if len(daily_revenue) >= 14:
            last_7_days = daily_revenue.tail(7).mean()
            prev_7_days = daily_revenue.iloc[-14:-7].mean()
            revenue_change = ((last_7_days - prev_7_days) / prev_7_days * 100) if prev_7_days > 0 else 0
        else:
            revenue_change = 0

        # Transaction metrics
        total_transactions = len(df[df['status'] == 'success'])
        avg_transaction_value = df[df['status'] == 'success']['amount'].mean() if total_transactions > 0 else 0

        # Repeat customer ratio (simplified - would need customer_id in real implementation)
        repeat_ratio = 0.5  # Default, would be calculated from customer data

        # Cashflow metrics (simplified)
        cashflow_stress = self._calculate_cashflow_stress(df)

        # Calculate health score components
        health_components = self._calculate_health_components(
            revenue_volatility=revenue_volatility,
            revenue_change=revenue_change,
            cashflow_stress=cashflow_stress,
            peer_percentile=peer_data.get('percentile', 60) if peer_data else 60,
            repeat_ratio=repeat_ratio
        )

        # Overall health score (weighted average)
        health_score = (
            health_components['revenue_health'] * 0.25 +
            health_components['stability_health'] * 0.25 +
            health_components['cashflow_health'] * 0.25 +
            health_components['peer_health'] * 0.15 +
            health_components['retention_health'] * 0.10
        )

        # Survival probability (based on health score and trends)
        survival_probability = self._calculate_survival_probability(
            health_score=health_score,
            revenue_change=revenue_change,
            cashflow_stress=cashflow_stress
        )

        # Determine risk level
        if health_score < 50:
            risk_level = "high"
        elif health_score < 70:
            risk_level = "medium"
        else:
            risk_level = "low"

        return {
            "healthScore": round(health_score, 1),
            "survivalProbability": round(survival_probability, 1),
            "riskLevel": risk_level,
            "kpis": {
                "revenue": round(total_revenue, 2),
                "revenueChange": round(revenue_change, 2),
                "volatilityScore": round(min(100, revenue_volatility), 1),
                "cashflowStressIndex": round(cashflow_stress, 1),
                "peerPercentile": peer_data.get('percentile', 60) if peer_data else 60,
                "repeatRatio": repeat_ratio
            },
            "components": health_components
        }

    def _calculate_health_components(
        self,
        revenue_volatility: float,
        revenue_change: float,
        cashflow_stress: float,
        peer_percentile: float,
        repeat_ratio: float
    ) -> Dict[str, float]:
        """Calculate individual health component scores (0-100)"""

        # Revenue health (based on change)
        # Positive growth = high score, negative = low score
        revenue_health = min(100, max(0, 70 + revenue_change * 3))

        # Stability health (lower volatility = higher score)
        stability_health = max(0, 100 - revenue_volatility)

        # Cashflow health (lower stress = higher score)
        cashflow_health = max(0, 100 - cashflow_stress)

        # Peer health (higher percentile = higher score)
        peer_health = peer_percentile

        # Retention health (higher repeat ratio = higher score)
        retention_health = repeat_ratio * 100

        return {
            "revenue_health": revenue_health,
            "stability_health": stability_health,
            "cashflow_health": cashflow_health,
            "peer_health": peer_health,
            "retention_health": retention_health
        }

    def _calculate_survival_probability(
        self,
        health_score: float,
        revenue_change: float,
        cashflow_stress: float
    ) -> float:
        """
        Calculate survival probability based on health metrics
        Returns percentage (0-100)
        """
        # Base survival probability from health score
        base_survival = health_score * 0.9

        # Adjust for revenue trend
        trend_adjustment = min(10, max(-10, revenue_change))

        # Adjust for cashflow stress
        cashflow_adjustment = -cashflow_stress * 0.2

        survival = base_survival + trend_adjustment + cashflow_adjustment
        return min(99, max(10, survival))

    def _calculate_cashflow_stress(self, df: pd.DataFrame) -> float:
        """
        Calculate cashflow stress index (0-100)
        Higher = more stress
        """
        if 'transaction_time' not in df.columns:
            return 50  # Default

        # Simplified: assume outflow is a percentage of inflow
        total_inflow = df[df['status'] == 'success']['amount'].sum()

        # Estimate outflow (in real implementation, this would come from expense data)
        estimated_outflow = total_inflow * 0.85  # Assume 85% goes to expenses

        net_cashflow = total_inflow - estimated_outflow

        # Stress index based on net cashflow margin
        margin = (net_cashflow / total_inflow * 100) if total_inflow > 0 else 0

        # Convert to stress index (lower margin = higher stress)
        stress = max(0, min(100, 70 - margin * 3))

        return stress

    def _empty_health_result(self) -> Dict[str, Any]:
        """Return empty health result for merchants with no data"""
        return {
            "healthScore": 50,
            "survivalProbability": 60,
            "riskLevel": "medium",
            "kpis": {
                "revenue": 0,
                "revenueChange": 0,
                "volatilityScore": 50,
                "cashflowStressIndex": 50,
                "peerPercentile": 50,
                "repeatRatio": 0.5
            }
        }

    def detect_anomalies(
        self,
        transactions: List[Dict[str, Any]],
        contamination: float = 0.05
    ) -> List[Dict[str, Any]]:
        """
        Detect anomalous transactions using Isolation Forest

        Args:
            transactions: List of transaction dictionaries
            contamination: Expected proportion of anomalies (0-1)

        Returns:
            List of transactions with anomaly flags and scores
        """
        if len(transactions) < 10:
            # Not enough data for ML, use rule-based detection
            return self._rule_based_anomaly_detection(transactions)

        df = pd.DataFrame(transactions)

        # Prepare features for anomaly detection
        features = ['amount']
        if 'hour' in df.columns:
            features.append('hour')

        # Extract numeric features
        X = df[features].select_dtypes(include=[np.number]).fillna(0)

        if X.empty or X.shape[0] < 10:
            return self._rule_based_anomaly_detection(transactions)

        # Standardize features
        X_scaled = self.scaler.fit_transform(X)

        # Train Isolation Forest
        model = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100
        )

        # Fit and predict
        predictions = model.fit_predict(X_scaled)
        scores = model.decision_function(X_scaled)

        # Normalize scores to 0-1 (higher = more anomalous)
        normalized_scores = 1 - (scores - scores.min()) / (scores.max() - scores.min() + 1e-10)

        # Add anomaly information to transactions
        results = []
        for i, tx in enumerate(transactions):
            is_anomaly = predictions[i] == -1
            anomaly_score = normalized_scores[i]

            tx_with_anomaly = tx.copy()
            tx_with_anomaly['is_anomaly'] = is_anomaly
            tx_with_anomaly['anomaly_score'] = round(anomaly_score, 3)

            results.append(tx_with_anomaly)

        return results

    def _rule_based_anomaly_detection(
        self,
        transactions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Simple rule-based anomaly detection for small datasets
        """
        if not transactions:
            return []

        amounts = [tx.get('amount', 0) for tx in transactions]
        avg_amount = np.mean(amounts)
        std_amount = np.std(amounts) if len(amounts) > 1 else avg_amount * 0.3

        results = []
        for tx in transactions:
            amount = tx.get('amount', 0)

            # Calculate z-score
            z_score = abs(amount - avg_amount) / std_amount if std_amount > 0 else 0

            is_anomaly = z_score > 2.5
            anomaly_score = min(1, z_score / 4)  # Normalize to 0-1

            tx_with_anomaly = tx.copy()
            tx_with_anomaly['is_anomaly'] = is_anomaly
            tx_with_anomaly['anomaly_score'] = round(anomaly_score, 3)

            results.append(tx_with_anomaly)

        return results

    def forecast_revenue(
        self,
        daily_revenue: List[Dict[str, Any]],
        periods: int = 7
    ) -> List[Dict[str, Any]]:
        """
        Forecast future revenue using simple time-series methods

        Args:
            daily_revenue: List of {date, revenue} dictionaries
            periods: Number of periods to forecast

        Returns:
            List of forecasts with date and predicted revenue
        """
        if not daily_revenue or len(daily_revenue) < 7:
            return []

        # Convert to time series
        df = pd.DataFrame(daily_revenue)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')

        revenues = df['revenue'].values

        # Simple forecasting: weighted moving average + trend
        recent_7_avg = np.mean(revenues[-7:])
        recent_3_avg = np.mean(revenues[-3:])

        # Trend detection
        trend = (recent_3_avg - recent_7_avg) / recent_7_avg if recent_7_avg > 0 else 0

        # Generate forecasts
        forecasts = []
        last_date = df['date'].max()

        for i in range(1, periods + 1):
            forecast_date = last_date + timedelta(days=i)

            # Apply trend (decaying)
            trend_factor = 1 + trend * (1 - i / (periods + 1))
            forecasted_revenue = recent_7_avg * trend_factor

            forecasts.append({
                "date": forecast_date.strftime('%Y-%m-%d'),
                "forecast": round(forecasted_revenue, 2)
            })

        return forecasts

    def calculate_peer_benchmark(
        self,
        merchant_metrics: Dict[str, Any],
        peer_metrics: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate peer benchmarking metrics

        Args:
            merchant_metrics: Current merchant's metrics
            peer_metrics: List of peer merchant metrics

        Returns:
            Benchmark comparison data
        """
        if not peer_metrics:
            return {"percentile": 50, "radarData": [], "comparisonTable": []}

        peer_df = pd.DataFrame(peer_metrics)

        # Calculate percentile for key metrics
        revenue = merchant_metrics.get('revenue', 0)
        percentile = (peer_df['revenue'] < revenue).sum() / len(peer_df) * 100 if len(peer_df) > 0 else 50

        # Radar chart data (normalized 0-100)
        metrics_for_radar = [
            ('Revenue Growth', merchant_metrics.get('revenueChange', 0), 10),
            ('Cash Flow', 100 - merchant_metrics.get('cashflowStressIndex', 50), 100),
            ('Customer Retention', merchant_metrics.get('repeatRatio', 0.5) * 100, 100),
            ('Transaction Volume', merchant_metrics.get('revenue', 0), peer_df['revenue'].max()),
            ('Stability', 100 - merchant_metrics.get('volatilityScore', 50), 100),
            ('Profit Margin', 25, 30),  # Default estimate
        ]

        radar_data = []
        for metric_name, merchant_value, max_value in metrics_for_radar:
            peer_avg = peer_df.select_dtypes(include=[np.number]).mean().mean() if not peer_df.empty else max_value * 0.5
            merchant_normalized = min(100, (merchant_value / max_value * 100) if max_value > 0 else 50)
            peer_normalized = 50  # Assume average peer performance

            radar_data.append({
                "metric": metric_name,
                "merchant": round(merchant_normalized, 1),
                "peers": round(peer_normalized, 1)
            })

        return {
            "percentile": round(percentile, 1),
            "radarData": radar_data
        }

    def simulate_scenario(
        self,
        base_metrics: Dict[str, Any],
        discount_percentage: float = 0,
        cost_reduction: float = 0,
        marketing_boost: float = 0,
        delivery_integration: bool = False
    ) -> Dict[str, Any]:
        """
        Simulate what-if business scenarios

        Args:
            base_metrics: Current merchant metrics
            discount_percentage: Proposed discount percentage
            cost_reduction: Proposed cost reduction percentage
            marketing_boost: Expected marketing-driven volume boost
            delivery_integration: Whether to integrate delivery platforms

        Returns:
            Simulated metrics
        """
        base_revenue = base_metrics.get('kpis', {}).get('revenue', 100000000)
        base_health = base_metrics.get('healthScore', 75)
        base_survival = base_metrics.get('survivalProbability', 82)

        # Calculate impact
        # Discount drives volume but reduces margin
        discount_volume_boost = discount_percentage * 1.2  # Each 1% discount = 1.2% volume
        discount_margin_impact = -discount_percentage * 0.8  # But reduces effective revenue

        # Net revenue impact from discount
        discount_revenue_impact = discount_volume_boost + discount_margin_impact

        # Cost reduction directly improves health
        cost_health_impact = cost_reduction * 1.5

        # Marketing drives top-line growth
        marketing_revenue_impact = marketing_boost * 0.8

        # Delivery integration adds new channel
        delivery_revenue_impact = 15 if delivery_integration else 0

        # Total impacts
        total_revenue_impact = (
            discount_revenue_impact +
            marketing_revenue_impact +
            delivery_revenue_impact
        )

        total_health_impact = (
            cost_health_impact +
            total_revenue_impact * 0.3  # Revenue growth improves health
        )

        total_survival_impact = total_health_impact * 0.8

        # Apply impacts
        forecasted_revenue = base_revenue * (1 + total_revenue_impact / 100)
        updated_health = min(100, base_health + total_health_impact)
        updated_survival = min(100, base_survival + total_survival_impact)

        return {
            "forecastedRevenue": round(forecasted_revenue, 2),
            "updatedHealthScore": round(updated_health, 1),
            "updatedSurvivalProbability": round(updated_survival, 1),
            "impact": {
                "revenue": round(total_revenue_impact, 1),
                "healthScore": round(total_health_impact, 1),
                "survivalProbability": round(total_survival_impact, 1)
            }
        }


# Convenience function
def create_analytics_service() -> AnalyticsService:
    """Create a new AnalyticsService instance"""
    return AnalyticsService()
