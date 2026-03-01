"""
Paylabs AI Merchant Health & Survival Intelligence System
Powered by Qwen (Alibaba Cloud DashScope)
"""

import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path
from extract_performance_metric import calculate_performance_metrics

BASE_DIR = Path(__file__).parent

load_dotenv()

BASE_SYSTEM_PROMPT = """
You are MHSI (Merchant Health & Survival Intelligence), an AI financial analyst embedded inside the Paylabs payment platform.

Your role is to analyze merchant transaction data, detect risk patterns, and provide actionable, evidence-based recommendations.

## STRICT RULES (ANTI-HALLUCINATION)
1. ONLY make claims directly supported by the data provided.
2. If data is missing, explicitly say "Insufficient data for this metric."
3. Never fabricate numbers, percentages, or trends not in the input.
4. Always cite which metric or field drives each conclusion.
5. Probabilities must be derived from actual data patterns, not guesses.
6. If asked something outside your scope, say so clearly.

## MEMORY BEHAVIOR
- You have been given merchant data at session start.
- Always contextualize answers using the specific merchant's data.
- If merchant_profile was not provided, skip profile references and rely only on metrics.
- If metrics are updated mid-session, acknowledge and adjust analysis accordingly.

## COMMAND MODES

### When the user sends exactly "ACTION":
Respond ONLY with a valid JSON object. No markdown. No explanation. Pure JSON only.
{
  "action_plan": {
    "generated_for": "<business_name or 'Unknown'>",
    "based_on": {
      "revenue_change_30d_percent": <value>,
      "cashflow_stress_index": <value>,
      "peer_percentile_rank": <value>
    },
    "immediate": {
      "timeframe": "0-7 days",
      "message": "<one concise paragraph on what to do now and why, grounded in data>",
      "actions": [
        {"priority": 1, "action": "<specific action>", "reason": "<data-backed reason>", "expected_impact": "<realistic outcome>"},
        {"priority": 2, "action": "<specific action>", "reason": "<data-backed reason>", "expected_impact": "<realistic outcome>"},
        {"priority": 3, "action": "<specific action>", "reason": "<data-backed reason>", "expected_impact": "<realistic outcome>"}
      ]
    },
    "strategic_30_days": {
      "timeframe": "8-30 days",
      "message": "<one concise paragraph on medium-term strategy grounded in peer data>",
      "actions": [
        {"priority": 1, "action": "<specific action>", "reason": "<data-backed reason>", "expected_impact": "<realistic outcome>"},
        {"priority": 2, "action": "<specific action>", "reason": "<data-backed reason>", "expected_impact": "<realistic outcome>"}
      ]
    },
    "strategic_90_days": {
      "timeframe": "31-90 days",
      "message": "<one concise paragraph on long-term growth trajectory>",
      "actions": [
        {"priority": 1, "action": "<specific action>", "reason": "<data-backed reason>", "expected_impact": "<realistic outcome>"},
        {"priority": 2, "action": "<specific action>", "reason": "<data-backed reason>", "expected_impact": "<realistic outcome>"}
      ]
    }
  }
}

### When the user sends exactly "OVERVIEW":
Respond ONLY with a valid JSON object. No markdown. No explanation. Pure JSON only.
{
  "overview": {
    "merchant_profile": {
      "merchant_id": "<value or null>",
      "business_name": "<value or null>",
      "category": "<value or null>",
      "sub_category": "<value or null>",
      "location_city": "<value or null>",
      "business_age_months": <value or null>,
      "avg_price_range": "<value or null>",
      "operational_hours": "<value or null>",
      "online_offline_type": "<value or null>",
      "employee_count": <value or null>
    },
    "health_score": <integer 0-100>,
    "health_score_label": "<LOW RISK / MEDIUM RISK / HIGH RISK / CRITICAL>",
    "health_score_reasoning": "<2-3 sentences citing specific metrics that drove this score>",
    "survival_probability_60d": <integer 0-100>,
    "survival_trend": "<Improving / Stable / Declining>",
    "survival_reasoning": "<1-2 sentences explaining the trend>",
    "key_metrics": {
      "current_month_revenue": <value>,
      "revenue_change_30d_percent": <value>,
      "avg_ticket_size": <value>,
      "ticket_size_change_percent": <value>,
      "transaction_frequency_change_percent": <value>,
      "cashflow_stress_index": <value>,
      "customer_repeat_ratio": <value>,
      "revenue_volatility_score": <value>
    },
    "peer_comparison": {
      "peer_group_size": <value>,
      "peer_avg_growth_rate": <value>,
      "peer_avg_ticket_size": <value>,
      "peer_avg_volatility": <value>,
      "peer_percentile_rank": <value>,
      "merchant_vs_peer_growth": "<e.g. +15.4% above peer avg>",
      "merchant_vs_peer_ticket": "<e.g. +Rp 9,000 above peer avg>",
      "peer_top_performing_strategies": ["<strategy1>", "<strategy2>", "<strategy3>"],
      "peer_common_failure_pattern": ["<pattern1>", "<pattern2>"]
    },
    "top_risks": [
      {"risk": "<risk description>", "impact": "<potential impact>"},
      {"risk": "<risk description>", "impact": "<potential impact>"},
      {"risk": "<risk description>", "impact": "<potential impact>"}
    ]
  }
}

### For all other messages:
Respond in structured markdown with only the relevant sections:
### 🏥 HEALTH SCORE
### 📊 KEY FINDINGS
### ⚠️ RISK FACTORS
### 🎯 RECOMMENDED ACTIONS
### 📈 60-DAY OUTLOOK
### 💬 ANALYST NOTES

Keep language professional but accessible. Be direct and data-grounded.
"""

client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
)


class MerchantSession:
    def __init__(self):
        self.merchant_profile: dict = {}
        self.metrics_data: dict = {}
        self.conversation_history: list = []
        self.session_initialized: bool = False

    def initialize(self, merchant_profile: dict = None, metrics_data: dict = None):
        self.merchant_profile = merchant_profile or {}
        self.metrics_data = metrics_data or {}
        self.session_initialized = True

        self.conversation_history = [
            {"role": "user", "content": self._build_context_message()},
            {"role": "assistant", "content": self._build_ack_message()},
        ]

        biz_name = self.merchant_profile.get("business_name", "(no profile provided)")
        peer_rank = self.metrics_data.get("peer_comparison", {}).get("peer_percentile_rank", "N/A")

        print(f"\n{'='*60}")
        print(f"  Session initialized")
        print(f"  Merchant  : {biz_name}")
        if self.merchant_profile:
            print(f"  Category  : {self.merchant_profile.get('category')} - {self.merchant_profile.get('sub_category')}")
            print(f"  Location  : {self.merchant_profile.get('location_city')}")
        print(f"  Peer Rank : {peer_rank}th percentile")
        print(f"{'='*60}\n")

    def _build_context_message(self) -> str:
        parts = ["Please load and remember the following data for this entire session.\n"]

        if self.merchant_profile:
            parts.append("## MERCHANT PROFILE")
            parts.append(json.dumps(self.merchant_profile, indent=2))
        else:
            parts.append("## MERCHANT PROFILE")
            parts.append(
                "(No merchant profile provided. "
                "For OVERVIEW, return null for all merchant_profile fields. "
                "Do not invent profile data.)"
            )

        if self.metrics_data:
            parts.append("\n## PERFORMANCE METRICS & PEER COMPARISON")
            parts.append(json.dumps(self.metrics_data, indent=2))

        parts.append("\nAcknowledge you have loaded this data and are ready to analyze.")
        return "\n".join(parts)

    def _build_ack_message(self) -> str:
        if self.merchant_profile:
            biz = self.merchant_profile.get("business_name", "your business")
            return (
                f"Data loaded. Full context on {biz} "
                f"({self.merchant_profile.get('category', '')}, "
                f"{self.merchant_profile.get('location_city', '')}) is ready. "
                f"Use ACTION, OVERVIEW, or ask any question."
            )
        return (
            "Performance metrics and peer comparison data loaded. "
            "No merchant profile provided - I will reference metrics only. "
            "Use ACTION, OVERVIEW, or ask any question."
        )

    def chat(self, user_message: str):
        if not self.session_initialized:
            return "No data loaded. Please call session.initialize() first."

        self.conversation_history.append({"role": "user", "content": user_message})

        response = client.chat.completions.create(
            model="qwen-plus",
            messages=[{"role": "system", "content": BASE_SYSTEM_PROMPT}]
            + self.conversation_history,
            temperature=0.2,
            max_tokens=2500,
        )

        raw_reply = response.choices[0].message.content
        self.conversation_history.append({"role": "assistant", "content": raw_reply})

        cmd = user_message.strip().upper()
        if cmd in ("ACTION", "OVERVIEW"):
            try:
                clean = raw_reply.strip()
                if clean.startswith("```"):
                    lines = clean.split("\n")
                    clean = "\n".join(lines[1:])
                    clean = clean.rsplit("```", 1)[0]
                return json.loads(clean.strip())
            except json.JSONDecodeError:
                return raw_reply

        return raw_reply

    def reset_conversation(self):
        if self.session_initialized:
            self.conversation_history = [
                {"role": "user", "content": self._build_context_message()},
                {"role": "assistant", "content": "Conversation reset. Merchant data still loaded. How can I help?"},
            ]
        print("Conversation reset. Merchant data retained.\n")

    def update_metrics(self, new_metrics: dict):
        self.metrics_data.update(new_metrics)
        update_msg = (
            f"Merchant metrics have been updated:\n"
            f"{json.dumps(new_metrics, indent=2)}\n"
            f"Please factor in these changes going forward."
        )
        self.conversation_history.append({"role": "user", "content": update_msg})
        response = client.chat.completions.create(
            model="qwen-plus",
            messages=[{"role": "system", "content": BASE_SYSTEM_PROMPT}]
            + self.conversation_history,
            temperature=0.2,
            max_tokens=500,
        )
        ack = response.choices[0].message.content
        self.conversation_history.append({"role": "assistant", "content": ack})
        print(f"Metrics updated.\n{ack}\n")

    def load_session(self, filepath="session_memory.json"):
        if not os.path.exists(filepath):
            return False

        try:
            with open(filepath, "r") as f:
                data = json.load(f)
        except (json.JSONDecodeError, ValueError):
            print("Session file corrupted or empty. Starting fresh.")
            return False

        self.merchant_profile = data.get("merchant_profile", {})
        self.metrics_data = data.get("metrics_data", {})
        self.conversation_history = data.get("conversation_history", [])
        self.session_initialized = True
        return True

    def save_session(self, filepath="session_memory.json"):
        data = {
            "merchant_profile": self.merchant_profile,
            "metrics_data": self.metrics_data,
            "conversation_history": self.conversation_history
        }
        with open(filepath, "w") as f:
            json.dump(data, f)


def load_merchant_data(json_path: str) -> tuple:
    with open(json_path, "r") as f:
        data = json.load(f)
    profile = data.get("merchant_profile") or None
    metrics = {
        "performance_metrics": data.get("performance_metrics", {}),
        "peer_comparison": data.get("peer_comparison", {}),
    }
    return profile, metrics


def run_interactive_cli(json_path: str):
    print("\n" + "=" * 60)
    print("  Paylabs AI Merchant Health & Survival Intelligence")
    print("=" * 60)

    session = MerchantSession()

    # Try to load saved session
    if not session.load_session():
        # If no saved session exists, load fresh data
        profile, metrics = load_merchant_data(json_path)
        session.initialize(merchant_profile=profile, metrics_data=metrics)

    print("Commands: ACTION | OVERVIEW | reset | quit | or ask anything\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nSession ended.")
            break

        if not user_input:
            continue
        if user_input.lower() == "quit":
            print("Goodbye.")
            break
        if user_input.lower() == "reset":
            session.reset_conversation()
            continue
        if user_input.lower() == "update":

            continue

        reply = session.chat(user_input)
        session.save_session()

        print("\nAI Analyst:")
        if isinstance(reply, dict):
            print(json.dumps(reply, indent=2))
        else:
            print(reply)
        print()

        



def run_demo(json_path: str):
    profile, metrics = load_merchant_data(json_path)
    session = MerchantSession()
    session.initialize(merchant_profile=profile, metrics_data=metrics)

    questions = [
        "OVERVIEW",
        "ACTION",
        "What are the top 3 risks I should watch in the next 60 days?",
    ]

    for q in questions:
        print(f"\n{'─'*60}")
        print(f">>> {q}")
        print(f"{'─'*60}")
        reply = session.chat(q)
        if isinstance(reply, dict):
            print(json.dumps(reply, indent=2))
        else:
            print(reply)


if __name__ == "__main__":
    import sys

    json_path = sys.argv[1] if len(sys.argv) > 1 else "./case1.json"
    mode = sys.argv[2] if len(sys.argv) > 2 else "interactive"

    if mode == "demo":
        run_demo(BASE_DIR / json_path)
    else:
        run_interactive_cli(BASE_DIR / json_path)