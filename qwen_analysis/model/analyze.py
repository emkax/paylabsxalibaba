"""
Paylabs AI Merchant Health & Survival Intelligence System
Powered by Qwen (Alibaba Cloud DashScope)
"""

import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# ──────────────────────────────────────────────
# SYSTEM PROMPT
# ──────────────────────────────────────────────

SYSTEM_PROMPT = """
You are MHSI (Merchant Health & Survival Intelligence), an AI financial analyst embedded inside the Paylabs payment platform.

Your role is to analyze merchant transaction data, detect risk patterns, and provide actionable, evidence-based recommendations to help merchants survive and grow.

## YOUR CAPABILITIES
- Calculate and explain Merchant Health Score (0–100)
- Classify risk level: LOW / MEDIUM / HIGH / CRITICAL
- Estimate 60-day survival probability (%)
- Identify anomalies in revenue, cashflow, and customer behavior
- Benchmark merchant against peer group
- Generate specific, prioritized action plans

## STRICT RULES (ANTI-HALLUCINATION)
1. ONLY make claims that are directly supported by the data provided.
2. If data is missing or insufficient, explicitly say "Insufficient data for this metric."
3. Never fabricate numbers, percentages, or trends not present in the input.
4. Always cite which metric or field drives each conclusion.
5. Probabilities must be derived from actual data patterns, not guesses.
6. If asked something outside your scope, say so clearly.

## MEMORY BEHAVIOR
- You will be given a merchant profile at the start of the session.
- Remember and reference this profile throughout the entire conversation.
- When the user asks follow-up questions, always contextualize your answer using their specific business profile and metrics.
- If the merchant profile is updated, acknowledge the change and adjust your analysis accordingly.

## RESPONSE FORMAT
Always structure your responses using these sections (use only sections relevant to the question):

### 🏥 HEALTH SCORE
[Score /100] — [LOW / MEDIUM / HIGH / CRITICAL risk]
Brief justification based on specific metrics.

### 📊 KEY FINDINGS
- Finding 1 (cite the metric)
- Finding 2 (cite the metric)
- Finding 3 (cite the metric)

### ⚠️ RISK FACTORS
- Risk 1: [description] → [impact]
- Risk 2: [description] → [impact]

### 🎯 RECOMMENDED ACTIONS
Priority 1 — [Action Title]
  What: [specific action]
  Why: [data-backed reason]
  When: [timeframe]
  Expected impact: [realistic outcome]

Priority 2 — ...

### 📈 60-DAY OUTLOOK
Survival Probability: [X%]
Trend: [Improving / Stable / Declining]
Key assumption: [what must happen for this to hold]

### 💬 ANALYST NOTES
[Any caveats, data gaps, or context the merchant should know]

---
Keep language professional but accessible. Avoid jargon without explanation. Be direct — merchants need clarity, not corporate speak.
"""

# ──────────────────────────────────────────────
# CLIENT SETUP
# ──────────────────────────────────────────────

client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
)

# ──────────────────────────────────────────────
# MEMORY / CONVERSATION STATE
# ──────────────────────────────────────────────

class MerchantSession:
    def __init__(self):
        self.merchant_profile: dict = {}
        self.metrics_data: dict = {}
        self.conversation_history: list = []
        self.session_initialized: bool = False

    def initialize(self, merchant_profile: dict, metrics_data: dict):
        """Load merchant profile and metrics into session memory."""
        self.merchant_profile = merchant_profile
        self.metrics_data = metrics_data
        self.session_initialized = True

        # Inject merchant context as first user message + assistant acknowledgment
        context_message = self._build_context_message()
        self.conversation_history = [
            {"role": "user", "content": context_message},
            {
                "role": "assistant",
                "content": (
                    f"Merchant profile loaded. I now have full context on "
                    f"**{merchant_profile.get('business_name', 'your business')}** "
                    f"({merchant_profile.get('category', '')}, {merchant_profile.get('location_city', '')}). "
                    f"I'll reference this data throughout our session. "
                    f"What would you like to analyze?"
                ),
            },
        ]
        print(f"\n✅ Session initialized for: {merchant_profile.get('business_name')}")
        print(f"   Category : {merchant_profile.get('category')} — {merchant_profile.get('sub_category')}")
        print(f"   Location : {merchant_profile.get('location_city')}")
        print(f"   Peer Rank: Top {100 - metrics_data.get('peer_comparison', {}).get('peer_percentile_rank', 0)}%\n")

    def _build_context_message(self) -> str:
        return f"""
Please load and remember the following merchant profile and performance data for this entire session.

## MERCHANT PROFILE
{json.dumps(self.merchant_profile, indent=2)}

## PERFORMANCE METRICS & PEER COMPARISON
{json.dumps(self.metrics_data, indent=2)}

Acknowledge that you have loaded this data and are ready to analyze.
""".strip()

    def chat(self, user_message: str) -> str:
        """Send a message and get a response, maintaining conversation history."""
        if not self.session_initialized:
            return "⚠️ No merchant data loaded. Please call session.initialize() first."

        self.conversation_history.append({"role": "user", "content": user_message})

        response = client.chat.completions.create(
            model="qwen-plus",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}]
            + self.conversation_history,
            temperature=0.3,   # lower = more grounded, less hallucination
            max_tokens=2000,
        )

        assistant_reply = response.choices[0].message.content
        self.conversation_history.append(
            {"role": "assistant", "content": assistant_reply}
        )
        return assistant_reply

    def reset_conversation(self):
        """Keep merchant memory but clear conversation thread."""
        if self.session_initialized:
            context_message = self._build_context_message()
            self.conversation_history = [
                {"role": "user", "content": context_message},
                {
                    "role": "assistant",
                    "content": "Conversation reset. Merchant profile is still loaded. How can I help?",
                },
            ]
        print("🔄 Conversation reset. Merchant profile retained.")

    def update_metrics(self, new_metrics: dict):
        """Update metrics mid-session (e.g. after new transaction data)."""
        self.metrics_data.update(new_metrics)
        update_msg = f"Merchant metrics have been updated:\n{json.dumps(new_metrics, indent=2)}\nPlease factor in these changes going forward."
        self.conversation_history.append({"role": "user", "content": update_msg})
        response = client.chat.completions.create(
            model="qwen-plus",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}]
            + self.conversation_history,
            temperature=0.3,
            max_tokens=500,
        )
        ack = response.choices[0].message.content
        self.conversation_history.append({"role": "assistant", "content": ack})
        print(f"📥 Metrics updated. AI acknowledged:\n{ack}\n")


# ──────────────────────────────────────────────
# HELPER: LOAD JSON DATA
# ──────────────────────────────────────────────

def load_merchant_data(json_path: str) -> tuple[dict, dict]:
    """
    Load merchant data from a JSON file.
    Returns (merchant_profile, performance_metrics_and_peers).
    """
    with open(json_path, "r") as f:
        data = json.load(f)

    profile = data.get("merchant_profile", {})
    metrics = {
        "performance_metrics": data.get("performance_metrics", {}),
        "peer_comparison": data.get("peer_comparison", {}),
    }
    return profile, metrics


# ──────────────────────────────────────────────
# INTERACTIVE CLI
# ──────────────────────────────────────────────

def run_interactive_cli(json_path: str):
    print("\n" + "=" * 60)
    print("  Paylabs AI Merchant Health & Survival Intelligence")
    print("=" * 60)

    profile, metrics = load_merchant_data(json_path)

    session = MerchantSession()
    session.initialize(profile, metrics)

    print("Commands: 'reset' | 'quit' | or type any question\n")

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

        print("\nAI Analyst: ", end="", flush=True)
        reply = session.chat(user_input)
        print(reply)
        print()


# ──────────────────────────────────────────────
# EXAMPLE: PROGRAMMATIC USAGE
# ──────────────────────────────────────────────

def run_demo(json_path: str):
    """Run a preset demo analysis."""
    profile, metrics = load_merchant_data(json_path)

    session = MerchantSession()
    session.initialize(profile, metrics)

    demo_questions = [
        "Give me a full health assessment of this merchant.",
        "What are the top 3 risks I should watch for in the next 60 days?",
        "Based on what top peers are doing, what strategies should I adopt?",
        "What is my survival probability and what can improve it?",
    ]

    for q in demo_questions:
        print(f"\n{'─'*60}")
        print(f"📌 {q}")
        print(f"{'─'*60}")
        reply = session.chat(q)
        print(reply)


# ──────────────────────────────────────────────
# ENTRY POINT
# ──────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    json_path = sys.argv[1] if len(sys.argv) > 1 else "high_growth.json"
    mode = sys.argv[2] if len(sys.argv) > 2 else "interactive"

    if mode == "demo":
        run_demo(json_path)
    else:
        run_interactive_cli(json_path)