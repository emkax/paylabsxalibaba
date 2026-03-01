"""
Alibaba Cloud AI Service Integration

This module provides integration with Alibaba Cloud's Qwen (Tongyi Qianwen) API
for generating natural language insights and recommendations for merchants.
"""
import os
import json
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

# Try to import dashscope (Alibaba Cloud Qwen SDK)
try:
    import dashscope
    from dashscope import Generation
    DASHSCOPE_AVAILABLE = True
except ImportError:
    DASHSCOPE_AVAILABLE = False


class QwenAIService:
    """
    Service for interacting with Alibaba Cloud Qwen AI API
    """

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
        self.model = os.getenv("QWEN_MODEL", "qwen-max")

        if DASHSCOPE_AVAILABLE and self.api_key:
            dashscope.api_key = self.api_key
        else:
            print("Warning: Dashscope not configured. AI features will use fallback responses.")

    def generate_merchant_insights(
        self,
        merchant_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate natural language insights for a merchant based on their data

        Args:
            merchant_data: Dictionary containing merchant metrics including:
                - health_score, survival_probability, revenue, etc.
                - daily_revenue, transaction_frequency
                - cashflow data, peer comparison

        Returns:
            Dictionary with insights, root causes, and recommendations
        """
        # Create prompt for Qwen
        prompt = self._build_analysis_prompt(merchant_data)

        if DASHSCOPE_AVAILABLE and self.api_key:
            try:
                response = Generation.call(
                    model=self.model,
                    prompt=prompt,
                    temperature=0.7,
                    max_tokens=1000
                )

                if response.status_code == 200:
                    return self._parse_ai_response(response.output.text)
                else:
                    print(f"Qwen API error: {response.code} - {response.message}")
            except Exception as e:
                print(f"Qwen API exception: {str(e)}")

        # Fallback to rule-based insights
        return self._generate_fallback_insights(merchant_data)

    def _build_analysis_prompt(self, data: Dict[str, Any]) -> str:
        """Build a structured prompt for Qwen analysis"""

        health_score = data.get('healthScore', 75)
        survival_prob = data.get('survivalProbability', 80)
        kpis = data.get('kpis', {})

        revenue = kpis.get('revenue', 0)
        revenue_change = kpis.get('revenueChange', 0)
        volatility = kpis.get('volatilityScore', 30)
        cashflow_stress = kpis.get('cashflowStressIndex', 40)
        peer_percentile = kpis.get('peerPercentile', 60)
        repeat_ratio = kpis.get('repeatRatio', 0.5)

        daily_revenue = data.get('dailyRevenue', [])
        cashflow = data.get('cashflow', {})

        prompt = f"""
Analyze this merchant's financial health data and provide actionable insights:

FINANCIAL METRICS:
- Health Score: {health_score}/100
- Survival Probability: {survival_prob}%
- Monthly Revenue: IDR {revenue:,.0f}
- Revenue Change: {revenue_change:+.1f}%
- Revenue Volatility: {volatility}/100 (lower is better)
- Cashflow Stress Index: {cashflow_stress}/100 (lower is better)
- Peer Percentile: {peer_percentile}% (vs similar merchants)
- Customer Repeat Ratio: {repeat_ratio:.1%}

CASHFLOW STATUS:
- Negative Days Streak: {cashflow.get('negativeStreak', 0)} days
- Liquidity Runway: {cashflow.get('liquidityRunway', 90)} days

TASK:
1. Identify the top 2-3 root causes of any financial stress
2. Provide 3 immediate actionable recommendations (can be implemented within 1 week)
3. Provide 2-3 strategic recommendations (longer-term initiatives)
4. Estimate the potential impact if recommendations are implemented

Format your response as valid JSON with this structure:
{{
    "rootCauses": [
        {{"title": "...", "description": "...", "severity": "high|medium|low"}}
    ],
    "immediateActions": [
        {{"title": "...", "description": "...", "expectedImpact": "...", "priority": "high|medium|low"}}
    ],
    "strategicActions": [
        {{"title": "...", "description": "...", "expectedImpact": "...", "priority": "high|medium|low"}}
    ],
    "expectedImpact": {{
        "revenue": <percentage increase>,
        "healthScore": <point increase>
    }}
}}
"""
        return prompt

    def _parse_ai_response(self, response_text: str) -> Dict[str, Any]:
        """Parse JSON response from Qwen"""
        try:
            # Extract JSON from response (handle markdown code blocks)
            if "```json" in response_text:
                json_str = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                json_str = response_text.split("```")[1].split("```")[0]
            else:
                json_str = response_text

            parsed = json.loads(json_str.strip())

            # Transform to expected format
            return {
                "rootCauses": [
                    {
                        "title": cause.get("title", ""),
                        "description": cause.get("description", ""),
                        "severity": cause.get("severity", "medium")
                    }
                    for cause in parsed.get("rootCauses", [])
                ],
                "immediateActions": [
                    {
                        "id": str(i + 1),
                        "title": action.get("title", ""),
                        "description": action.get("description", ""),
                        "expectedImpact": action.get("expectedImpact", ""),
                        "status": "pending",
                        "priority": action.get("priority", "medium")
                    }
                    for i, action in enumerate(parsed.get("immediateActions", []))
                ],
                "strategicActions": [
                    {
                        "id": str(i + 1),
                        "title": action.get("title", ""),
                        "description": action.get("description", ""),
                        "expectedImpact": action.get("expectedImpact", ""),
                        "status": "pending",
                        "priority": action.get("priority", "medium")
                    }
                    for i, action in enumerate(parsed.get("strategicActions", []))
                ],
                "expectedImpact": parsed.get("expectedImpact", {
                    "revenue": 15,
                    "healthScore": 8
                })
            }

        except json.JSONDecodeError as e:
            print(f"Failed to parse AI response: {e}")
            return self._generate_fallback_insights({})

    def _generate_fallback_insights(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate rule-based insights when AI is unavailable
        This ensures the dashboard always has recommendations
        """
        health_score = data.get('healthScore', 75)
        kpis = data.get('kpis', {})
        revenue_change = kpis.get('revenueChange', 0)
        volatility = kpis.get('volatilityScore', 30)
        cashflow_stress = kpis.get('cashflowStressIndex', 40)
        peer_percentile = kpis.get('peerPercentile', 60)

        root_causes = []
        immediate_actions = []
        strategic_actions = []

        # Analyze health score
        if health_score < 70:
            root_causes.append({
                "title": "Low Overall Health Score",
                "description": f"Your health score of {health_score} indicates significant financial stress that needs attention.",
                "severity": "high"
            })
            immediate_actions.append({
                "id": "1",
                "title": "Conduct Financial Review",
                "description": "Review all revenue streams and expenses to identify immediate cost-cutting opportunities.",
                "expectedImpact": "+5 health score",
                "status": "pending",
                "priority": "high"
            })

        # Analyze revenue trend
        if revenue_change < -5:
            root_causes.append({
                "title": "Declining Revenue",
                "description": f"Revenue has decreased by {abs(revenue_change):.1f}% compared to the previous period.",
                "severity": "high"
            })
            immediate_actions.append({
                "id": "2",
                "title": "Launch Revenue Recovery Campaign",
                "description": "Implement targeted promotions to re-engage dormant customers and boost sales.",
                "expectedImpact": "+10% revenue",
                "status": "pending",
                "priority": "high"
            })
        elif revenue_change < 0:
            root_causes.append({
                "title": "Slight Revenue Dip",
                "description": f"Revenue decreased by {abs(revenue_change):.1f}%. Monitor closely for trends.",
                "severity": "medium"
            })

        # Analyze volatility
        if volatility > 50:
            root_causes.append({
                "title": "High Revenue Volatility",
                "description": "Significant day-to-day revenue fluctuations make financial planning difficult.",
                "severity": "medium"
            })
            immediate_actions.append({
                "id": "3",
                "title": "Stabilize Revenue Streams",
                "description": "Introduce subscription options or recurring payment plans to smooth revenue.",
                "expectedImpact": "-20% volatility",
                "status": "pending",
                "priority": "medium"
            })

        # Analyze cashflow
        if cashflow_stress > 50:
            root_causes.append({
                "title": "Cash Flow Pressure",
                "description": "High cashflow stress index indicates potential liquidity challenges.",
                "severity": "high"
            })
            immediate_actions.append({
                "id": "4",
                "title": "Improve Cash Collection",
                "description": "Accelerate receivables collection and negotiate extended payment terms with suppliers.",
                "expectedImpact": "+15 days runway",
                "status": "pending",
                "priority": "high"
            })

        # Analyze peer performance
        if peer_percentile < 50:
            root_causes.append({
                "title": "Below-Average Peer Performance",
                "description": f"Your performance ranks in the {peer_percentile}th percentile compared to similar merchants.",
                "severity": "medium"
            })
            strategic_actions.append({
                "id": "5",
                "title": "Competitive Analysis",
                "description": "Study top-performing peers to identify best practices and growth opportunities.",
                "expectedImpact": "+10 percentile ranking",
                "status": "pending",
                "priority": "medium"
            })

        # Add strategic actions if healthy
        if health_score >= 80 and revenue_change > 5:
            strategic_actions.append({
                "id": "6",
                "title": "Scale Successful Operations",
                "description": "Consider expanding product lines or entering new markets while momentum is strong.",
                "expectedImpact": "+20% revenue growth",
                "status": "pending",
                "priority": "medium"
            })
            strategic_actions.append({
                "id": "7",
                "title": "Build Cash Reserves",
                "description": "Strengthen financial position by building 6+ months of operating reserves.",
                "expectedImpact": "Improved financial resilience",
                "status": "pending",
                "priority": "low"
            })

        # Default recommendations if none generated
        if not root_causes:
            root_causes.append({
                "title": "Maintain Current Performance",
                "description": "Your metrics are healthy. Focus on sustaining momentum and preparing for growth.",
                "severity": "low"
            })

        if not immediate_actions:
            immediate_actions = [
                {
                    "id": "1",
                    "title": "Monitor Key Metrics",
                    "description": "Continue tracking health score and revenue trends weekly.",
                    "expectedImpact": "Early issue detection",
                    "status": "pending",
                    "priority": "medium"
                },
                {
                    "id": "2",
                    "title": "Optimize Payment Experience",
                    "description": "Review payment success rates and minimize friction in checkout.",
                    "expectedImpact": "+5% conversion",
                    "status": "pending",
                    "priority": "medium"
                }
            ]

        if not strategic_actions:
            strategic_actions = [
                {
                    "id": "3",
                    "title": "Expand Product Offerings",
                    "description": "Add complementary products to increase average order value.",
                    "expectedImpact": "+15% AOV",
                    "status": "pending",
                    "priority": "medium"
                },
                {
                    "id": "4",
                    "title": "Implement Loyalty Program",
                    "description": "Launch rewards program to increase customer retention.",
                    "expectedImpact": "+20% repeat purchases",
                    "status": "pending",
                    "priority": "low"
                }
            ]

        return {
            "rootCauses": root_causes,
            "immediateActions": immediate_actions,
            "strategicActions": strategic_actions,
            "expectedImpact": {
                "revenue": 15,
                "healthScore": 8
            }
        }

    def analyze_transaction_anomaly(
        self,
        transaction: Dict[str, Any],
        historical_pattern: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze a transaction for potential anomalies

        Args:
            transaction: Current transaction data
            historical_pattern: Historical transaction patterns

        Returns:
            Anomaly analysis with score and explanation
        """
        # Simple rule-based anomaly detection
        # (In production, this would use PAI - Platform of AI)

        amount = transaction.get('amount', 0)
        avg_amount = historical_pattern.get('avg_amount', amount)
        std_amount = historical_pattern.get('std_amount', amount * 0.3)

        hour = transaction.get('hour', 12)
        typical_hours = historical_pattern.get('typical_hours', [9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20])

        anomaly_score = 0
        reasons = []

        # Check amount anomaly
        if std_amount > 0:
            z_score = abs(amount - avg_amount) / std_amount
            if z_score > 3:
                anomaly_score += 0.5
                reasons.append(f"Unusually {'high' if amount > avg_amount else 'low'} transaction amount")

        # Check time anomaly
        if hour not in typical_hours:
            anomaly_score += 0.2
            reasons.append("Transaction at unusual hour")

        return {
            "is_anomaly": anomaly_score > 0.5,
            "anomaly_score": round(anomaly_score, 2),
            "reasons": reasons
        }


# Convenience function
def create_qwen_service() -> QwenAIService:
    """Create a new Qwen AI service instance"""
    return QwenAIService()
